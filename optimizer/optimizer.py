class MemoryOptimizer(object):
    def __init__(self, ecs, cloudwatch):
        self.ecs = ecs
        self.cloudwatch = cloudwatch
        self.min_memory_unit = 64 # 64MB before recommending any changes

    def optimize(self, cluster, service, start_date, end_date, oversubscribe, undersubscribe):
        max_memory_utilization = self.cloudwatch.max_memory_utilization(cluster, service, start_date, end_date)
        if max_memory_utilization <= 0.0:
            return

        hard_limit, soft_limit = self.ecs.service_memory_reservation(cluster, service)
        direction = None
        if (max_memory_utilization - (oversubscribe * 100.0)) > 100.0:
            direction = 'oversubscribed'

        if (max_memory_utilization + (undersubscribe * 100.0)) < 100.0:
            direction = 'undersubscribed'

        peak_memory = soft_limit*(max_memory_utilization/100.0)
        recommended_limit = self._recommended_limit(peak_memory)

        if direction and abs(recommended_limit - soft_limit) > self.min_memory_unit:
            print "%s is %s because peak usage was %dMB but %dMB was reserved. Recommended soft limit of %dMB and hard limit greater than %dMB." % \
                (service, direction, peak_memory, soft_limit, recommended_limit, recommended_limit)


    def _recommended_limit(self, peak_memory):
        recommendation = 0.0
        while recommendation < peak_memory:
            recommendation += self.min_memory_unit

        return recommendation
