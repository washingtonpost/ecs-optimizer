class ServiceOptimizer(object):
    def __init__(self, ecs, cloudwatch):
        self.ecs = ecs
        self.cloudwatch = cloudwatch

    def optimize(self, verbose, cluster, service, start_date, end_date, cpu_over_reserve, cpu_under_reserve,
                 mem_hard_over_reserve, mem_soft_over_reserve, mem_soft_under_reserve):
        mem_utilization = self.cloudwatch.max_memory_utilization(cluster, service, start_date, end_date)
        cpu_utilization = self.cloudwatch.avg_cpu_utilization(cluster, service, start_date, end_date)
        cpu_shares, mem_hard_limit, mem_soft_limit = self.ecs.service_reservations(cluster, service)
        instance_cpu_capacity, instance_mem_capacity = self.ecs.instance_capacity(cluster)
        new_cpu_shares = self.recommend_cpu(cpu_utilization, instance_cpu_capacity, cpu_shares, cpu_over_reserve, cpu_under_reserve)
        new_mem_hard_limit, new_mem_soft_limit = self.recommend_memory(mem_utilization, mem_hard_limit, mem_soft_limit, mem_hard_over_reserve,
                                                                       mem_soft_over_reserve, mem_soft_under_reserve)

        recommendations = []
        if new_mem_soft_limit != mem_soft_limit or verbose:
            # only make recommendation on new soft_limit not hard_limit since the soft_limit reserves memory, but hard_limit does not
            recommendations.append("change memory hard/soft limit from %dMB/%dMB to %dMB/%dMB" % \
                    (mem_hard_limit, mem_soft_limit, new_mem_hard_limit, new_mem_soft_limit))

        if new_cpu_shares != cpu_shares or verbose:
            recommendations.append("change CPU shares from %d to %d" % (cpu_shares, new_cpu_shares))

        if len(recommendations):
            print "%s: %s." % (service, ", ".join(recommendations))

    def recommend_memory(self, utilization, hard_limit, soft_limit, hard_over_reserve, soft_over_reserve, soft_under_reserve):
        memory = soft_limit*(utilization/100.0)
        new_soft_limit = self.calc_memory_limit(memory)
        new_hard_limit = self.calc_memory_limit(memory * (1.0 + hard_over_reserve))

        hard_limit = self.optimal_limit(memory, hard_limit, new_hard_limit, hard_over_reserve)
        soft_limit = self.optimal_limit(memory, soft_limit, new_soft_limit, soft_over_reserve, soft_under_reserve)

        if hard_limit < soft_limit:
            hard_limit = soft_limit

        return hard_limit, soft_limit

    def recommend_cpu(self, utilization, instance_cpu_capacity, cpu_shares, over_reserve, under_reserve):
        new_cpu_shares = int(round((utilization/100.0) * instance_cpu_capacity))
        if new_cpu_shares < 16:
            new_cpu_shares = 0

        return self.optimal_limit(new_cpu_shares, cpu_shares, new_cpu_shares, over_reserve, under_reserve)

    def optimal_limit(self, curr_value, old_limit, new_limit, over_reserve, under_reserve=0):
        lower_limit = curr_value * (1.0 - under_reserve)
        upper_limit = curr_value * (1.0 + over_reserve)
        if old_limit < lower_limit or old_limit > upper_limit:
            return new_limit
        else:
            return old_limit

    def calc_memory_chunk_size(self, memory):
        # 4MB is the smallest memory chunk
        memory_chunk = 4

        while (memory_chunk * 16) < memory:
            memory_chunk *= 2

        return memory_chunk

    def calc_memory_limit(self, memory):
        memory_chunk = self.calc_memory_chunk_size(memory)
        new_limit = 0
        while new_limit < memory:
            new_limit += memory_chunk

        return new_limit

