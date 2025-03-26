class WCET_AdaptiveAgent:
    def __init__(self, min_wcet=1.0, max_wcet=10.0):
        self.min_wcet = min_wcet
        self.max_wcet = max_wcet
        self.task_policies = {}

    def get_task_policy(self, task):
        if task.id not in self.task_policies:
            self.task_policies[task.id] = task.wcet[CriticalityLevel.LOW]
        return self.task_policies[task.id]

    def adapt_wcet(self, task, execution_history, deadline_miss):
        current_wcet = self.get_task_policy(task)
        avg_execution_time = np.mean(execution_history) if execution_history else current_wcet
        if deadline_miss:
            new_wcet = min(current_wcet * 1.1, self.max_wcet)
        else:
            new_wcet = max(avg_execution_time * 0.9, self.min_wcet)
        self.task_policies[task.id] = new_wcet
        return new_wcet