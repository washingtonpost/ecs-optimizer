from unittest import TestCase
from optimizer.optimizer import MemoryOptimizer

class MemoryOptimizerTest(TestCase):
    def test_service(self):
        optimizer = MemoryOptimizer()
        test_cases = {
            # utilization, current hard/soft limit, recommended hard/soft limit
            ('16MB', 16.0, 20, 16),
            ('48MB', 48.0, 64, 48),
            ('57.6MB', 57.6, 80, 64),
            ('72MB', 72.0, 128, 96),
            ('2048MB', 2048.0, 2560, 2048),
        }

        for test_case in test_cases:
            msg, memory, expected_hard_limit, expected_soft_limit = test_case
            new_hard_limit, new_soft_limit = optimizer.recommend(memory)

            self.assertEquals(expected_soft_limit, new_soft_limit, 'soft limit %s != %s %s' % (expected_soft_limit, new_soft_limit, msg))
            self.assertEquals(expected_hard_limit, new_hard_limit, 'hard limit %s != %s %s' % (expected_hard_limit, new_hard_limit, msg))
