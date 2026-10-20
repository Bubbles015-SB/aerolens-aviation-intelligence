#!/usr/bin/env python3
"""Generate editable Microsoft Power BI PBIP/TMDL/PBIR project.

This is static authoring against published open-format schemas. We can lint and
validate cross-references offline, but cannot claim Power BI Desktop execution.
"""
from __future__ import annotations
import csv,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PBI=ROOT/'powerbi'
NAME='AeroLensIntelligence'
base=PBI/NAME
sm=base/f'{NAME}.SemanticModel'
rep=base/f'{NAME}.Report'
tables=sm/'definition/tables'
reportdef=rep/'definition'

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def write(path,s):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(s.rstrip()+'\n',encoding='utf-8')

def readcsv(filename):
    with (ROOT/'data/bi'/filename).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

write_json(base/(NAME+'.pbip'),{
  '$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json',
  'version':'1.0','artifacts':[{'report':{'path':NAME+'.Report'}}],
  'settings':{'enableAutoRecovery':True}})
write_json(sm/'definition.pbism',{
  '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json',
  'version':'4.2','settings':{'qnaEnabled':True}})
write(sm/'definition/database.tmdl',"database 6199164e-a615-4d9e-9aac-cace63d0183e\n\tcompatibilityLevel: 1702\n\tcompatibilityMode: powerBI\n\tlanguage: 1033\n")
write(sm/'definition/model.tmdl',"model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\tdiscourageImplicitMeasures\n\nref table MarketObservations\nref table FleetScenarios\nref table EvidenceRegister\nref table NetworkScenarios\nref table EmissionsScenarios\nref table ForecastDemo\n")

TDEF={
  'MarketObservations':('market_observed_long.csv',[
   ('code','string'),('city','string'),('region','string'),('year','int64'),('passengers','int64'),('classification','string')]),
  'FleetScenarios':('portfolio_route_scenarios.csv',[
   ('code','string'),('city','string'),('observed_2025_market_passengers','int64'),('assumed_weekly_demand','int64'),
   ('seats_per_flight','int64'),('assumed_fare_gbp','double'),('assumed_departure_cost_gbp','double'),
   ('assumed_variable_cost_per_pax_gbp','double'),('assumed_block_hours_per_flight','int64'),
   ('assumed_emissions_t_per_flight','int64'),('max_weekly_flights','int64'),('assumed_distance_km','double'),('classification','string')]),
  'EvidenceRegister':('synthetic_assurance_records.csv',[
   ('id','string'),('requirement','string'),('criticality','string'),('revision','int64'),('approved_revision','int64'),
   ('approved','boolean'),('due_date','string'),('status','string'),('issues','string'),('classification','string')]),
 'NetworkScenarios':('synthetic_network_legs.csv',[
   ('flight_id','string'),('carrier','string'),('origin','string'),('destination','string'),
   ('departure_utc','string'),('arrival_utc','string'),('duration_minutes','int64'),('classification','string')]),
 'EmissionsScenarios':('synthetic_emissions.csv',[
   ('code','string'),('city','string'),('hypothetical_departures_per_week','int64'),('great_circle_km','double'),
   ('assumed_block_hours_per_flight','int64'),('model_fuel_t','double'),('model_co2_t','double'),
   ('model_kg_co2_per_pax_km','double'),('classification','string')]),
 'ForecastDemo':('synthetic_monthly_forecast_demo.csv',[
   ('month','string'),('modelled_passengers','int64'),('period','string'),('classification','string')]),
}

MEASURES={
 'MarketObservations':[
   ('Selected Passenger Movements',"SUM('MarketObservations'[passengers])",'#,##0'),
   ('2025 Market Movements',"CALCULATE(SUM('MarketObservations'[passengers]), 'MarketObservations'[year] = 2025)",'#,##0'),
   ('2024 Market Movements',"CALCULATE(SUM('MarketObservations'[passengers]), 'MarketObservations'[year] = 2024)",'#,##0'),
   ('Market YoY Change',"[2025 Market Movements] - [2024 Market Movements]",'#,##0'),
   ('Market YoY Growth %',"DIVIDE([Market YoY Change],[2024 Market Movements])",'0.0%'),
   ('Airport Markets',"DISTINCTCOUNT('MarketObservations'[code])",'#,##0'),
   ('Data Boundary Notice', '"CAA: selected airport pairs, all airlines, both directions; no route-level profitability"',None)
 ],
 'FleetScenarios':[
  ('Routes in Scenario',"COUNTROWS('FleetScenarios')",'#,##0'),
  ('Assumed Weekly Demand',"SUM('FleetScenarios'[assumed_weekly_demand])",'#,##0'),
  ('Illustrative Maximum Weekly Seats',"SUMX('FleetScenarios','FleetScenarios'[max_weekly_flights]*'FleetScenarios'[seats_per_flight])",'#,##0'),
  ('Illustrative Maximum Block Hours',"SUMX('FleetScenarios','FleetScenarios'[max_weekly_flights]*'FleetScenarios'[assumed_block_hours_per_flight])",'#,##0'),
  ('Illustrative Maximum CO2 Tonnes',"SUMX('FleetScenarios','FleetScenarios'[max_weekly_flights]*'FleetScenarios'[assumed_emissions_t_per_flight])",'#,##0'),
  ('Illustrative Weekly Gross Sales at Capacity',"SUMX('FleetScenarios',MIN('FleetScenarios'[assumed_weekly_demand],'FleetScenarios'[max_weekly_flights]*'FleetScenarios'[seats_per_flight])*'FleetScenarios'[assumed_fare_gbp])",'£#,##0'),
 ],
 'EvidenceRegister':[
   ('Synthetic Documents',"COUNTROWS('EvidenceRegister')",'#,##0'),
   ('Review Ready Documents',"CALCULATE(COUNTROWS('EvidenceRegister'), 'EvidenceRegister'[status] = \"ready\")",'#,##0'),
   ('Blocked Documents',"CALCULATE(COUNTROWS('EvidenceRegister'), 'EvidenceRegister'[status] = \"blocked\")",'#,##0'),
   ('Readiness %',"DIVIDE([Review Ready Documents],[Synthetic Documents])",'0.0%'),
   ('Critical Blocked',"CALCULATE(COUNTROWS('EvidenceRegister'), 'EvidenceRegister'[status] = \"blocked\", 'EvidenceRegister'[criticality] = \"critical\")",'#,##0'),
 ],
 'NetworkScenarios':[
   ('Synthetic Flight Legs',"COUNTROWS('NetworkScenarios')",'#,##0'),
   ('Synthetic Average Segment Minutes',"AVERAGE('NetworkScenarios'[duration_minutes])",'#,##0'),
   ('Fictional Operators',"DISTINCTCOUNT('NetworkScenarios'[carrier])",'#,##0'),
 ],
 'EmissionsScenarios':[
   ('Scenario Weekly CO2 Tonnes',"SUM('EmissionsScenarios'[model_co2_t])",'#,##0.0'),
   ('Scenario Weekly Fuel Tonnes',"SUM('EmissionsScenarios'[model_fuel_t])",'#,##0.0'),
   ('Scenario Weekly Departures',"SUM('EmissionsScenarios'[hypothetical_departures_per_week])",'#,##0'),
 ],
 'ForecastDemo':[
   ('Synthetic Monthly Passengers',"SUM('ForecastDemo'[modelled_passengers])",'#,##0'),
   ('Synthetic Time Points',"COUNTROWS('ForecastDemo')",'#,##0'),
 ]
}


def mvalue(cell,datatype):
    if datatype=='string':return '"'+str(cell).replace('"','""')+'"'
    if datatype=='boolean':return 'true' if cell.lower() in ('true','1') else 'false'
    if datatype=='int64':return str(int(cell))
    if datatype=='double':return repr(float(cell))
    raise AssertionError(datatype)

for table,(csvfile,fields) in TDEF.items():
    values=readcsv(csvfile)
    cols=', '.join(f'{name} = '+ {'int64':'Int64.Type','double':'type number','boolean':'type logical','string':'type text'}[kind] for name,kind in fields)
    data='\n'.join('            {'+', '.join(mvalue(row[name],kind) for name,kind in fields)+'},' for row in values)
    data=data.rstrip(',')
    source=f'''let
    Source = #table(type table [{cols}], {{
{data}
    }})
in
    Source'''
    lines=['table '+table,'']
    for name,expr,fmt in MEASURES[table]:
        lines.append('\tmeasure '+("'"+name+"'" if ' ' in name else name)+' = '+expr)
        if fmt:lines.append('\t\tformatString: '+fmt)
        lines.append('')
    for name,kind in fields:
        lines.extend(['\tcolumn '+name,'\t\tdataType: '+kind,'\t\tsummarizeBy: none','\t\tsourceColumn: '+name,''])
    lines.extend(['\tpartition '+table+' = m','\t\tmode: import','\t\tsource =',*('\t\t\t'+line for line in source.splitlines())])
    write(tables/(table+'.tmdl'),'\n'.join(lines))

write_json(rep/'definition.pbir',{
 '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json',
 'version':'4.0','datasetReference':{'byPath':{'path':'../'+NAME+'.SemanticModel'}}})
write_json(reportdef/'version.json',{
 '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json',
 'version':'2.0.0'})
write_json(reportdef/'report.json',{
 '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json',
 'settings':{'useStylableVisualContainerHeader':True,'defaultFilterActionIsDataFilter':True,'useEnhancedTooltips':True}})

# Public PBIR schema. Simplified built-in native visuals with explicit semantic field queries.
PAGE_SPEC=[
 ('Aviation Markets', 'MarketObservations',[
  ('card','2025 Market Movements', 40,30,400,145),
  ('card','Market YoY Growth %',460,30,380,145),
  ('clusteredBarChart',('city','2025 Market Movements'),40,210,790,400),
  ('tableEx',('city','year','passengers'),850,30,380,580)]),
 ('Aerospace Fleet Scenarios', 'FleetScenarios',[
  ('card','Routes in Scenario',40,30,385,145),
  ('card','Assumed Weekly Demand',450,30,385,145),
  ('clusteredBarChart',('code','assumed_weekly_demand'),40,210,790,400),
  ('tableEx',('code','assumed_block_hours_per_flight','assumed_emissions_t_per_flight','assumed_fare_gbp'),850,30,380,580)]),
 ('Engineering Evidence', 'EvidenceRegister',[
  ('card','Readiness %',40,30,385,145),
  ('card','Blocked Documents',450,30,385,145),
  ('clusteredBarChart',('requirement','Synthetic Documents'),40,210,790,400),
  ('tableEx',('id','requirement','status','issues'),850,30,380,580)]),
 ('Network Connectivity (Synthetic)', 'NetworkScenarios',[
  ('card','Synthetic Flight Legs',40,30,385,145),
  ('card','Fictional Operators',450,30,385,145),
  ('clusteredBarChart',('origin','Synthetic Flight Legs'),40,210,790,400),
  ('tableEx',('flight_id','carrier','origin','destination','duration_minutes'),850,30,380,580)]),
 ('Sustainability Scenarios', 'EmissionsScenarios',[
  ('card','Scenario Weekly CO2 Tonnes',40,30,385,145),
  ('card','Scenario Weekly Fuel Tonnes',450,30,385,145),
  ('clusteredBarChart',('code','Scenario Weekly CO2 Tonnes'),40,210,790,400),
  ('tableEx',('code','great_circle_km','model_co2_t','model_kg_co2_per_pax_km'),850,30,380,580)]),
 ('Forecasting Demonstration (Synthetic)', 'ForecastDemo',[
  ('card','Synthetic Monthly Passengers',40,30,385,145),
  ('card','Synthetic Time Points',450,30,385,145),
  ('lineChart',('month','Synthetic Monthly Passengers'),40,210,790,400),
  ('tableEx',('month','modelled_passengers','period'),850,30,380,580)]),
]

def id20(value):return hashlib.sha256(value.encode()).hexdigest()[:20]

def projection(table,field):
    measure=any(name==field for name,_,_ in MEASURES[table]); type_key='Measure' if measure else 'Column'
    return {'field':{type_key:{'Expression':{'SourceRef':{'Entity':table}},'Property':field}},'queryRef':f'{table}.{field}'}

page_order=[]
for page_title,table,vis_specs in PAGE_SPEC:
    pageid=id20('page:'+page_title);page_order.append(pageid)
    pagedir=reportdef/'pages'/pageid
    write_json(pagedir/'page.json',{
      '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json',
      'name':pageid,'displayName':page_title,'displayOption':'FitToPage','height':720,'width':1280})
    for i,(vis,field,x,y,w,h) in enumerate(vis_specs):
        vid=id20(page_title+str(i)+vis)
        if vis=='card':state={'Values':{'projections':[projection(table,field)]}}
        elif vis in ('clusteredBarChart','lineChart'):
            a,b=field;state={'Category':{'projections':[projection(table,a)]},'Y':{'projections':[projection(table,b)]}}
        else:state={'Values':{'projections':[projection(table,q) for q in field]}}
        obj={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json',
             'name':vid,'position':{'x':x,'y':y,'z':1000+i,'height':h,'width':w,'tabOrder':i},
             'visual':{'visualType':vis,'query':{'queryState':state},'drillFilterOtherVisuals':True}}
        write_json(pagedir/'visuals'/vid/'visual.json',obj)
write_json(reportdef/'pages/pages.json',{
 '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json',
 'pageOrder':page_order,'activePageName':page_order[0]})
write(PBI/'README.md',f'''# AeroLens 3 Power BI project (PBIP / TMDL / PBIR)

**Editable source files created, not a screenshot or a PBIX rename.**

1. Open `powerbi/{NAME}/{NAME}.pbip` in **Microsoft Power BI Desktop** on Windows.
2. Enable PBIP / PBIR / TMDL project features in File → Options → Preview Features if required by your Desktop build.
3. Refresh the six imported tables and check all visuals render. Embedded Power Query `#table` data is self-contained, with no external file path.
4. Optionally replace each `#table` partition with the corresponding CSV import under `data/bi/` for refreshed source data.
5. Save as PBIX in Desktop if required; that proprietary file is not generated by this repo.

## Evidence boundaries

- MarketObservations: 56 **observed** rows (2024 and 2025) manually curated from the UK CAA; **all airlines, both directions**.
- FleetScenarios: 9 **illustrative** routes; only `observed_2025_market_passengers` originates from observed CAA records. All cost, yield, block-time and carbon fields are *invented parameters*.
- EvidenceRegister: 40 **synthetic, fictional** technical-record scenarios; no actual design/certification data.
- NetworkScenarios: 154 **fictional** dated flight legs with correct UTC chronology and made-up carrier identifiers.
- EmissionsScenarios: 9 **hypothetical** route emissions estimates, not measured aircraft data.
- ForecastDemo: 48 **synthetic** month records, only for demonstration, not observed seasonality.

## Important validation qualification

The PBIP layout and JSON cross-references are checked offline; **Power BI Desktop cannot run in this environment**, so its final rendering, DAX execution and refresh are **not claimed verified**. Open and save it in Desktop to complete validation before presenting it as a functioning Power BI report.

Docs: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
''')
# validate references and required artifact layout
for path in (base/(NAME+'.pbip'),sm/'definition.pbism',rep/'definition.pbir',reportdef/'pages/pages.json'):
    assert path.exists()
for tbl in TDEF: assert (tables/(tbl+'.tmdl')).exists()
for pageid in page_order:
    page=reportdef/'pages'/pageid
    assert len(list((page/'visuals').glob('*/visual.json')))==4
print('Generated PBIP model with',len(TDEF),'tables,',sum(map(len,MEASURES.values())),'DAX measures,',len(page_order),'report pages and',len(page_order)*4,'visuals. Desktop not tested.')
