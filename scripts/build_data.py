#!/usr/bin/env python3
"""Deterministic raw CSV -> browser JS + derived CSV build. Stdlib only."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/caa_lhr_us_annual_2025_2024_curated.csv'
OUTPUT = ROOT / 'assets/data.js'
DERIVED = ROOT / 'data/derived/route_summary.csv'


def load_routes(path=RAW):
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        expected = ['airport','city','region','passengers_2024','passengers_2025']
        if reader.fieldnames != expected:
            raise ValueError(f'Expected {expected}; got {reader.fieldnames}')
        rows = []
        for i, r in enumerate(reader, start=2):
            code = r['airport'].strip()
            if not (len(code) == 3 and code.isascii() and code.isupper()):
                raise ValueError(f'Invalid IATA code on line {i}: {code!r}')
            a,b = int(r['passengers_2024']),int(r['passengers_2025'])
            if a <= 0 or b <= 0: raise ValueError(f'Nonpositive passenger value on line {i}')
            if not r['city'].strip() or not r['region'].strip():
                raise ValueError(f'Missing city or region on line {i}')
            rows.append(dict(code=code,city=r['city'].strip(),region=r['region'].strip(),y2024=a,y2025=b,
                             delta=b-a,growth_pct=round(100*(b-a)/a,4)))
    codes = [r['code'] for r in rows]
    if len(codes) != len(set(codes)): raise ValueError('Duplicate route code')
    if len(rows) < 10: raise ValueError('Curated coverage unexpectedly small')
    return rows


def summary(routes):
    total24 = sum(r['y2024'] for r in routes)
    total25 = sum(r['y2025'] for r in routes)
    return dict(routes=len(routes),pax_2024=total24,pax_2025=total25,
                delta=total25-total24,growth_pct=round((total25/total24-1)*100,2),
                growing_routes=sum(r['delta']>0 for r in routes),
                declining_routes=sum(r['delta']<0 for r in routes),
                largest_2025=max(routes,key=lambda r:r['y2025'])['code'],
                largest_loss=min(routes,key=lambda r:r['delta'])['code'])


def build():
    routes = load_routes()
    bundle={
        'meta':{
            'dataset':'CAA Table 12.1 — 2025 Annual International Air Passenger Traffic Route Analysis',
            'basis':'Heathrow to/from selected US airports; all airlines; both directions; total passengers',
            'years':[2024,2025],
            'source_pdf':'https://www.caa.co.uk/Documents/Download/24007/87fb7670-4e10-4aeb-942d-509238aa25a1/17511',
            'source_page':'90 of PDF / printed table pages 89–90 (0-index PDF p89)',
            'limitations':['Selected airport markets, not exhaustive Heathrow–US list',
                           'Airport-pair market totals, not any specific airline traffic or revenue',
                           'No airline-level seats, fares, profit, seasonality or true load factors']
        },
        'summary':summary(routes),
        'routes':routes
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text('/* GENERATED: python scripts/build_data.py; DO NOT EDIT BY HAND */\nwindow.AEROLENS_DATA = '+
                      json.dumps(bundle,separators=(',',':'),ensure_ascii=False)+';\n',encoding='utf-8')
    with DERIVED.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['code','city','region','y2024','y2025','delta','growth_pct'])
        w.writeheader();w.writerows(routes)
    print('Wrote',OUTPUT,'and',DERIVED,'for',len(routes),'markets')
    return bundle

if __name__ == '__main__': build()
