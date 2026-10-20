#!/usr/bin/env python3
"""Run a reproducible SQL example from the curated CAA CSV; stdlib sqlite3."""
import csv
import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(':memory:')
conn.row_factory = sqlite3.Row
conn.execute('CREATE TABLE lhr_us_routes (code TEXT PRIMARY KEY, city TEXT NOT NULL, region TEXT NOT NULL, y2024 INTEGER NOT NULL, y2025 INTEGER NOT NULL)')
with (ROOT / 'data/raw/caa_lhr_us_annual_2025_2024_curated.csv').open(newline='', encoding='utf-8') as f:
    records = list(csv.DictReader(f))
conn.executemany('INSERT INTO lhr_us_routes VALUES (?,?,?,?,?)',[(r['airport'],r['city'],r['region'],int(r['passengers_2024']),int(r['passengers_2025'])) for r in records])
queries = (ROOT/'sql/market_analysis.sql').read_text(encoding='utf-8').split(';')
for idx, query in enumerate(queries,1):
    # sqlite ignores comment-only SQL blocks and query 1 contains comments.
    if not query.strip() or not any(line.lstrip().upper().startswith(('SELECT','WITH')) for line in query.splitlines()):
        continue
    cursor=conn.execute(query)
    print(f'\n=== SQL Query {idx} ===')
    cols=[d[0] for d in cursor.description]
    print(' | '.join(cols))
    for row in cursor.fetchmany(7):
        print(' | '.join(str(row[k]) for k in cols))
