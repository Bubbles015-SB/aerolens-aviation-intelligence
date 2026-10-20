#!/usr/bin/env python3
"""Deterministic AeroLens 3 enterprise scenario/BI exports; stdlib only."""
from pathlib import Path
from datetime import date,timedelta
from dataclasses import asdict
from hashlib import sha256
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build_data import load_routes
from aerolens.portfolio import RouteOption,optimise,stress_portfolio
from aerolens.sustainability import great_circle_km,flight_emission_scenario
from aerolens.assurance import Evidence,audit
from aerolens.connectivity import AIRPORTS
DATA=ROOT/'data/bi';DATA.mkdir(parents=True,exist_ok=True)
AIRCRAFT={'family':'Illustrative 250-seat twinjet','seats':250,'fuel_burn_kg_per_hour':5500,'co2_factor':3.16,'assumption':True}
options=[]
for r in load_routes():
    code=r['code']
    if code not in AIRPORTS:continue
    if code=='LHR':continue
    # A curated route scenario, not an inference of an actual airline's economics.
    tz,lat,lon=AIRPORTS[code]
    _,a_lat,a_lon=AIRPORTS['LHR']
    dist=great_circle_km(a_lat,a_lon,lat,lon)
    block_hr=max(4,round(dist/810+1.0))
    assumed_weekly_demand=round(r['y2025']/52*.09)
    fare=round(195+dist*.064,0)
    dep_cost=round(9500+dist*3.65,0)
    carbon_t=max(1,round(block_hr*AIRCRAFT['fuel_burn_kg_per_hour']*AIRCRAFT['co2_factor']/1000))
    option=RouteOption(code,assumed_weekly_demand,250,fare,dep_cost,48,block_hr,carbon_t,8)
    options.append((r,option,dist))
options.sort(key=lambda x:x[0]['y2025'],reverse=True)
options=options[:9]
rows=[]
for r,o,d in options:
    rows.append(dict(code=o.code,city=r['city'],observed_2025_market_passengers=r['y2025'],
       assumed_weekly_demand=o.weekly_demand,seats_per_flight=o.seats_per_flight,assumed_fare_gbp=o.fare_gbp,
       assumed_departure_cost_gbp=o.departure_cost_gbp,assumed_variable_cost_per_pax_gbp=o.variable_cost_per_pax_gbp,
       assumed_block_hours_per_flight=o.hours_per_flight,assumed_emissions_t_per_flight=o.emissions_t_per_flight,
       max_weekly_flights=o.max_weekly_flights,assumed_distance_km=round(d,1),classification='MIXED: ONLY observed_2025_market_passengers is official CAA data'))

def dump_csv(file,rows):
    with (DATA/file).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
dump_csv('portfolio_route_scenarios.csv',rows)
obs=[]
for r in load_routes():
    for y in (2024,2025):obs.append(dict(code=r['code'],city=r['city'],region=r['region'],year=y,passengers=r[f'y{y}'],classification='OBSERVED_CAA'))
dump_csv('market_observed_long.csv',obs)

# Synthetic technical records only. Never encode DRDO or other privileged records.
requirements=[('Material verification','HIGH'),('Configuration baseline','CRITICAL'),('Structural substantiation','HIGH'),('Inspection record','MEDIUM'),('Test procedure','MEDIUM'),('Design review evidence','HIGH'),('Release acceptance','CRITICAL'),('Part traceability','MEDIUM')]
records=[];evidence=[]
ref=date(2026,10,19)
for i in range(1,41):
    req,priority=requirements[(i-1)%len(requirements)]
    rev=1+(i%3);approved=not(i%7==0);approved_rev=rev-(1 if i%5==0 else 0)
    evidence.append(Evidence(f'EV-{i:04d}',req,rev,approved_rev,approved,ref+timedelta(days=(i%14)-6),f'synthetic://ev/{i:04d}',priority.lower()))
a=audit(evidence,ref)
for e,result in zip(evidence,a['records_detail']):
    records.append(dict(id=e.id,requirement=e.requirement,criticality=e.criticality,revision=e.revision,
       approved_revision=e.approved_revision,approved=e.approved,due_date=e.due_date.isoformat(),
       status=result['status'],issues=';'.join(result['issues']),classification='SYNTHETIC_SCENARIO'))
dump_csv('synthetic_assurance_records.csv',records)

# Enrich Power BI with clearly labelled synthetic network, sustainability and forecast labs.
network_source=json.loads((ROOT/'data/advanced/synthetic_time_aware_schedule.json').read_text(encoding='utf-8'))
netrows=[dict(flight_id=f['id'],carrier=f['carrier'],origin=f['origin'],destination=f['destination'],
              departure_utc=f['depart_utc'],arrival_utc=f['arrive_utc'],duration_minutes=f['duration_minutes'],
              classification='SYNTHETIC_SCHEDULE') for f in network_source['flights']]
dump_csv('synthetic_network_legs.csv',netrows)
emi=[]
for r,o,d in options:
    m=flight_emission_scenario(d,8,o.seats_per_flight,.82,5500,o.hours_per_flight)
    emi.append(dict(code=o.code,city=r['city'],hypothetical_departures_per_week=8,
                    great_circle_km=round(d,1),assumed_block_hours_per_flight=o.hours_per_flight,
                    model_fuel_t=m['estimated_fuel_t'],model_co2_t=m['estimated_co2_t'],
                    model_kg_co2_per_pax_km=m['emissions_kg_per_passenger_km'],classification='SYNTHETIC_EMISSIONS'))
dump_csv('synthetic_emissions.csv',emi)
forecast_demo=[]
for n in range(48):
    y=2022+n//12;mo=n%12+1
    demo=round(12000+125*n+2400*__import__('math').sin(2*__import__('math').pi*n/12))
    forecast_demo.append(dict(month=f'{y}-{mo:02d}',modelled_passengers=demo,period='synthetic_history',classification='SYNTHETIC_DEMO'))
dump_csv('synthetic_monthly_forecast_demo.csv',forecast_demo)


# Portable 12- and 24-month BI time dims are numeric/or mock: no false real demand history.
res=optimise([o for _,o,_ in options],hours_budget=200,emissions_budget_t=2100)
if not res['feasible']:raise RuntimeError('Could not generate base allocation')
stress=stress_portfolio([o for _,o,_ in options],200,2100,draws=250,seed=20261019)
summary=dict(observed_market_rows=len(obs),observed_market_source='UK CAA Annual 2025, Table 12.1; curated Heathrow–US pairs',
             market_class='all-carrier two-way annual observations',scenario_routes=len(rows),
             records=len(records),assurance_summary={k:v for k,v in a.items() if k!='records_detail'},
             portfolio_optimum=res,portfolio_stress={k:v for k,v in stress.items() if k!='base'},
             source_sha256=sha256((ROOT/'data/raw/caa_lhr_us_annual_2025_2024_curated.csv').read_bytes()).hexdigest())
(ROOT/'data/scenarios/enterprise_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
bundle=dict(meta=dict(title='AeroLens 3 Aerospace & Aviation Intelligence',
                observation='CAA airport pairs: real observations (curated)',
                scenario='All fleet, emissions, financial, scheduling, technical-evidence values invented and labelled'),
            routes=rows,assurance=records,summary=summary,aircraft=AIRCRAFT)
(ROOT/'assets/enterprise_data.js').write_text('/* GENERATED: python scripts/build_enterprise.py */\nwindow.AEROLENS_ENTERPRISE = '+json.dumps(bundle,separators=(',',':'))+';\n',encoding='utf-8')
print('Wrote enterprise scenarios, observed BI long-format, QA matrix and dashboard JS; sources',len(obs),len(rows),len(records))
