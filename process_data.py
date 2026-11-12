#!/usr/bin/env python3
"""
Waldviertel Village Names Processor
1. Extracts all Ortsnamen in Waldviertel from data/ortschaften_oesterreich.csv and adds their Bezirk.
2. Uses charsplit to split compound village names into start and end components.
3. Extracts start and end words that occur multiple times.
4. Saves the results to CSV files and exports data for the static webpage.
"""

import csv
import json
import os
from collections import Counter, defaultdict
import charsplit
from geopy.geocoders import Nominatim

# Lower Austria (GKZ prefix 3) Bezirke belonging to Waldviertel:
# 301: Krems an der Donau (Statutarstadt)
# 309: Gmünd
# 311: Horn
# 313: Krems (Land)
# 322: Waidhofen an der Thaya
# 325: Zwettl
WALDVIERTEL_BEZIRKE = {
    '301': 'Krems an der Donau',
    '309': 'Gmünd',
    '311': 'Horn',
    '313': 'Krems (Land)',
    '322': 'Waidhofen an der Thaya',
    '325': 'Zwettl',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_CSV = os.path.join(DATA_DIR, 'ortschaften_oesterreich.csv')
ORTSNAMEN_CSV = os.path.join(DATA_DIR, 'waldviertel_ortsnamen.csv')
EXTRACTED_WORDS_CSV = os.path.join(DATA_DIR, 'waldviertel_extracted_words.csv')
WORDS_SUMMARY_CSV = os.path.join(DATA_DIR, 'waldviertel_words_summary.csv')
WEB_DATA_JS = os.path.join(BASE_DIR, 'web_data.js')


def load_waldviertel_data():
    records = []
    # geolocator = Nominatim(user_agent="waldviertel_name_generator_2", timeout=10)
    with open(INPUT_CSV, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 3 and row[3][:3] in WALDVIERTEL_BEZIRKE:
                okz = row[0].strip()
                ortsname = row[1].strip()
                plz = row[2].strip()
                gkz = row[3].strip()
                gemeindename = row[4].strip() if len(row) > 4 else ''
                bezirk = WALDVIERTEL_BEZIRKE[gkz[:3]]

                # location = geolocator.geocode(ortsname, country_codes="at")
                # print(f"\t{ortsname}: {(location.latitude, location.longitude)}")

                records.append({
                    'okz': okz,
                    'ortsname': ortsname,
                    'bezirk': bezirk,
                    'plz': plz,
                    'gkz': gkz,
                    'gemeindename': gemeindename,
                    # 'latitude': location.latitude,
                    # 'longitude': location.longitude
                })
    return records


def save_ortsnamen_csv(records):
    fieldnames = ['ortsname', 'bezirk', 'plz', 'gkz', 'gemeindename', 'okz']
    with open(ORTSNAMEN_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    print(f"Saved {len(records)} Waldviertel Ortsnamen to {ORTSNAMEN_CSV}")


def split_village_names(records):
    splitter = charsplit.Splitter()

    # Map each unique village name to its Bezirke and records
    name_to_records = defaultdict(list)
    for r in records:
        name_to_records[r['ortsname']].append(r)

    unique_names = sorted(name_to_records.keys())

    start_counter = Counter()
    end_counter = Counter()
    start_origins = defaultdict(set)
    end_origins = defaultdict(set)
    splits_by_name = {}

    for name in unique_names:
        res = splitter.split_compound(name)
        if not res:
            continue
        score, start, end = res[0]
        start = start.strip()
        end = end.strip()
        if not start or not end:
            continue
        # Skip if charsplit could not split the word
        if start.lower() == end.lower() == name.lower():
            continue

        splits_by_name[name] = (start, end, score)
        start_counter[start] += 1
        end_counter[end] += 1
        start_origins[start].add(name)
        end_origins[end].add(name)

    # Filter for words that occur multiple times (> 1)
    mult_starts = {w: c for w, c in start_counter.items() if c > 1}
    mult_ends = {w: c for w, c in end_counter.items() if c > 1}

    return {
        'unique_names': unique_names,
        'splits_by_name': splits_by_name,
        'mult_starts': mult_starts,
        'mult_ends': mult_ends,
        'start_origins': start_origins,
        'end_origins': end_origins,
        'name_to_records': name_to_records,
    }


def save_extracted_words_csv(split_data):
    mult_starts = split_data['mult_starts']
    mult_ends = split_data['mult_ends']
    start_origins = split_data['start_origins']
    end_origins = split_data['end_origins']

    # 1. Occurrence level CSV: word, type, frequency, origin
    rows = []
    # Add start words
    for word, count in sorted(mult_starts.items(), key=lambda x: (-x[1], x[0])):
        for origin in sorted(start_origins[word]):
            rows.append({
                'word': word,
                'type': 'start',
                'frequency': count,
                'origin': origin,
            })
    # Add end words
    for word, count in sorted(mult_ends.items(), key=lambda x: (-x[1], x[0])):
        for origin in sorted(end_origins[word]):
            rows.append({
                'word': word,
                'type': 'end',
                'frequency': count,
                'origin': origin,
            })

    with open(EXTRACTED_WORDS_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'type', 'frequency', 'origin'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} extracted word entries to {EXTRACTED_WORDS_CSV}")

    # 2. Aggregated summary CSV: word, type, frequency, origins
    summary_rows = []
    for word, count in sorted(mult_starts.items(), key=lambda x: (-x[1], x[0])):
        origins_str = '; '.join(sorted(start_origins[word]))
        summary_rows.append({
            'word': word,
            'type': 'start',
            'frequency': count,
            'origins': origins_str,
        })
    for word, count in sorted(mult_ends.items(), key=lambda x: (-x[1], x[0])):
        origins_str = '; '.join(sorted(end_origins[word]))
        summary_rows.append({
            'word': word,
            'type': 'end',
            'frequency': count,
            'origins': origins_str,
        })

    with open(WORDS_SUMMARY_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'type', 'frequency', 'origins'])
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Saved {len(summary_rows)} summary words to {WORDS_SUMMARY_CSV}")


def export_web_data(records, split_data):
    mult_starts = split_data['mult_starts']
    mult_ends = split_data['mult_ends']
    start_origins = split_data['start_origins']
    end_origins = split_data['end_origins']
    unique_names = set(split_data['unique_names'])

    start_list = [
        {
            'word': w,
            'count': mult_starts[w],
            'origins': sorted(list(start_origins[w])),
        }
        for w in sorted(mult_starts.keys(), key=lambda x: (-mult_starts[x], x))
    ]

    end_list = [
        {
            'word': w,
            'count': mult_ends[w],
            'origins': sorted(list(end_origins[w])),
        }
        for w in sorted(mult_ends.keys(), key=lambda x: (-mult_ends[x], x))
    ]

    web_payload = {
        'totalOrtschaften': len(records),
        'uniqueRealNames': sorted(list(unique_names)),
        'startWords': start_list,
        'endWords': end_list,
        'bezirke': list(set(WALDVIERTEL_BEZIRKE.values())),
    }

    content = f"// Generated Waldviertel data for static village generator\nwindow.WALDVIERTEL_DATA = {json.dumps(web_payload, ensure_ascii=False, indent=2)};\n"
    with open(WEB_DATA_JS, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Exported web data payload to {WEB_DATA_JS}")


def main():
    print("Step 1: Extracting Waldviertel records...")
    records = load_waldviertel_data()
    save_ortsnamen_csv(records)

    print("Step 2: Splitting village names with charsplit...")
    split_data = split_village_names(records)

    print("Step 3: Saving extracted words to CSV...")
    save_extracted_words_csv(split_data)

    print("Step 4: Exporting web data...")
    export_web_data(records, split_data)
    print("Done!")


if __name__ == '__main__':
    main()
