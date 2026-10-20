"""AeroLens v2 correctness, boundary and source-separation tests."""
import csv
import json
import sys
import tempfile
import unittest
from datetime import date, timezone, datetime, timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from aerolens.connectivity import (AIRPORTS,MCT_MINUTES,generate_scenario,localized,
                                    enumerate_itineraries,pareto_frontier,haversine_km,itinerary_metrics)
from aerolens.commercial import Inputs,economics,simulate
from aerolens.ingest import import_bts
from scripts.build_advanced import build as build_bundle

class SyntheticNetworkTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.flights=generate_scenario(date(2026,11,3),7)
 def test_dated_schedule_utc_monotonic(self):
  self.assertEqual(len(self.flights),154)
  for f in self.flights:
   self.assertEqual(f.depart_utc.tzinfo,timezone.utc)
   self.assertGreater(f.arrive_utc,f.depart_utc)
   self.assertEqual(f.schedule_status,'synthetic')
 def test_local_times_physically_correct_november(self):
  a=next(f for f in self.flights if f.id=='S01-20261103')
  self.assertEqual(a.depart_utc.hour,9) # London is GMT in November
  self.assertEqual(a.arrive_utc.hour,17) # New York is EST in November
  self.assertEqual(int((a.arrive_utc-a.depart_utc).total_seconds()/60),495)
 def test_dst_transition_applies_different_rules(self):
  london=localized(date(2026,10,25),'01:30','LHR')
  # The day British daylight time ends; check offset changes by next day.
  self.assertEqual(localized(date(2026,10,24),'12:00','LHR').utcoffset().total_seconds(),3600)
  self.assertEqual(localized(date(2026,10,26),'12:00','LHR').utcoffset().total_seconds(),0)
  self.assertEqual(localized(date(2026,10,31),'12:00','JFK').utcoffset().total_seconds(),-4*3600)
  self.assertEqual(localized(date(2026,11,2),'12:00','JFK').utcoffset().total_seconds(),-5*3600)
 def test_no_backwards_connections(self):
  found=enumerate_itineraries(self.flights,'LHR','MIA',carriers={'AX','DX','CX','BX'},max_connections=2,buffer_minutes=15)
  self.assertTrue(found)
  for row in found:
   self.assertEqual(row['flights'][0]['origin'],'LHR')
   self.assertEqual(row['flights'][-1]['destination'],'MIA')
   self.assertLessEqual(len(row['flights']),3)
   legs=row['flights']
   for a,b in zip(legs,legs[1:]):
    self.assertGreaterEqual(datetime.fromisoformat(b['depart_utc'].replace('Z','+00:00'))-datetime.fromisoformat(a['arrive_utc'].replace('Z','+00:00')),
                            timedelta(minutes=MCT_MINUTES.get(a['destination'],75)+15))
 def test_network_expands_with_partner_labels(self):
  vs=enumerate_itineraries(self.flights,'LHR','MIA',{'AX'},buffer_minutes=15)
  alli=enumerate_itineraries(self.flights,'LHR','MIA',{'AX','CX','DX','BX'},buffer_minutes=15)
  self.assertEqual(len(vs),0)
  self.assertGreater(len(alli),0)
 def test_three_segment_paths_exist(self):
  routes=enumerate_itineraries(self.flights,'LHR','RDU',{'AX','BX','CX','DX'},buffer_minutes=10,max_connections=2,limit=100)
  self.assertTrue(any(len(x['flights'])==3 for x in routes))
 def test_airport_great_circle_distance(self):
  self.assertTrue(5400<haversine_km('LHR','JFK')<5800)
  self.assertEqual(haversine_km('LHR','LHR'),0)
 def test_reject_invalid_constraints(self):
  with self.assertRaises(ValueError): enumerate_itineraries(self.flights,'LHR','JFK',max_connections=8)
  with self.assertRaises(ValueError): generate_scenario(days=40)
 def test_pareto_dominance(self):
  arr=[dict(flights=[1,2],duration_minutes=100,assumed_trip_completion_probability=.9),
       dict(flights=[1,2],duration_minutes=125,assumed_trip_completion_probability=.8),
       dict(flights=[1],duration_minutes=130,assumed_trip_completion_probability=.7)]
  out=pareto_frontier(arr)
  self.assertEqual(len(out),2)

class EconomicsTests(unittest.TestCase):
 def test_capped_load_factor_and_spill(self):
  x=Inputs(total_market_passengers=1000000,assumed_capture_pct=40,
           annual_departures=100,seats_per_departure=200,net_fare_gbp=500,
           cost_per_departure_gbp=10000,variable_cost_per_passenger_gbp=100,annual_fixed_cost_gbp=0)
  r=economics(x)
  self.assertEqual(r['carried_passengers'],20000)
  self.assertEqual(r['unserved_demand'],380000)
  self.assertEqual(r['load_factor'],1)
 def test_breakeven_exact(self):
  r=economics(Inputs(total_market_passengers=10000,assumed_capture_pct=50,
     annual_departures=100,seats_per_departure=100,net_fare_gbp=200,
     cost_per_departure_gbp=1000,variable_cost_per_passenger_gbp=100,annual_fixed_cost_gbp=0))
  self.assertEqual(r['breakeven_passengers'],1000)
  self.assertAlmostEqual(r['breakeven_load_factor'],.1)
 def test_infeasible_breakeven(self):
  r=economics(Inputs(total_market_passengers=100000,net_fare_gbp=100,
       variable_cost_per_passenger_gbp=100))
  self.assertFalse(r['breakeven_feasible'])
 def test_reject_invalid_inputs(self):
  for inp in [Inputs(total_market_passengers=-1),Inputs(total_market_passengers=100,assumed_capture_pct=101),Inputs(total_market_passengers=100,annual_departures=0)]:
   with self.assertRaises(ValueError):economics(inp)
 def test_monte_carlo_reproducible_and_ordered(self):
  x=Inputs(total_market_passengers=1000000)
  a=simulate(x,draws=500,seed=2026);b=simulate(x,draws=500,seed=2026)
  self.assertEqual(a,b)
  self.assertLessEqual(a['contribution_p05_gbp'],a['contribution_p50_gbp'])
  self.assertLessEqual(a['contribution_p50_gbp'],a['contribution_p95_gbp'])

class BTSImporterTests(unittest.TestCase):
 def test_authenticated_shape_and_aggregation(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'bts.csv'
   f.write_text('YEAR,MONTH,ORIGIN,DEST,UNIQUE_CARRIER,PASSENGERS,SEATS,DEPARTURES_PERFORMED\n2025,1,LHR,JFK,AA,90,100,1\n2025,1,JFK,LHR,AA,70,100,1\n2025,2,ORD,LAX,AA,50,100,1\n')
   rows=import_bts(f)
   self.assertEqual(len(rows),1)
   self.assertEqual(rows[0]['seat_load_factor'],.8)
   self.assertEqual(rows[0]['departures'],2)
 def test_inconsistent_seats_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'bts.csv'
   f.write_text('YEAR,MONTH,ORIGIN,DEST,UNIQUE_CARRIER,PASSENGERS,SEATS,DEPARTURES_PERFORMED\n2025,1,LHR,JFK,AA,105,100,1\n')
   with self.assertRaisesRegex(ValueError,'passengers exceed seats'):import_bts(f)
 def test_missing_required_columns_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'bts.csv';f.write_text('ORIGIN,DEST\nLHR,JFK\n')
   with self.assertRaisesRegex(ValueError,'missing required'):import_bts(f)

if __name__=='__main__':unittest.main()
