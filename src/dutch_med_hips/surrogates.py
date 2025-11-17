"""
Default surrogate generators for PHI types, using Faker.

All generators take a `re.Match` object and return a surrogate string.
"""

import random
import re
from typing import Callable, Dict

from faker import Faker

from .constants import PHIType
from .defaults import (
    PERSON_NAME_FIRST_ONLY_PROB,
    PERSON_NAME_INITIALS_PROB,
    PERSON_NAME_LAST_ONLY_PROB,
    PERSON_NAME_LOWERCASE_PROB,
    PERSON_NAME_MAX_INITIALS,
    PERSON_NAME_REVERSE_ORDER_PROB,
    PERSON_NAME_UPPERCASE_PROB,
)

# Single Faker instance for the whole module (Dutch locale)
_fake = Faker("nl_NL")


def seed_surrogates(seed: int) -> None:
    """
    Seed the Faker instance used by the surrogate generators.
    """
    _fake.seed_instance(seed)


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
    """Generate a fake date in ISO format (YYYY-MM-DD)."""
    # date() already returns an ISO date string.
    return _fake.date()


def generate_fake_time(match: re.Match) -> str:
    """Generate a fake time in HH:MM format."""
    return _fake.time(pattern="%H:%M")


def generate_fake_age(match: re.Match) -> str:
    """Generate a fake age."""
    return str(_fake.random_int(min=0, max=100))


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
