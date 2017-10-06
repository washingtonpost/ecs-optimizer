# ecs-optimizer
Optimizer your ECS cluster by learned the correct CPU and memory limits for your tasks and implementing autoscaling that keeps enough capacity in your cluster to continue launching more containers.

```sh
pip install ecs-optimizer
ecs-optimizer "cluster name"
```

This command will output an tasks that need limit adjustments to be optimal. You can ignore limits that are too high and only report on limits that are too low with the option --ignore-high-limits.

It will also output the overall cluster utilization. By default it looks at your CloudWatch metrics over the last 7 days. You can change that time window by using the --analyze-duration option.

## Architecture
There are two main packages. The cli package provides a helpful command line interface for checking your cluster and tasks manually. The lib package contains all the logic for doing the retrieval and calculations so that you can emmbed the code in a Lambda function that auto-scales your cluster or makes suggestions on a Slack channel for changing limits. You can also use the lib package to build a metrics report to track the overal utilization and limit trends in your ECS environment for tracking your cost effeciency over time.

## Metrics
* cluster_cpu_utilization_reserved - a ratio of the cpu capacity reserved on the cluster by tasks divided by the total cluster capacity
* cluster_memory_utilization_reserved - a ratio of the memory capacity reserved on the cluster by tasks divided by the total cluster capacity
* cluster_cpu_utilization - a ratio of the cpu capacity used on the cluster by tasks divided by the total cluster capacity
* cluster_memory_utilization - a ratio of the memory capacity used on the cluster by tasks divided by the total cluster capacity 
* task_cpu_utilization - a ratio of the cpu capacity used vs reserved by the task 
* task_memory_utilization - a ratio of the memory capacity used vs reserved by the task

TODO is the metric by task or by service where all the task definitions are added up?

Each metric has average, min and max values over the time range.
