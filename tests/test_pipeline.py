"""Run using python -m unittest discover -s tests -v (no third-party libraries)."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('aerolens_builder',ROOT/'scripts/build_data.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RoutePipelineTests(unittest.TestCase):
    def setUp(self):
        self.routes=mod.load_routes()
        self.summary=mod.summary(self.routes)

    def test_expected_coverage(self):
        self.assertEqual(len(self.routes),28)
        self.assertEqual(len(set(r['code'] for r in self.routes)),28)

    def test_source_spot_checks(self):
        """Hand-verified rows from official CAA PDF p.89 (0-index)."""
        lookup={r['code']:r for r in self.routes}
        self.assertEqual((lookup['JFK']['y2024'],lookup['JFK']['y2025']),(3238557,3220238))
        self.assertEqual((lookup['LAX']['y2024'],lookup['LAX']['y2025']),(1679883,1459443))
        self.assertEqual((lookup['ATL']['y2024'],lookup['ATL']['y2025']),(739622,790122))
        self.assertEqual((lookup['BOS']['y2024'],lookup['BOS']['y2025']),(1071220,1105185))

    def test_change_math(self):
        for r in self.routes:
            self.assertEqual(r['delta'],r['y2025']-r['y2024'])
            self.assertAlmostEqual(r['growth_pct'],100*(r['y2025']/r['y2024']-1),places=3)

    def test_summary_reconciles(self):
        self.assertEqual(self.summary['pax_2024'],sum(r['y2024'] for r in self.routes))
        self.assertEqual(self.summary['pax_2025'],sum(r['y2025'] for r in self.routes))
        self.assertEqual(self.summary['growing_routes']+self.summary['declining_routes'],28)

    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.csv'
            with mod.RAW.open(newline='',encoding='utf-8') as source:
                records=list(csv.reader(source))
            records.append(records[1])
            with p.open('w',newline='',encoding='utf-8') as f:
                csv.writer(f).writerows(records)
            with self.assertRaisesRegex(ValueError,'Duplicate route'):
                mod.load_routes(p)

    def test_negative_passengers_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.csv'
            with mod.RAW.open(newline='',encoding='utf-8') as source:
                records=list(csv.reader(source))
            records[1][3]='-1'
            with p.open('w',newline='',encoding='utf-8') as f:
                csv.writer(f).writerows(records)
            with self.assertRaisesRegex(ValueError,'Nonpositive'):
                mod.load_routes(p)

if __name__=='__main__': unittest.main()
