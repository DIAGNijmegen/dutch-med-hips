# 🇳🇱 dutch-med-hips

A robust, highly configurable **PHI anonymization and surrogate generation** toolkit designed for **Dutch medical and radiology reports**.  
It replaces PHI tokens (e.g. `<PERSOON>`, `<Z-NUMMER>`, `<DATUM>`) with realistic surrogate values such as names, ages, dates, hospitals, study names, IDs, BSNs, IBANs, phone numbers, URLs, emails, and more.

`dutch-med-hips` uses:

- **Faker** for Dutch-language surrogate generation  
- **Configurable templates** for ID-like fields  
- **Locale dictionaries** for hospitals, months, cities, study names  
- **A combined regex engine** for fast and safe substitution  
- **Document-level deterministic seeding** (optional)

---

## Features

### 🔐 PHI Surrogates

Supports realistic surrogates for:

- Person names (with initials, Dutch tussenvoegsels, formats, etc.)
- Hospital names & abbreviations (based on full Dutch hospital list)
- Cities & locations (sometimes used instead of hospital names)
- Study names (medical trials, oncology studies, MRI protocols, etc.)
- Dates (Dutch formats: `12 februari`, `12-02`, `4 mei`, etc.)
- Times (`12:34`, `12u34`, textual like _“kwart voor zes”_)
- Ages (Gaussian mixture model to mimic real hospital distributions)
- Phone numbers (mobile, landlines, **SEIN** pager numbers)
- Patient IDs, Z-numbers, PHI numbers, document IDs (template-driven)
- BSN & IBAN (valid structure, via Faker)
- URLs
- Email addresses

### 🔧 Flexible Configuration

All defaults live in `settings.py` and can be overridden at runtime:

```python
from dutch_med_hips import settings

settings.ID_TEMPLATES_BY_TAG["<Z-NUMMER>"] = "Z-###-###"
settings.PERSON_NAME_REUSE_PROB = 0.15
settings.ENABLE_TYPOS = True
```

### 🧪 Deterministic Output

Provide a seed or allow the system to hash the document to stabilize output:

```python
hips = HideInPlainSight(seed=123)
```

### ✏️ Optional Typo Injection

Using the `typo` Python package, some surrogates can receive:

- Adjacent-key typos
- Insertions
- Deletions  
You can enable/disable this globally.

### ⚠️ Automatic Disclaimer Header

Every anonymized document can automatically receive an anonymization disclaimer at the top.  
You may customize or disable it.

---

## Installation

```bash
pip install dutch-med-hips
```

(or your local workflow)

---

## Quickstart

```python
from dutch_med_hips import HideInPlainSight

text = """
Patiënt <PERSOON> werd opgenomen in <HOSPITAL_NAME> op <DATUM>.
Z-nummer: <Z-NUMMER>, BSN: <BSN>, Email: <EMAIL>.
Rapport ID: <RAPPORT_ID.T_NUMMER>.
""" 

hips = HideInPlainSight(seed=42)
result = hips.run(text)

print(result["text"])
print(result["mapping"])  # Shows original -> surrogate mapping
```

---

## Customizing ID Formats

All ID formats are driven by simple templates:

| Symbol | Meaning |
|--------|---------|
| `#` | digit 0–9 |
| `A` | uppercase letter |
| `a` | lowercase letter |
| `X` | letter or digit |

Example:

```python
settings.ID_TEMPLATES_BY_TAG["<PATIENT_ID>"] = "PT-######"
settings.ID_TEMPLATES_BY_TAG["<Z-NUMMER>"] = "Z-###-###"
```

---

## Hospital & Location Logic

Hospital data lives in `locale.py` as lists of variants:

```python
HOSPITAL_NAME_POOL = [
    ["Amsterdam UMC locatie AMC", "AUMC-AMC", "AMC"],
    ["Radboud UMC", "Radboudumc", "RUMC"],
    ["LUMC"],
    ...
]

HOSPITAL_CITY_POOL = [
    ["Amsterdam", "Adam", "A'dam"],
    ["Nijmegen"],
    ["Leiden"],
    ...
]
```

The surrogate system sometimes picks the **city** rather than the **hospital name**, mirroring real report style.

---

## Study Name Surrogates

Also in `locale.py`, a curated list of Dutch/medical trials:

```python
STUDY_NAME_POOL = [
    "LEMA",
    "Donan",
    ["M-SPECT", "mSPECT"],
    ["Alpe d'Huzes MRI", "Alpe"],
    "TULIP",
    "PRIAS",
    ...
]
```

---

## Extending / Overriding Configuration

Users can override ANY default value:

```python
from dutch_med_hips import settings

settings.STUDY_NAME_POOL.append("NEWSTUDY")
settings.ENABLE_HEADER = False
settings.PHONE_TYPE_SEIN_PROB = 0.20
```

---

## Mapping Output Structure

`result = hips.run(text)` returns:

```python
{
    "text": "anonymized text...",
    "mapping": [
        {
            "original": "<PERSOON>",
            "surrogate": "Jan Steen",
            "phi_type": "person_name",
            "start": 10,
            "end": 18
        },
        ...
    ]
}
```

---
