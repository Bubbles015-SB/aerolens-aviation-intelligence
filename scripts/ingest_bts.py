#!/usr/bin/env python3
"""Load an *authentic* separately downloaded BTS T100 extract; never bundle fake capacity."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from aerolens.ingest import export_bts_summary

def main(argv=None):
 p=argparse.ArgumentParser(description='Validate/aggregate BY-YEAR-BY-MONTH actual supplied BTS T100 segments')
 p.add_argument('source',help='Official BTS T-100 CSV export path (not included)')
 p.add_argument('--output',default=str(ROOT/'data/derived/bts_t100_verified_import.csv'))
 p.add_argument('--source-note',help='URL and date of the exact downloaded BTS extract',required=True)
 args=p.parse_args(argv)
 if not args.source_note.strip():p.error('Supply actual BTS source and download date.')
 count=export_bts_summary(args.source,args.output)
 provenance=Path(args.output).with_suffix('.SOURCE.txt')
 provenance.write_text(f'Data supplier: U.S. Bureau of Transportation Statistics T-100\nSource record: {args.source_note}\nFile supplied by analyst: {args.source}\nAggregated rows: {count}\nNote: segment measurements, not complete O&D passenger flows.\n',encoding='utf-8')
 print(f'Validated {count} LHR segment groups → {args.output}\nDocumented source: {provenance}')
if __name__=='__main__':main()
