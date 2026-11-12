# Waldviertel Imaginary Village Names Generator

A static web application and data extraction pipeline that generates authentically sounding compound imaginary village names based on real places in the **Waldviertel** region of Lower Austria (*Niederösterreich*).

---

## Overview

The Waldviertel has a distinct toponymic landscape shaped by medieval forest clearings (*-schlag*, *-reith*), historical manors (*-hof*), and topographical markers (*-bach*, *-berg*, *-stein*). 

This project:
1. Filters official Austrian municipal register data for all Ortschaften across the Waldviertel districts.
2. Uses the German compound splitter [`charsplit`](https://github.com/dtuggener/CharSplit) to segment two-word compound names into their base prefixes (start words) and suffixes (end words).
3. Extracts components occurring multiple times and links them to their original source villages.
4. Provides a standalone static webpage to generate and explore authentic imaginary village names.

---

## Data & Output Files

- `data/ortschaften_oesterreich.csv`: Source dataset of Austrian settlements.
- `data/waldviertel_ortsnamen.csv`: 1,063 Waldviertel settlements with their assigned political district (*Bezirk*):
  - **Gmünd** (`309xx`)
  - **Horn** (`311xx`)
  - **Krems (Land)** (`313xx`)
  - **Krems an der Donau** (`301xx`)
  - **Waidhofen an der Thaya** (`322xx`)
  - **Zwettl** (`325xx`)
- `data/waldviertel_extracted_words.csv`: Every occurrence of recurring start and end words paired with its original village name reference (`word,type,frequency,origin`).
- `data/waldviertel_words_summary.csv`: Aggregated vocabulary of recurring components (110 start words, 121 end words) with full semicolon-separated origin lists.
- `web_data.js`: Pre-computed JSON payload embedded for offline static execution.

---

## Python Pipeline

### Prerequisites

Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install "git+https://github.com/dtuggener/CharSplit" geopy
```

### Run Extraction

```bash
python process_data.py
```

---

## Static Webpage

Open `index.html` directly in any web browser or serve via:

```bash
python -m http.server 8000
```

### Webpage Features
- **Instant Generation**: Generates compound imaginary names adhering to Waldviertel phonetics.
- **Etymological Breakdown**: Displays the real origin villages from which the prefix and suffix originated.
- **Fictional Guarantee**: Validates combinations against the real settlement registry to ensure generated names are genuinely fictional.
- **Component Locking & Batch Mode**: Lock preferred prefixes/suffixes or generate multiple names at once.
- **Keyboard Shortcut**: Press <kbd>Spacebar</kbd> to generate a new name.
