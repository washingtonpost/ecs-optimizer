class MemoryOptimizer(object):
    def optimize(self, ecs, cloudwatch, cluster, service, start_date, end_date, over_reserve, under_reserve):
        max_memory_utilization = cloudwatch.max_memory_utilization(cluster, service, start_date, end_date)
        if max_memory_utilization <= 0.0:
            return

        hard_limit, soft_limit = ecs.service_memory_reservation(cluster, service)
        peak_memory, new_hard_limit, new_soft_limit = self.recommend(max_memory_utilization, hard_limit, soft_limit, under_reserve)

        if new_soft_limit != soft_limit:
            print "%s used %dMB out of %dMB reserved memory. Recommended new hard/soft limit of %dMB/%dMB." % \
                (service, peak_memory, soft_limit, new_hard_limit, new_soft_limit)

    def recommend(self, utilization, hard_limit, soft_limit, under_reserve=0.1):
        peak = soft_limit*(utilization/100.0)
        new_hard_limit, new_soft_limit = self._calculate_memory_chunk(peak, under_reserve)

        return int(peak), int(new_hard_limit), int(new_soft_limit)

    def _calculate_memory_chunk(self, memory, under_reserve):
        memory_chunk = 4 # 4MB is the min memory chunk
        prev_memory_chunk = memory_chunk
        soft_limit = 0
        hard_limit = 0
        low_memory = memory * (1.0 - under_reserve)

        while (memory_chunk * 4) < low_memory:
            prev_memory_chunk = memory_chunk
            memory_chunk *= 2

        while soft_limit < low_memory:
            soft_limit += memory_chunk

        # hard limit is at least 25% greater than the soft limit
        while hard_limit < (soft_limit * 1.25):
            hard_limit += memory_chunk

        return hard_limit, soft_limit

