# src/dutch_med_hips/surrogates.py

"""
Default surrogate generators for PHI types.

All generators take a `re.Match` object and return a surrogate string.
"""

import random
import re
from typing import Callable, Dict

from .constants import PHIType

# --- People ------------------------------------------------------


def generate_fake_person_name(match: re.Match) -> str:
    """Generate a fake Dutch-ish person name."""
    first_names = ["Alice", "Bob", "Carol", "David", "Eva", "Frank"]
    last_names = ["Janssen", "De Vries", "Bakker", "Visser", "Smit", "Mulder"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_fake_person_initials(match: re.Match) -> str:
    """Generate fake initials like 'A.B.'."""
    letters = [chr(random.randint(ord("A"), ord("Z"))) for _ in range(2)]
    return ".".join(letters) + "."


# --- Dates / times / numbers -------------------------------------


def generate_fake_date(match: re.Match) -> str:
    """Generate a simple fake date in YYYY-MM-DD."""
    years = [2019, 2020, 2021, 2022, 2023]
    months = list(range(1, 13))
    days = list(range(1, 28))
    return f"{random.choice(years):04d}-{random.choice(months):02d}-{random.choice(days):02d}"


def generate_fake_time(match: re.Match) -> str:
    """Generate a simple fake time in HH:MM."""
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"


def generate_fake_age(match: re.Match) -> str:
    """Generate a fake age (bounded to something reasonable)."""
    return str(random.randint(0, 100))


# --- Contact / location ------------------------------------------


def generate_fake_phone(match: re.Match) -> str:
    """Generate a fake Dutch mobile phone number."""
    return f"+31-6-{random.randint(10000000, 99999999)}"


def generate_fake_address(match: re.Match) -> str:
    """Generate a simple fake address."""
    streets = ["Hoofdstraat", "Kerklaan", "Dorpsstraat", "Stationsweg"]
    numbers = random.randint(1, 200)
    cities = ["Amsterdam", "Rotterdam", "Utrecht", "Den Haag"]
    return f"{random.choice(streets)} {numbers}, {random.choice(cities)}"


def generate_fake_location(match: re.Match) -> str:
    """Generate a fake city/location name."""
    locations = ["Amsterdam", "Rotterdam", "Utrecht", "Groningen", "Maastricht"]
    return random.choice(locations)


# --- IDs / numbers -----------------------------------------------


def generate_fake_patient_id(match: re.Match) -> str:
    """Generate a fake patient identifier."""
    return f"PAT-{random.randint(100000, 999999)}"


def generate_fake_z_number(match: re.Match) -> str:
    """Generate a fake Z-number."""
    return f"Z-{random.randint(1000000, 9999999)}"


def generate_fake_document_id(match: re.Match) -> str:
    """Generate a fake document/rapport ID."""
    return f"DOC-{random.randint(100000, 999999)}"


def generate_fake_document_sub_id(match: re.Match) -> str:
    """
    Generate a fake rapport sub-ID, preserving the subtype T/R/C/DPA/RPA.

    Pattern: <RAPPORT[_-]ID\.(T|R|C|DPA|RPA)[_-]NUMMER>
    group(1) is the subtype.
    """
    subtype = match.group(1) if match.lastindex and match.lastindex >= 1 else "X"
    return f"RAPPORT-{subtype}-NUMMER-{random.randint(1000, 9999)}"


def generate_fake_phi_number(match: re.Match) -> str:
    """Generate a generic fake PHI number."""
    return f"PHI-{random.randint(100000, 999999)}"


def generate_fake_accreditation_number(match: re.Match) -> str:
    """Generate a fake accreditation number."""
    return f"ACC-{random.randint(100000, 999999)}"


# --- Other text fields -------------------------------------------


def generate_fake_hospital_name(match: re.Match) -> str:
    """Generate a fake hospital name."""
    names = [
        "St. Antonius Ziekenhuis",
        "Academisch Medisch Centrum",
        "Rijnland Kliniek",
        "Noorderlicht Ziekenhuis",
    ]
    return random.choice(names)


def generate_fake_study_name(match: re.Match) -> str:
    """Generate a fake study / trial name."""
    prefixes = ["STUDY", "TRIAL", "PROJECT"]
    suffix = random.randint(100, 999)
    return f"{random.choice(prefixes)}-{suffix}"


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
