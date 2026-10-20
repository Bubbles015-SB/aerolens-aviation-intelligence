import unittest
from scripts.validate_powerbi import run

class PowerBIProjectTests(unittest.TestCase):
    def test_semantic_bindings_and_structure(self):self.assertTrue(run())

if __name__=='__main__':unittest.main()
