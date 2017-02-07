class MemoryOptimizer(object):
    def __init__(self):
        self.min_memory_unit = 64 # 64MB before recommending any changes

    def optimize(self, ecs, cloudwatch, cluster, service, start_date, end_date, oversubscribe, undersubscribe):
        max_memory_utilization = cloudwatch.max_memory_utilization(cluster, service, start_date, end_date)
        if max_memory_utilization <= 0.0:
            return

        hard_limit, soft_limit = ecs.service_memory_reservation(cluster, service)
        peak_memory, new_hard_limit, new_soft_limit = self.recommend(max_memory_utilization, hard_limit, soft_limit)

        if abs(new_soft_limit - soft_limit) > self.min_memory_unit or abs(new_soft_limit - soft_limit) > self.min_memory_unit:
            print "%s used %dMB out of %dMB reserved memory. New soft limit should be %dMB and hard limit should be %dMB." % \
                (service, peak_memory, soft_limit, new_soft_limit, new_hard_limit)

    def recommend(self, max_memory_utilization, hard_limit, soft_limit):
        peak_memory = soft_limit*(max_memory_utilization/100.0)
        new_soft_limit = 0.0
        new_hard_limit = 0.0
        while new_soft_limit < peak_memory:
            new_soft_limit += self.min_memory_unit

        new_hard_limit = new_soft_limit + self.min_memory_unit

        return peak_memory, new_hard_limit, new_soft_limit
