from typing import Dict, List


class PHIType:
    PERSON_NAME = "person_name"
    PERSON_NAME_ABBREV = "person_name_abbrev"
    DATE = "date"
    TIME = "time"
    PHONE_NUMBER = "phone_number"
    ADDRESS = "address"
    PATIENT_ID = "patient_id"
    Z_NUMBER = "z_number"
    LOCATION = "location"
    DOCUMENT_ID = "document_id"
    DOCUMENT_SUB_ID = "document_sub_id"
    PHI_NUMBER = "phi_number"
    AGE = "age"
    HOSPITAL_NAME = "hospital_name"
    ACCREDITATION_NUMBER = "accreditation_number"
    STUDY_NAME = "study_name"


# "Smart" regex patterns per PHI type
DEFAULT_PATTERNS: Dict[str, List[str]] = {
    # <PERSOON>, <PERSON_NAME>, <NAAM>, <NAME>
    PHIType.PERSON_NAME: [
        r"<(?:PERSOON|PERSON_NAME|NAAM|NAME)>",
    ],
    # <DATE>, <DATUM>
    PHIType.DATE: [
        r"<(?:DATE|DATUM)>",
    ],
    # <TIME>, <TIJD>
    PHIType.TIME: [
        r"<(?:TIME|TIJD)>",
    ],
    # <PHONE>, <PHONENUMBER>, <TELEFOON>, <TELEFOONNUMMER>
    PHIType.PHONE_NUMBER: [
        r"<(?:PHONE|PHONENUMBER|TELEFOON|TELEFOONNUMMER)>",
    ],
    # <ADRES>, <ADDRESS>
    PHIType.ADDRESS: [
        r"<(?:ADRES|ADDRESS)>",
    ],
    # <PATIENT_ID>, <PATIENTID>, <PATIENTNUMMER>
    PHIType.PATIENT_ID: [
        r"<PATIENT(?:_ID|ID|NUMMER)>",
    ],
    # <Z_NUMMER>, <Z_NUMBER>, <ZNUMMER>, <ZNUMBER>, <Z-NUMMER>, <Z-NUMBER>
    # Z, optional - or _, then NUMMER or NUMBER
    PHIType.Z_NUMBER: [
        r"<Z[-_]?(?:NUMMER|NUMBER)>",
    ],
    # <LOCATIE>, <LOCATION>, <PLAATS>, <PLACE>
    PHIType.LOCATION: [
        r"<(?:LOCATIE|LOCATION|PLAATS|PLACE)>",
    ],
    # <DOCUMENT_ID>, <DOCUMENTID>, <RAPPORT_ID>, <RAPPORTID>
    # DOCUMENT or RAPPORT, optional - or _, then ID
    PHIType.DOCUMENT_ID: [
        r"<(?:DOCUMENT|RAPPORT)[-_]?ID>",
    ],
    # <RAPPORT[_-]ID.(T|R|C|DPA|RPA)[_-]NUMMER>
    # Keep the capturing group so generators can use the subtype.
    PHIType.DOCUMENT_SUB_ID: [
        r"<RAPPORT[_-]ID\.(T|R|C|DPA|RPA)[_-]NUMMER>",
    ],
    # <PHI_NUMMER>, <PHI_NUMBER>, <PHINUMMER>, <PHINUMBER>, <PHI-NUMMER>, <PHI-NUMBER>
    # PHI, optional - or _, then NUMMER or NUMBER
    PHIType.PHI_NUMBER: [
        r"<PHI[-_]?(?:NUMMER|NUMBER)>",
    ],
    # <LEEFTIJD>, <AGE>
    PHIType.AGE: [
        r"<(?:LEEFTIJD|AGE)>",
    ],
    # <PERSON_INITIALS>, <PERSOONAFKORTING>
    PHIType.PERSON_NAME_ABBREV: [
        r"<(?:PERSON_INITIALS|PERSOONAFKORTING)>",
    ],
    # <HOSPITAL_NAME>, <ZIEKENHUIS>, <HOSPITAL>
    PHIType.HOSPITAL_NAME: [
        r"<(?:HOSPITAL_NAME|ZIEKENHUIS|HOSPITAL)>",
    ],
    # <ACCREDITATION_NUMBER>, <ACCREDITATIE_NUMMER>
    PHIType.ACCREDITATION_NUMBER: [
        r"<(?:ACCREDITATION_NUMBER|ACCREDITATIE_NUMMER|ACCREDATIE[-_]?NUMMER)>",
    ],
    # <STUDY_NAME>, <STUDYNAME>, <STUDY-NAME>,
    # <STUDIENAAM>, <STUDIE_NAAM>, <STUDIE-NAAM>
    PHIType.STUDY_NAME: [
        r"<(?:STUDY[-_]?NAME|STUDIE[-_]?NAAM)>",
    ],
}
