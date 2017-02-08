from unittest import TestCase
from optimizer.optimizer import MemoryOptimizer

class MemoryOptimizerTest(TestCase):
    def test_service(self):
        optimizer = MemoryOptimizer()
        test_cases = {
            # utilization, current hard/soft limit, recommended hard/soft limit
            ('small 90% reserved', 90.0, 80, 64, 80, 64),
            ('small 110% reserved', 110.0, 80, 64, 80, 64),
            ('small 113% reserved (under)', 113.0, 80, 64, 128, 96),
            ('small 75% reserved (over)', 75.0, 80, 64, 64, 48),
            ('tiny 25% reserved (over)', 25.0, 128, 64, 20, 16),
            ('large 200% reserved (under)', 200.0, 1280, 1024, 2560, 2048),
        }

        for test_case in test_cases:
            msg, utilization, current_hard_limit, current_soft_limit, expected_hard_limit, expected_soft_limit = test_case
            peak, new_hard_limit, new_soft_limit = optimizer.recommend(utilization, current_hard_limit, current_soft_limit)

            self.assertEquals(expected_soft_limit, new_soft_limit, 'soft limit %s != %s %s' % (expected_soft_limit, new_soft_limit, msg))
            self.assertEquals(expected_hard_limit, new_hard_limit, 'hard limit %s != %s %s' % (expected_hard_limit, new_hard_limit, msg))
