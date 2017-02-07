from unittest import TestCase
from optimizer.optimizer import MemoryOptimizer

class MemoryOptimizerTest(TestCase):
    def test_small_service(self):
        optimizer = MemoryOptimizer()
        peak_memory, hard_limit, soft_limit = optimizer.recommend(10.0, 256, 128)
        self.assertEquals(128, hard_limit)
        self.assertEquals(64, soft_limit)

