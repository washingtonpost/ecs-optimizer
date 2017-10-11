class ServiceOptimizer(object):
    def __init__(self, ecs, cloudwatch):
        self.ecs = ecs
        self.cloudwatch = cloudwatch

    def optimize(self, verbose, cluster, service, start_date, end_date, cpu_over_reserve, cpu_under_reserve, mem_over_reserve, recommend_limit_decrease):
        mem_utilization = self.cloudwatch.max_memory_utilization(cluster, service, start_date, end_date)
        cpu_utilization = self.cloudwatch.avg_cpu_utilization(cluster, service, start_date, end_date)
        cpu_shares, mem_hard_limit, mem_soft_limit = self.ecs.service_reservations(cluster, service)
        instance_cpu_capacity, instance_mem_capacity = self.ecs.instance_capacity(cluster)
        new_cpu_shares = self.recommend_cpu(cpu_utilization, instance_cpu_capacity, cpu_shares, cpu_over_reserve, cpu_under_reserve,
                                            recommend_limit_decrease)
        new_mem_limit = self.recommend_memory(mem_utilization, mem_hard_limit, mem_soft_limit, mem_over_reserve, recommend_limit_decrease)

        recommendations = []
        if new_mem_limit != mem_soft_limit or verbose:
            recommendations.append("change memory hard/soft limit from %dMB to %dMB" % (mem_soft_limit, new_mem_limit))

        if new_cpu_shares != cpu_shares or verbose:
            recommendations.append("change CPU shares from %d to %d" % (cpu_shares, new_cpu_shares))

        if len(recommendations):
            print "%s: %s." % (service, ", ".join(recommendations))

    def recommend_memory(self, utilization, old_hard_limit, old_soft_limit, over_reserve, recommend_limit_decrease=True):
        memory = old_soft_limit*(utilization/100.0)
        new_limit = self.calc_memory_limit(memory * (1.0 + over_reserve))

        return self.optimal_limit(memory, old_soft_limit, new_limit, over_reserve, 0, recommend_limit_decrease)

    def recommend_cpu(self, utilization, instance_cpu_capacity, cpu_shares, over_reserve, under_reserve, recommend_limit_decrease=True):
        new_cpu_shares = int(round((utilization/100.0) * instance_cpu_capacity))
        if new_cpu_shares < 16:
            new_cpu_shares = 0

        return self.optimal_limit(new_cpu_shares, cpu_shares, new_cpu_shares, over_reserve, under_reserve, recommend_limit_decrease)

    def optimal_limit(self, curr_value, old_limit, new_limit, over_reserve, under_reserve, recommend_limit_decrease):
        lower_limit = curr_value * (1.0 - under_reserve)
        upper_limit = curr_value * (1.0 + over_reserve)
        if old_limit < lower_limit or (recommend_limit_decrease and old_limit > upper_limit):
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

