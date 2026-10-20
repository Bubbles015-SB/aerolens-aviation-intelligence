#!/usr/bin/env python3
"""Validate and summarise externally sourced dated flights (does not assert authenticity)."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aerolens.operations import import_schedule
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('csvfile');p.add_argument('--source-note',required=True)
a=p.parse_args();r=import_schedule(a.csvfile,a.source_note)
print(json.dumps({'records':len(r['flights']),'sha256':r['sha256'],'source_note':r['source'],
                  'authenticity':r['authenticity'],'first_departure_utc':r['flights'][0].depart_utc.isoformat()},indent=2))
