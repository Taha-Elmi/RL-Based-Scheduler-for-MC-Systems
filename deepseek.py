import heapq
from typing import List, Tuple


# Task structure
class Task:
    def __init__(self, task_id: int, period: int, deadline: int, execution_time: float, criticality: str):
        self.task_id = task_id
        self.period = period
        self.deadline = deadline
        self.execution_time = execution_time
        self.criticality = criticality  # 'low' or 'high'
        self.virtual_deadline = deadline  # Virtual deadline for EDF-VD

    def __lt__(self, other):
        # Compare tasks based on virtual deadlines for EDF
        return self.virtual_deadline < other.virtual_deadline

    def __repr__(self):
        return f"Task(ID={self.task_id}, Period={self.period}, Deadline={self.deadline}, Exec={self.execution_time}, Crit={self.criticality}, VD={self.virtual_deadline})"


# EDF-VD Scheduler
class EDFVDScheduler:
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
        self.time = 0
        self.system_mode = 'low'  # Start in low-criticality mode

    def update_virtual_deadlines(self):
        # Adjust virtual deadlines for high-criticality tasks
        for task in self.tasks:
            if task.criticality == 'high':
                if self.system_mode == 'low':
                    task.virtual_deadline = task.deadline * 0.75  # Example scaling factor
                else:
                    task.virtual_deadline = task.deadline

    def schedule(self):
        # Main scheduling loop
        while self.time < 100:  # Simulate for 100 time units
            self.update_virtual_deadlines()

            # Get ready tasks (tasks whose period has arrived)
            ready_tasks = [task for task in self.tasks if self.time % task.period == 0]

            if ready_tasks:
                # Use a priority queue (heap) to sort tasks by virtual deadline
                heapq.heapify(ready_tasks)
                next_task = heapq.heappop(ready_tasks)

                print(f"Time {self.time}: Executing Task {next_task.task_id}")

                # Simulate task execution
                self.time += next_task.execution_time

                # Check for mode change (e.g., if a high-criticality task misses its deadline)
                if next_task.criticality == 'high' and self.time > next_task.deadline:
                    print(f"High-criticality task {next_task.task_id} missed deadline. Switching to high-criticality mode.")
                    self.system_mode = 'high'
            else:
                # Idle time
                self.time += 1


# Example usage
if __name__ == "__main__":
    # Define tasks
    tasks = [
        Task(task_id=1, period=10, deadline=10, execution_time=2, criticality='low'),
        Task(task_id=2, period=20, deadline=20, execution_time=4, criticality='high'),
        Task(task_id=3, period=30, deadline=30, execution_time=3, criticality='low')
    ]

    # Create scheduler and run
    scheduler = EDFVDScheduler(tasks)
    scheduler.schedule()
