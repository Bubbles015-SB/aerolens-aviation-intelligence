#!/usr/bin/env python3
"""Reproducibly generate advanced network and research provenance JS bundle."""
import json, sys, hashlib
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from aerolens.connectivity import generate_scenario,AIRPORTS,LEG_TEMPLATES,MCT_MINUTES
from aerolens.commercial import Inputs,economics


def build():
    flights=generate_scenario(date(2026,11,3),7)
    airports={k:{'timezone':v[0],'latitude':v[1],'longitude':v[2]} for k,v in AIRPORTS.items()}
    curated=(ROOT/'data/raw/caa_lhr_us_annual_2025_2024_curated.csv').read_bytes()
    bundle={
        'version':'2.0.0',
        'provenance':{'caa_source':'https://www.caa.co.uk/data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-2025/annual-2025/',
            'caa_table':'Table 12.1, selected LHR to US airports, total ALL-airline BOTH-direction traffic',
            'caa_csv_sha256':hashlib.sha256(curated).hexdigest(),
            'synthetic_notice':'ALL displayed flight times, carriers, transfer rules, fares, costs and probabilities in labs are fabricated training inputs.',
            'simulation_year':'2026-11-03 through 2026-11-09: FICTIONAL test week',
            'inference_warning':'CAA passenger market totals cannot reveal individual airline fares, seats, load factors, route economics, punctuality or alliance revenues.'},
        'airports':airports,
        'mct':MCT_MINUTES,
        'flights':[x.export() for x in flights],
        'model_assumptions':{'connection_base_leg_success':.94,'emissions_proxy_kg_per_pax_km':.09,
                              'break_even_inputs':Inputs(total_market_passengers=1000000).__dict__,
                              'economic_assumptions':'All financial and reliability inputs are illustrative; cost figures are not industry benchmarks.'},
    }
    raw=ROOT/'data/advanced/synthetic_time_aware_schedule.json'
    raw.write_text(json.dumps({'provenance':bundle['provenance'],'flights':bundle['flights']},indent=2)+'\n',encoding='utf-8')
    js=ROOT/'assets/advanced_data.js'
    js.write_text('/* GENERATED: python scripts/build_advanced.py; synthetic scenarios only */\nwindow.AEROLENS_ADVANCED = '+json.dumps(bundle,separators=(',',':'))+';\n',encoding='utf-8')
    print(f'Built {len(flights)} dated UTC-valid hypothetical legs; SHA256 CAA: {bundle["provenance"]["caa_csv_sha256"][:12]}')
    return bundle

if __name__=='__main__':build()
