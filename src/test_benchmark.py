import unittest
from benchmark import age_group
class AgeGroupTests(unittest.TestCase):
    def test_age_boundaries(self):
        for age, expected in [(18,"18-30"),(30,"18-30"),(31,"31-50"),(50,"31-50"),(51,"51+"),(85,"51+")]:
            self.assertEqual(age_group(age),expected)
    def test_underage_rejected(self):
        with self.assertRaises(ValueError): age_group(17)
if __name__ == "__main__": unittest.main()
