# 🇳🇱 dutch-med-hips

A robust, highly configurable **PHI anonymization and surrogate generation** toolkit designed for **Dutch medical and radiology reports**.  
It replaces PHI tokens (e.g. `<PERSOON>`, `<Z-NUMMER>`, `<DATUM>`) with realistic surrogate values such as names, ages, dates, hospitals, study names, IDs, BSNs, IBANs, phone numbers, URLs, emails, and more.

`dutch-med-hips` uses:

- [**Faker**](https://faker.readthedocs.io/en/master/) for Dutch-language surrogate generation  
- **Configurable templates** for ID-like fields  
- **Locale dictionaries** for hospitals, months, cities, study names  
- **A combined regex engine** for fast and safe substitution  
- **Document-level deterministic seeding** (optional)

---

## Installation

```bash
pip install dutch-med-hips
```

---

## Quickstart

### Python API

```python
from dutch_med_hips import HideInPlainSight

text = """
Patiënt <PERSOON> werd opgenomen in <HOSPITAL_NAME> op <DATUM>.
Z-nummer: <Z-NUMMER>, BSN: <BSN>, Email: <EMAIL>.
Rapport ID: <RAPPORT_ID.T_NUMMER>.
""" 

hips = HideInPlainSight()
result = hips.run(text)

print(result["text"])
print(result["mapping"])  # Shows original -> surrogate mapping
```

### Command-Line Interface

```bash
dutch-med-hips [OPTIONS]
```

#### Common Options

| Option | Meaning |
|--------|---------|
| `-i, --input PATH` | Input file (UTF-8). Use `-` or omit to read from **stdin**. |
| `-o, --output PATH` | Output file (UTF-8). Use `-` or omit to write to **stdout**. |
| `--mapping-out PATH` | Write the JSON mapping (original → surrogate) to a file. |
| `--seed N` | Use a fixed seed for deterministic surrogate generation. |
| `--no-document-hash-seed` | Disable automatic seeding based on the document hash. |
| `--no-header` | Disable the anonymization disclaimer header. |
| `--disable-typos` | Disable random typo injection in surrogates. |
| `-V, --version` | Show version information and exit. |

---

## Features

### 🔐 PHI Surrogates

#### 👤 People & Demographics

- **Person names**
  - Dutch-style names (first/last), tussenvoegsels (`van`, `de`, …)
  - Variants: first-only, last-only, full, initials (`J. Jansen`, `J.S. Jansen`)
  - Randomized casing (`jan jansen`, `JAN JANSEN`, `Jansen, Jan`)
- **Person initials**
  - Derived from full fake names: `Jan Steen` → `JS`, `Vincent van Gogh` → `VvG`
- **Age**
  - Sampled from a hospital-like Gaussian mixture model (more 40–85 year olds)

#### 🧾 Identifiers & Numbers

- **Patient IDs / Z-numbers / generic PHI numbers**
  - All driven by simple templates per tag (e.g. `<Z-NUMMER>` → `Z######`)
  - Template mini-language (`#` = digit, etc.)
- **Document IDs & sub-IDs**
  - Main report IDs from templates
  - Sub-IDs like `<RAPPORT_ID.T_NUMMER>` → `T123456`
- **BSN**
  - Dutch BSN-like numbers via Faker `ssn()`
- **IBAN**
  - Dutch IBANs via Faker, compact or grouped (`NL91ABNA0417164300`, `NL91 ABNA 0417 1643 00`)
- **Accreditation number**
  - Always `M` + 3 digits (e.g. `M007`, `M123`)

#### 🏥 Hospitals, Locations & Studies

- **Hospital names**
  - Realistic Dutch hospital pool with full names and abbreviations  
    e.g. `Amsterdam UMC locatie AMC`, `AMC`, `Radboudumc`, `LUMC`, `ADRZ`
  - Sometimes uses only the city as shorthand (e.g. `Amsterdam`, `Nijmegen`)
- **Locations**
  - Dutch cities and place names drawn from hospital/location data
- **Study names**
  - Curated list of real-looking study labels and variants  
    e.g. `LEMA`, `Donan`, `M-SPECT`/`mSPECT`, `Alpe d'Huzes MRI`, `TULIP`, `PRIAS`

#### 📅 Dates & Times

- **Dates**
  - Dutch-style formats:
    - Numeric: `D-M`, `DD-MM`, with/without year (`03-02-2025`, `3-2-12`)
    - Named months: `3 februari`, `3 feb 2025`
  - Mix of year/no-year, numeric vs month-name
  - Start/end date range configuration (e.g. last 10 years)
- **Times**
  - 24h clock formats: `13:45`, `13:45 uur`, `13.45`, `13u45`
  - Natural Dutch phrases: `kwart voor zes`, `kwart over drie`, `half vier`

#### 📞 Contact & Online

- **Phone numbers**
  - Dutch mobile numbers (`06-12345678`, `+31 6 12345678`)
  - Landlines / hospital numbers (`020-5669111`, `088-…`)
  - Internal SEIN/pager numbers (4–5 digit codes)
- **Email addresses**
  - Fake but valid emails via Faker (customizable domains)
- **URLs**
  - Fake but valid http(s) URLs via Faker (can be styled to look like portals/EPD endpoints)

#### 🏠 Addresses & Misc

- **Addresses**
  - Dutch-style street + number + postcode + city via Faker (`nl_NL`)
- **Other PHI**
  - Any additional tag-based IDs or tokens configured via templates can be mapped to surrogates in the same way.

### 🔧 Flexible Configuration

All defaults live in `settings.py` and can be overridden at runtime:

```python
from dutch_med_hips import settings

settings.ID_TEMPLATES_BY_TAG["<Z-NUMMER>"] = "Z-###-###"
settings.PERSON_NAME_REUSE_PROB = 0.15
settings.ENABLE_TYPOS = True
```

### 🧪 Deterministic Output

The system automatically hashes the document to generate a seed to stabilize output. This can be turned off, or you can provide your own fixed seed:

```python
hips = HideInPlainSight(seed=123)
```

!!! Note
    Using a fixed seed means the **same input document** will always yield the **same output document** and **same surrogate mappings**.  
    Different documents will still produce different outputs.

### ✏️ Optional Typo Injection

Using the [`typo`](https://github.com/ranvijaykumar/typo) Python package, some surrogates can receive:

- Adjacent-key typos
- Insertions
- Deletions  
You can enable/disable this globally.

### ⚠️ Automatic Disclaimer Header

Every anonymized document can automatically receive an anonymization disclaimer at the top.  
You may customize or disable it.

---

## Customizing ID Formats

All ID formats are driven by simple templates:

| Symbol | Meaning |
|--------|---------|
| `#` | random digit 0–9 |

Any other character is inserted verbatim.

Example:

```python
settings.ID_TEMPLATES_BY_TAG["<PATIENT_ID>"] = "P######"    # Patient IDs like P123456
settings.ID_TEMPLATES_BY_TAG["<Z-NUMMER>"] = "Z-###-###"      # Z-numbers like Z-123-456
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
