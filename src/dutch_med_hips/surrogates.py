"""
Default surrogate generators for PHI types, using Faker.

All generators take a `re.Match` object and return a surrogate string.
"""

import re
from typing import Callable, Dict

from faker import Faker

from .constants import PHIType

# Single Faker instance for the whole module (Dutch locale)
_fake = Faker("nl_NL")


def seed_surrogates(seed: int) -> None:
    """
    Seed the Faker instance used by the surrogate generators.
    """
    _fake.seed_instance(seed)


# --- People ------------------------------------------------------


def generate_fake_person_name(match: re.Match) -> str:
    """Generate a fake (Dutch) person name."""
    return _fake.name()


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
