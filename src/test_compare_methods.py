import unittest
from compare_methods import load_rows, repeat_workload,baseline,proposed,baseline_reference
from benchmark_statistics import aggregate,bootstrap_median_ci

class CompareMethodsTest(unittest.TestCase):
    def test_methods_identical_at_all_loads(self):
        rows=load_rows()
        for factor in (1,2,4,8):
            workload=repeat_workload(rows,factor)
            self.assertEqual(baseline(workload),proposed(workload))
            self.assertEqual(proposed(workload),baseline_reference(workload))
            self.assertEqual(sum(x['n'] for x in proposed(workload).values()),45*factor)
    def test_filter_and_ci(self):
        entries=[{'method':'baseline','load_records':45,'phase':'warmup','success':True,'latency_ms':100},
                 {'method':'baseline','load_records':45,'phase':'benchmark','success':True,'latency_ms':1},
                 {'method':'baseline','load_records':45,'phase':'benchmark','success':False,'latency_ms':2},
                 {'method':'baseline','load_records':45,'phase':'benchmark','success':True,'latency_ms':3}]
        result=aggregate(entries)[0]
        self.assertEqual(result['warmup_runs_excluded'],1)
        self.assertEqual(result['median_ms'],2)
        self.assertAlmostEqual(result['error_rate'],1/3,places=5)
    def test_bootstrap_fixed(self):
        self.assertEqual(bootstrap_median_ci([1,2,3,4,5]),bootstrap_median_ci([1,2,3,4,5]))
if __name__=='__main__':unittest.main()
