"""
Core functionality for hiding PHI in plain sight.

Key public pieces:
- PatternConfig: dataclass for regex-based PHI patterns.
- build_pattern_configs: helper that merges defaults and user overrides,
  with a duplicate-pattern check.
- HideInPlainSight: main anonymizer class.
"""

import random
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .constants import DEFAULT_PATTERNS, PHIType
from .surrogates import DEFAULT_GENERATORS


@dataclass
class PatternConfig:
    """
    Configuration for a PHI detection pattern.

    Attributes
    ----------
    phi_type:
        Logical PHI category (e.g. PHIType.PERSON_NAME).
    pattern:
        Regex string that matches the thing to be replaced, for example
        r"<PERSOON>" or r"<RAPPORT[_-]ID\.(T|R|C|DPA|RPA)[_-]NUMMER>".
    generator:
        Function that, given the regex match, returns a surrogate string.
        Signature: Callable[[re.Match], str]
    max_per_document:
        Optional cap on the number of replacements for this PHI type per
        document. If None, no limit.
    """

    phi_type: str
    pattern: str
    generator: Callable[[re.Match], str]
    max_per_document: Optional[int] = None


def build_pattern_configs(
    custom_patterns_per_type: Optional[Dict[str, List[str]]] = None,
    max_per_document: Optional[Dict[str, int]] = None,
) -> List[PatternConfig]:
    """
    Build PatternConfig objects starting from DEFAULT_PATTERNS,
    optionally overridden by the user.

    Parameters
    ----------
    custom_patterns_per_type:
        Optional dict mapping phi_type -> list of regex patterns.
        If provided for a phi_type, this *replaces* the default patterns
        for that phi_type.

        Example:
            {
                PHIType.PERSON_NAME: [r"<NAAM>", r"<NAME>"],
                PHIType.DATE: [r"<D>", r"<DATE>"],
            }

    max_per_document:
        Optional dict mapping phi_type -> max replacements per document.

    Returns
    -------
    List[PatternConfig]

    Raises
    ------
    ValueError
        If the same *pattern string* is assigned to more than one PHI type.
    KeyError
        If a PHI type has no default generator in DEFAULT_GENERATORS.
    """
    # 1) Merge defaults + custom overrides.
    final_patterns_per_type: Dict[str, List[str]] = {}

    for phi_type, default_patterns in DEFAULT_PATTERNS.items():
        if custom_patterns_per_type and phi_type in custom_patterns_per_type:
            # Use user-specified patterns, de-duplicated but order-preserving.
            patterns = list(dict.fromkeys(custom_patterns_per_type[phi_type]))
        else:
            patterns = list(dict.fromkeys(default_patterns))

        final_patterns_per_type[phi_type] = patterns

    # 2) Check for duplicate pattern strings across PHI types.
    seen: Dict[str, str] = {}
    conflicts: List[str] = []

    for phi_type, patterns in final_patterns_per_type.items():
        for pattern in patterns:
            if pattern in seen and seen[pattern] != phi_type:
                conflicts.append(
                    f"Pattern {pattern!r} used for both "
                    f"{seen[pattern]!r} and {phi_type!r}"
                )
            else:
                seen[pattern] = phi_type

    if conflicts:
        raise ValueError(
            "Duplicate regex pattern strings across PHI categories are not allowed:\n"
            + "\n".join(conflicts)
        )

    # 3) Build PatternConfig list.
    configs: List[PatternConfig] = []
    for phi_type, patterns in final_patterns_per_type.items():
        if phi_type not in DEFAULT_GENERATORS:
            raise KeyError(
                f"No default surrogate generator registered for PHI type {phi_type!r}"
            )

        generator = DEFAULT_GENERATORS[phi_type]
        max_doc = max_per_document.get(phi_type) if max_per_document else None

        for pattern in patterns:
            configs.append(
                PatternConfig(
                    phi_type=phi_type,
                    pattern=pattern,
                    generator=generator,
                    max_per_document=max_doc,
                )
            )

    return configs


class HideInPlainSight:
    """
    Main engine that replaces regex-based PHI patterns with surrogates.

    Usage
    -----
    from dutch_med_hips import HideInPlainSight, build_pattern_configs, PHIType

    configs = build_pattern_configs()
    hips = HideInPlainSight(configs, seed=42)

    result = hips.anonymize("Patiënt <PERSOON> kwam op <DATE> en <RAPPORT_ID> ...")
    print(result["text"])
    print(result["mapping"])
    """

    def __init__(
        self,
        pattern_configs: Optional[List[PatternConfig]] = None,
        *,
        seed: Optional[int] = None,
        custom_patterns_per_type: Optional[Dict[str, List[str]]] = None,
        max_per_document: Optional[Dict[str, int]] = None,
    ):
        if pattern_configs is None:
            pattern_configs = build_pattern_configs(
                custom_patterns_per_type=custom_patterns_per_type,
                max_per_document=max_per_document,
            )
        self._pattern_configs = pattern_configs

        # Defensive: ensure no identical pattern string is used for different PHI types.
        pattern_owner: Dict[str, str] = {}
        for cfg in pattern_configs:
            owner = pattern_owner.get(cfg.pattern)
            if owner is not None and owner != cfg.phi_type:
                raise ValueError(
                    f"Pattern {cfg.pattern!r} defined for multiple PHI types: "
                    f"{owner!r} and {cfg.phi_type!r}"
                )
            pattern_owner[cfg.pattern] = cfg.phi_type

        # Build a combined regex with named groups so we know which config matched.
        group_parts: List[str] = []
        self._group_to_config: Dict[str, PatternConfig] = {}

        for idx, cfg in enumerate(pattern_configs):
            group_name = f"p{idx}"
            group_parts.append(f"(?P<{group_name}>{cfg.pattern})")
            self._group_to_config[group_name] = cfg

        if group_parts:
            combined_src = "|".join(group_parts)
            self._combined_pattern = re.compile(combined_src)
        else:
            self._combined_pattern = None

        if seed is not None:
            random.seed(seed)

    def run(
        self,
        text: str,
        keep_mapping: bool = True,
    ) -> Dict[str, object]:
        """
        Replace all configured patterns in `text` with generated surrogates.

        Parameters
        ----------
        text:
            Input text containing PHI tags/patterns.
        keep_mapping:
            If True, returns a list of replacements with metadata.

        Returns
        -------
        dict with keys:
            - "text": anonymized text
            - "mapping": list of replacement records (or None if keep_mapping=False)
        """
        if self._combined_pattern is None:
            return {"text": text, "mapping": [] if keep_mapping else None}

        per_type_counts: Dict[str, int] = {}
        mapping: List[Dict[str, object]] = []

        def _replacement(match: re.Match) -> str:
            group_name = match.lastgroup
            cfg = self._group_to_config[group_name]
            phi_type = cfg.phi_type

            count = per_type_counts.get(phi_type, 0)
            if cfg.max_per_document is not None and count >= cfg.max_per_document:
                # Limit reached: leave original text unchanged.
                return match.group(0)

            surrogate = cfg.generator(match)
            per_type_counts[phi_type] = count + 1

            if keep_mapping:
                mapping.append(
                    {
                        "phi_type": phi_type,
                        "pattern": cfg.pattern,
                        "original": match.group(0),
                        "surrogate": surrogate,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

            return surrogate

        anonymized_text = self._combined_pattern.sub(_replacement, text)

        return {
            "text": anonymized_text,
            "mapping": mapping if keep_mapping else None,
        }
