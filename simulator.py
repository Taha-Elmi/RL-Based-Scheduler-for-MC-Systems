import random
from typing import List
from models import Task


class TaskGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)

    def generate_task(self, task_id: int) -> Task:
        """
        Generate a single task with random properties.
        """
        execution_time = random.randint(1, 10)  # Example range
        period = random.randint(10, 20)
        deadline = random.randint(execution_time, 20)

        return Task(
            id=task_id,
            execution_time=execution_time,
            period=period,
            deadline=deadline,
        )

    def generate_tasks(self, num_tasks: int) -> List[Task]:
        """
        Generate a list of tasks.
        """
        return [self.generate_task(i) for i in range(num_tasks)]

    def save_tasks_to_file(self, tasks: List[Task], filename: str) -> None:
        """
        Save a list of tasks to a file.
        """
        with open(filename, "w") as file:
            for task in tasks:
                file.write(f"{task.id},{task.type.value},{task.execution_time},{task.period},{task.deadline}\n")

    def load_tasks_from_file(self, filename: str) -> List[Task]:
        """
        Load a list of tasks from a file.
        """
        tasks = []
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                task_id = int(parts[0])
                execution_time = int(parts[2])
                period = int(parts[3]) if parts[3] != "None" else None
                deadline = int(parts[4]) if parts[4] != "None" else None

                tasks.append(Task(
                    id=task_id,
                    execution_time=execution_time,
                    period=period,
                    deadline=deadline,
                ))
        return tasks


class Simulator:
    def __init__(self, system):
        self.system = system

    def run(self):
        pass
