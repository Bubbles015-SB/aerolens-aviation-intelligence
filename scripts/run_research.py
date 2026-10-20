#!/usr/bin/env python3
"""Auditable Python command-line report for independent review (all financials hypothetical)."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from aerolens.commercial import Inputs,economics,simulate
from aerolens.connectivity import generate_scenario,enumerate_itineraries,pareto_frontier
from scripts.build_data import load_routes

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--market',default='JFK',help='Airport code among 28 CAA selected markets')
 ap.add_argument('--capture',type=float,default=5.0,help='Hypothetical all-carrier traffic share (%)')
 ap.add_argument('--destination',default='MIA',help='Synthetic connection endpoint from LHR')
 ap.add_argument('--json-out',default='',help='Write full report JSON file')
 a=ap.parse_args()
 routes={r['code']:r for r in load_routes()}
 if a.market not in routes:ap.error(f'Unknown market {a.market}; choose among {list(routes)}')
 route=routes[a.market]
 params=Inputs(total_market_passengers=route['y2025'],assumed_capture_pct=a.capture)
 finance=economics(params);uncertainty=simulate(params,draws=2500)
 scenario=generate_scenario()
 paths=enumerate_itineraries(scenario,'LHR',a.destination,carriers={'AX','DX','CX','BX'},buffer_minutes=15)
 report=dict(disclaimer='Only CAA passenger data are sourced. All schedules, risk inputs and commercial values hypothetical.',
             observed_market={'airport':route['code'],'city':route['city'],'passengers_2024':route['y2024'],
                              'passengers_2025':route['y2025'],'yoy_pct':route['growth_pct']},
             synthetic_financial_inputs=params.__dict__,synthetic_financial_scenario=finance,
             synthetic_stress_result=uncertainty,
             synthetic_connection_options=paths[:5])
 encoded=json.dumps(report,indent=2,ensure_ascii=False)
 if a.json_out:Path(a.json_out).write_text(encoded+'\n',encoding='utf-8')
 print(encoded)
if __name__=='__main__':main()
