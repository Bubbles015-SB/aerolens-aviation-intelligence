import tempfile,unittest
from pathlib import Path
from aerolens.operations import import_schedule,connection_reliability
FIELDS='flight_id,carrier,origin,destination,departure_local,arrival_local\n'
LINE1='AA001,AA,LHR,JFK,2026-11-04T09:00:00+00:00,2026-11-04T12:10:00-05:00\n'
LINE2='AA002,AA,JFK,MIA,2026-11-04T14:30:00-05:00,2026-11-04T18:00:00-05:00\n'
class TestOps(unittest.TestCase):
    def load(self,txt):
        with tempfile.TemporaryDirectory() as t:
            file=Path(t)/'input.csv';file.write_text(FIELDS+txt)
            return import_schedule(file,'Operator supplied sample schedule, provenance: synthetic test')
    def test_valid(self):
        x=self.load(LINE1+LINE2);self.assertEqual(len(x['flights']),2)
        result=connection_reliability(x['flights'],draws=150,seed=3)
        self.assertGreater(result['assumed_completion_rate'],.5)
        self.assertEqual(result,connection_reliability(x['flights'],draws=150,seed=3))
    def test_bad_tz_offset(self):
        with self.assertRaises(ValueError):self.load(LINE1.replace('09:00:00+00:00','09:00:00+01:00'))
    def test_duplicates(self):
        with self.assertRaises(ValueError):self.load(LINE1+LINE1)
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as t:
            file=Path(t)/'in.csv';file.write_text(FIELDS+LINE1)
            with self.assertRaises(ValueError):import_schedule(file,'bad')
    def test_noncontiguous(self):
        x=self.load(LINE1+LINE2)
        with self.assertRaises(ValueError):connection_reliability(x['flights'][::-1],draws=100)

if __name__=='__main__':unittest.main()
