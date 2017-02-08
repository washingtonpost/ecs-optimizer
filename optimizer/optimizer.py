class MemoryOptimizer(object):
    def optimize(self, ecs, cloudwatch, cluster, service, start_date, end_date, over_reserve, under_reserve):
        utilization = cloudwatch.max_memory_utilization(cluster, service, start_date, end_date)
        if utilization <= 0.0:
            return

        hard_limit, soft_limit = ecs.service_memory_reservation(cluster, service)
        peak_memory = soft_limit*(utilization/100.0)
        low_memory = peak_memory * (1.0 - under_reserve)
        high_memory = peak_memory * (1.0 + over_reserve)

        if low_memory > soft_limit or high_memory < soft_limit:
            new_hard_limit, new_soft_limit = self.recommend(low_memory)
            # only make recommendation on new soft_limit because reserved memory is the only cost driver
            if new_soft_limit != soft_limit:
                print "%s used %dMB with hard/soft limit of %dMB/%dMB. Recommended new hard/soft limit of %dMB/%dMB." % \
                    (service, peak_memory, hard_limit, soft_limit, new_hard_limit, new_soft_limit)

    def recommend(self, memory):
        memory_chunk = 4 # 4MB is the min memory chunk
        prev_memory_chunk = memory_chunk
        soft_limit = 0
        hard_limit = 0

        while (memory_chunk * 4) < memory:
            prev_memory_chunk = memory_chunk
            memory_chunk *= 2

        while soft_limit < memory:
            soft_limit += memory_chunk

        # hard limit is at least 25% greater than the soft limit
        while hard_limit < (soft_limit * 1.25):
            hard_limit += memory_chunk

        return hard_limit, soft_limit

