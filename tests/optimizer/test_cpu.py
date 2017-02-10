from unittest import TestCase
from optimizer.optimizer import CPUOptimizer

class CPUOptimizerTest(TestCase):
    def test_service(self):
        optimizer = CPUOptimizer(None, None)
        test_cases = {
            ('low cpu', 5.0, 4096, 0, 205),
            ('very low cpu', 0.4, 4096, 0, 16),
            ('extremely low cpu', 0.3, 4096, 0, 0),
            ('no cpu', 0.0, 4096, 0, 0),
            ('extremely high cpu', 100.0, 4096, 0, 4096),
            ('small over reserved', 5.0, 1024, 55, 55),
            ('small under reserved', 5.0, 1024, 46, 46),
        }

        for test_case in test_cases:
            msg, utilization, server_cpu_shares, current_cpu_shares, expected_cpu_shares = test_case
            new_cpu_shares = optimizer.recommend(utilization, server_cpu_shares, current_cpu_shares)

            self.assertEquals(expected_cpu_shares, new_cpu_shares, 'cpu shares %s != %s %s' % (expected_cpu_shares, new_cpu_shares, msg))
