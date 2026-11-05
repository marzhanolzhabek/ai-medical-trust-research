import unittest, tempfile,csv
from pathlib import Path
from process_data import age_group, analyze
class TestAgeGroups(unittest.TestCase):
 def test_boundaries(self):
  self.assertEqual([age_group(x) for x in [17,18,30,31,50,51,75]],[None,'18-30','18-30','31-50','31-50','51+','51+'])
 def test_real_demo(self):
  result=analyze(Path(__file__).resolve().parents[1]/'data/sample/sample_synthetic.csv')
  self.assertEqual([s['n'] for s in result['summary']],[15,15,15])
  self.assertEqual(result['invalid'],0)
if __name__=='__main__':unittest.main()
