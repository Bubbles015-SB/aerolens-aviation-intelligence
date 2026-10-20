import unittest, tempfile, pathlib
from datetime import date
from aerolens.portfolio import RouteOption,outcome,optimise,stress_portfolio
from aerolens.sustainability import great_circle_km,flight_emission_scenario
from aerolens.assurance import Evidence,audit
from aerolens.forecasting import read_monthly_csv,evaluate_and_forecast

class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.routes=[RouteOption('JFK',480,120,200,9000,20,7,18,6),RouteOption('BOS',300,100,180,7000,20,6,15,6)]
    def test_solution_optimized(self):
        got=optimise(self.routes,75,160)
        self.assertTrue(got['feasible']); self.assertLessEqual(got['hours_used'],75)
        self.assertLessEqual(got['emissions_used_t'],160)
        # brute force oracle
        options=[]
        for a in range(7):
            for b in range(7):
                x=outcome(self.routes[0],a);y=outcome(self.routes[1],b)
                if x['hours']+y['hours']<=75 and x['emissions_t']+y['emissions_t']<=160:
                    options.append(x['contribution_gbp']+y['contribution_gbp'])
        self.assertAlmostEqual(got['contribution_gbp'],max(options),places=2)
    def test_zero_budget(self):self.assertEqual(optimise(self.routes,0)['hours_used'],0)
    def test_infeasible_minimum(self):
        r=RouteOption('LAX',200,120,100,100,1,9,24,6,min_weekly_flights=3)
        self.assertFalse(optimise([r],20)['feasible'])
    def test_duplicate(self):
        with self.assertRaises(ValueError):optimise(self.routes+self.routes[:1],80)
    def test_determinism(self):
        a=stress_portfolio(self.routes,90,draws=25,seed=1)
        self.assertEqual(a,stress_portfolio(self.routes,90,draws=25,seed=1))
    def test_spill(self):self.assertEqual(outcome(self.routes[0],1)['spill'],360)

class SustainabilityTests(unittest.TestCase):
    def test_zero_distance(self):self.assertAlmostEqual(great_circle_km(51,-.4,51,-.4),0)
    def test_reference_earth(self):self.assertTrue(5400<great_circle_km(51.47,-.45,40.64,-73.78)<5700)
    def test_emissions(self):
        x=flight_emission_scenario(5500,5,250,.8,5400,7)
        self.assertAlmostEqual(x['estimated_co2_t'],5*5400*7*3.16/1000,places=2)
    def test_bad_coords(self):
        with self.assertRaises(ValueError):great_circle_km(100,0,0,0)

class AssuranceTests(unittest.TestCase):
    def test_blocked_revision(self):
        a=audit([Evidence('R1','Check material report',3,2,True,date(2026,9,1),'doc://r1','critical')],date(2026,10,19))
        self.assertEqual(a['critical_blocked'],1);self.assertEqual(a['release_gate'],'REVIEW_REQUIRED')
    def test_ready(self):
        a=audit([Evidence('R1','Doc',1,1,True,date(2026,9,1),'doc://r1')],date(2026,10,19))
        self.assertEqual(a['release_gate'],'EVIDENCE_READY')
    def test_duplicate(self):
        e=Evidence('R1','Doc',1,1,True,date(2026,9,1),'doc://r1')
        with self.assertRaises(ValueError):audit([e,e],date(2026,10,19))

class ForecastTests(unittest.TestCase):
    def test_leak_free_forecast(self):
        rows=[]
        for n in range(42):rows.append((f'{2022+n//12:04d}-{n%12+1:02d}',100+n%12+3*(n//12)))
        x=evaluate_and_forecast(rows,6)
        self.assertEqual(len(x['horizon']),6)
        self.assertGreater(x['backtest_months'],0)
        self.assertEqual(x['horizon'][0]['month'],'2025-07')
    def test_short_rejected(self):
        with self.assertRaises(ValueError):evaluate_and_forecast([('2025-01',1)])
    def test_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'monthly.csv'
            p.write_text('month,passengers\n'+''.join(f'{2022+i//12:04d}-{i%12+1:02d},100\n' for i in range(35)))
            self.assertEqual(len(read_monthly_csv(p)),35)
            p.write_text('month,passengers\n2025-01,-1\n')
            with self.assertRaises(ValueError):read_monthly_csv(p)

if __name__=='__main__':unittest.main()
