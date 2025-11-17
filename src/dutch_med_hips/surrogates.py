"""
Default surrogate generators for PHI types, using Faker.

All generators take a `re.Match` object and return a surrogate string.
"""

import math
import random
import re
from typing import Callable, Dict, List, Tuple

from faker import Faker

from .constants import PHIType
from .defaults import (
    AGE_GMM_MEANS,
    AGE_GMM_VARS,
    AGE_GMM_WEIGHTS,
    AGE_MAX,
    AGE_MIN,
    DATE_MONTH_AS_NAME_PROB,
    DATE_MONTH_NAME_ABBR_PROB,
    DATE_NUMERIC_PADDED_PROB,
    DATE_WITH_YEAR_PROB,
    PERSON_NAME_FIRST_ONLY_PROB,
    PERSON_NAME_INITIALS_PROB,
    PERSON_NAME_LAST_ONLY_PROB,
    PERSON_NAME_LOWERCASE_PROB,
    PERSON_NAME_MAX_INITIALS,
    PERSON_NAME_REVERSE_ORDER_PROB,
    PERSON_NAME_UPPERCASE_PROB,
    TIME_ADD_HOUR,
    TIME_FMT_HH_DOT_MM_PROB,
    TIME_FMT_HH_MM_PROB,
    TIME_FMT_HH_U_MM_PROB,
    TIME_FMT_NATURAL_DUTCH_PROB,
)

_DUTCH_MONTHS_FULL = [
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]

_DUTCH_MONTHS_ABBR = [
    "jan",
    "feb",
    "mrt",
    "apr",
    "mei",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
]

_DUTCH_HOUR_WORDS = [
    "twaalf",
    "één",
    "twee",
    "drie",
    "vier",
    "vijf",
    "zes",
    "zeven",
    "acht",
    "negen",
    "tien",
    "elf",
]


# Single Faker instance for the whole module (Dutch locale)
_fake = Faker("nl_NL")

# -- Seeder ------------------------------------------------------


def seed_surrogates(seed: int) -> None:
    """
    Seed the Faker instance used by the surrogate generators.
    """
    _fake.seed_instance(seed)


# --- Helper functions ---------------------------------------


def _choose_weighted_index(weights: List[float]) -> int:
    """
    Return an index 0..len(weights)-1 chosen according to the given weights.
    """
    total = sum(weights)
    if total <= 0:
        # fallback: uniform
        return random.randrange(len(weights))

    r = random.random() * total
    acc = 0.0
    for i, w in enumerate(weights):
        acc += w
        if r <= acc:
            return i
    return len(weights) - 1


def _chance(p: float) -> bool:
    return random.random() < p


# --- People ------------------------------------------------------


def _first_name_to_initials(first_name: str, extra_count: int) -> str:
    """
    Convert a first name into a compact initials string.

    - First initial always based on the given first_name.
    - extra_count additional initials are based on extra random first names.
    - Example outputs: "J.", "J.S.", "J.S.T."
    """
    initials = []

    first_name = first_name.strip()
    if first_name:
        initials.append(first_name[0].upper() + ".")

    for _ in range(extra_count):
        extra = _fake.first_name().strip()
        if extra:
            initials.append(extra[0].upper() + ".")

    # Join without spaces so you get "J.S.T." as a single token
    return "".join(initials)


def generate_fake_person_name(match: re.Match) -> str:
    """
    Generate a fake person name with:
    - First / last / full name variants
    - Initials only allowed when a last name is present (never lone initial)
    - Multi-initials (J., J.S., J.S.T.) using up to PERSON_NAME_MAX_INITIALS
    - Random capitalization
    - Optional 'Lastname, First' format
    """
    first = _fake.first_name()
    last = _fake.last_name()

    # Decide basic structure: first-only, last-only, or full
    r = random.random()
    if r < PERSON_NAME_FIRST_ONLY_PROB:
        structure = "first_only"
    elif r < PERSON_NAME_FIRST_ONLY_PROB + PERSON_NAME_LAST_ONLY_PROB:
        structure = "last_only"
    else:
        structure = "full"

    # Decide whether to use initials.
    # RULE 1: never a lone initial -> only allow initials when a last name is present.
    use_initials = structure == "full" and random.random() < PERSON_NAME_INITIALS_PROB

    if use_initials:
        # Decide how many initials (1..PERSON_NAME_MAX_INITIALS)
        max_n = max(1, PERSON_NAME_MAX_INITIALS)
        extra_count = random.randint(0, max_n - 1)  # 0 extra -> 1 initial total
        first_part = _first_name_to_initials(first, extra_count)
    else:
        first_part = first

    # Build the parts according to the structure
    if structure == "first_only":
        parts = [first_part]
    elif structure == "last_only":
        parts = [last]
    else:  # "full"
        parts = [first_part, last]

    # Maybe reverse order as "Lastname, First"
    if len(parts) == 2 and random.random() < PERSON_NAME_REVERSE_ORDER_PROB:
        parts = [parts[1] + ",", parts[0]]

    name = " ".join(parts)

    # Apply capitalization style
    c = random.random()
    if c < PERSON_NAME_LOWERCASE_PROB:
        name = name.lower()
    elif c < PERSON_NAME_LOWERCASE_PROB + PERSON_NAME_UPPERCASE_PROB:
        name = name.upper()
    else:
        # Keep as-is (Faker returns Title Case by default,
        # initials are already uppercase)
        pass

    return name


def generate_fake_person_initials(match: re.Match) -> str:
    """Generate fake initials like 'A.B.'."""
    # Faker doesn't have initials directly, so we improvise.
    initials = [
        _fake.random_uppercase_letter(),
        _fake.random_uppercase_letter(),
    ]
    return ".".join(initials) + "."


# --- Dates / times / age -----------------------------------------


def generate_fake_date(match: re.Match) -> str:
    """
    Generate a fake date using a 3-step scheme:

    1) pick with or without year
    2) pick month representation: name vs numeric
    3) pick exact format:
       - numeric: D-M or DD-MM (± year), never mixed padding
       - name: full vs abbreviated month (± year)
    """
    # Use a date in roughly the last 5 years
    d = _fake.date_between(start_date="-5y", end_date="today")
    year = d.year
    month = d.month
    day = d.day

    # Step 1: with or without year
    with_year = _chance(DATE_WITH_YEAR_PROB)

    # Step 2: month as name or number
    month_as_name = _chance(DATE_MONTH_AS_NAME_PROB)

    if month_as_name:
        # Named month
        use_abbr = _chance(DATE_MONTH_NAME_ABBR_PROB)
        month_str = (
            _DUTCH_MONTHS_ABBR[month - 1] if use_abbr else _DUTCH_MONTHS_FULL[month - 1]
        )
        # Always non-padded day here
        if with_year:
            # "3 februari 2025" / "3 feb 2025"
            return f"{day} {month_str} {year:04d}"
        else:
            # "3 februari" / "3 feb"
            return f"{day} {month_str}"
    else:
        # Numeric month: either D-M or DD-MM (both parts same style)
        padded = _chance(DATE_NUMERIC_PADDED_PROB)
        if padded:
            day_str = f"{day:02d}"
            month_str = f"{month:02d}"
        else:
            day_str = str(day)
            month_str = str(month)

        if with_year:
            # "03-02-2025" or "3-2-2025"
            return f"{day_str}-{month_str}-{year:04d}"
        else:
            # "03-02" or "3-2"
            return f"{day_str}-{month_str}"


def _natural_dutch_time() -> str:
    """
    Generate a simple natural-language Dutch time phrase, e.g.:
    - "kwart voor zes"
    - "kwart over drie"
    - "half vier"
    """
    # Use 1–11 as base hour; we'll map 0 -> "twaalf"
    base_hour = random.randint(0, 11)  # 0..11 -> 12,1,..11
    hour_word = _DUTCH_HOUR_WORDS[base_hour]

    # "half vier" in Dutch means 3:30 (halfway to 4), so we need next hour word too
    next_hour_word = _DUTCH_HOUR_WORDS[(base_hour + 1) % 12]

    kind = random.choice(["kwart_voor", "kwart_over", "half", "uur"])

    if kind == "kwart_voor":
        return f"kwart voor {next_hour_word}"
    elif kind == "kwart_over":
        return f"kwart over {hour_word}"
    elif kind == "half":
        return f"half {next_hour_word}"
    else:  # "uur"
        return f"{hour_word} uur"


def generate_fake_time(match: re.Match) -> str:
    """
    Generate a fake time in Dutch style.

    Formats:
    - "13:45"
    - "13:45 uur"
    - "13.45"
    - "13u45"
    - natural Dutch ("kwart voor zes", "half vier", ...)
    """
    # Base numeric time
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)

    idx = _choose_weighted_index(
        [
            TIME_FMT_HH_MM_PROB,
            TIME_FMT_HH_DOT_MM_PROB,
            TIME_FMT_HH_U_MM_PROB,
            TIME_FMT_NATURAL_DUTCH_PROB,
        ]
    )

    add_hour = _chance(TIME_ADD_HOUR)
    if add_hour:
        uur = " uur"
    else:
        uur = ""

    if idx == 0:
        return f"{hour:02d}:{minute:02d}{uur}"
    elif idx == 1:
        return f"{hour:02d}.{minute:02d}{uur}"
    elif idx == 2:
        # Belgian/Dutch style "12u23"
        return f"{hour}u{minute:02d}"
    else:
        # Natural phrase like "kwart voor zes"
        return _natural_dutch_time()


def generate_fake_age(match: re.Match) -> str:
    """
    Generate a fake age (years) using a 1D Gaussian Mixture Model defined in
    AGE_GMM_MEANS, AGE_GMM_VARS, AGE_GMM_WEIGHTS.

    We:
    - choose a component according to AGE_GMM_WEIGHTS
    - sample from N(mean, var) for that component
    - enforce integer age, truncated to [AGE_MIN, AGE_MAX]
      via simple rejection (with a fallback clamp)
    """
    if not (AGE_GMM_MEANS and AGE_GMM_VARS and AGE_GMM_WEIGHTS):
        # Fallback if misconfigured
        return str(random.randint(AGE_MIN, AGE_MAX))

    # Choose mixture component
    k = _choose_weighted_index(AGE_GMM_WEIGHTS)

    mean = AGE_GMM_MEANS[k]
    var = AGE_GMM_VARS[k]
    sigma = math.sqrt(var) if var > 0 else 1.0

    # Rejection sampling to stay within [AGE_MIN, AGE_MAX]
    for _ in range(10):
        sample = random.gauss(mean, sigma)
        age = int(round(sample))
        if AGE_MIN <= age <= AGE_MAX:
            return str(age)

    # Fallback: clamp a final sample
    sample = random.gauss(mean, sigma)
    age = int(round(sample))
    age = max(AGE_MIN, min(AGE_MAX, age))
    return str(age)


# --- Contact / location ------------------------------------------


def generate_fake_phone(match: re.Match) -> str:
    """Generate a fake phone number (locale-aware for nl_NL)."""
    return _fake.phone_number()


def generate_fake_address(match: re.Match) -> str:
    """Generate a fake address (single-line)."""
    # Faker's address includes newlines; we normalize to a single line.
    addr = _fake.address().replace("\n", ", ")
    return addr


def generate_fake_location(match: re.Match) -> str:
    """Generate a fake city/location name."""
    return _fake.city()


# --- IDs / numbers -----------------------------------------------


def generate_fake_patient_id(match: re.Match) -> str:
    """Generate a fake patient identifier."""
    # PAT-123456
    return _fake.bothify(text="PAT-######")


def generate_fake_z_number(match: re.Match) -> str:
    """Generate a fake Z-number."""
    # Z-1234567
    return _fake.bothify(text="Z-#######")


def generate_fake_document_id(match: re.Match) -> str:
    """Generate a fake document/rapport ID."""
    # DOC-123456
    return _fake.bothify(text="DOC-######")


def generate_fake_document_sub_id(match: re.Match) -> str:
    """
    Generate a fake rapport sub-ID, preserving the subtype T/R/C/DPA/RPA.

    Pattern: <RAPPORT[_-]ID\.(T|R|C|DPA|RPA)[_-]NUMMER>
    group(1) is the subtype.
    """
    subtype = match.group(1) if match.lastindex and match.lastindex >= 1 else "X"
    # e.g. RAPPORT-T-NUMMER-1234
    number_part = _fake.random_int(min=1000, max=9999)
    return f"RAPPORT-{subtype}-NUMMER-{number_part}"


def generate_fake_phi_number(match: re.Match) -> str:
    """Generate a generic fake PHI number."""
    # PHI-123456
    return _fake.bothify(text="PHI-######")


def generate_fake_accreditation_number(match: re.Match) -> str:
    """Generate a fake accreditation number."""
    # ACC-123456
    return _fake.bothify(text="ACC-######")


# --- Other text fields -------------------------------------------


def generate_fake_hospital_name(match: re.Match) -> str:
    """Generate a fake hospital name."""
    # Use a company name and append something hospital-ish.
    base = _fake.company()
    suffixes = [" Ziekenhuis", " Medisch Centrum", " Kliniek"]
    return base + _fake.random_element(suffixes)


def generate_fake_study_name(match: re.Match) -> str:
    """Generate a fake study / trial name."""
    # STUDY-ABC-123
    prefix = _fake.random_element(["STUDY", "TRIAL", "PROJECT"])
    code = _fake.bothify(text="???-###").upper()
    return f"{prefix}-{code}"


# --- Mapping from PHI type -> generator --------------------------


DEFAULT_GENERATORS: Dict[str, Callable[[re.Match], str]] = {
    PHIType.PERSON_NAME: generate_fake_person_name,
    PHIType.PERSON_NAME_ABBREV: generate_fake_person_initials,
    PHIType.DATE: generate_fake_date,
    PHIType.TIME: generate_fake_time,
    PHIType.PHONE_NUMBER: generate_fake_phone,
    PHIType.ADDRESS: generate_fake_address,
    PHIType.PATIENT_ID: generate_fake_patient_id,
    PHIType.Z_NUMBER: generate_fake_z_number,
    PHIType.LOCATION: generate_fake_location,
    PHIType.DOCUMENT_ID: generate_fake_document_id,
    PHIType.DOCUMENT_SUB_ID: generate_fake_document_sub_id,
    PHIType.PHI_NUMBER: generate_fake_phi_number,
    PHIType.AGE: generate_fake_age,
    PHIType.HOSPITAL_NAME: generate_fake_hospital_name,
    PHIType.ACCREDITATION_NUMBER: generate_fake_accreditation_number,
    PHIType.STUDY_NAME: generate_fake_study_name,
}
