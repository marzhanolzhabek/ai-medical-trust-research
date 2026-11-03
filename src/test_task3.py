import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from process_data import aggregate, bootstrap_ci, read_measurements

class Task3Tests(unittest.TestCase):
    def test_bootstrap_reproducible(self):
        self.assertEqual(bootstrap_ci([1,2,3,4],seed=42,replicates=100),bootstrap_ci([1,2,3,4],seed=42,replicates=100))
    def test_warmup_removed_and_error_tracked(self):
        rows=[{'phase':'warmup','status':'ok','latency_us':9000,'calculations_per_measurement':1},
              {'phase':'evaluation','status':'ok','latency_us':10,'calculations_per_measurement':1},
              {'phase':'evaluation','status':'error','latency_us':20,'calculations_per_measurement':1}]
        s=aggregate(rows,source='test',warmup_runs=1,replicates=50)
        self.assertEqual(s['median_latency_us'],10)
        self.assertEqual(s['error_rate'],0.5)
    def test_real_log(self):
        root=Path(__file__).resolve().parent.parent
        self.assertEqual(len(read_measurements(root/'data/raw/test_run.jsonl')),120)
