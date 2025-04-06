from models import Task, System, CriticalityLevel
from ui import ExecutionTimeAdjuster
import threading


def main():
    task1 = Task(1, 10, 2.0, 3.5, CriticalityLevel.LOW)
    task2 = Task(2, 15, 1.5, 2.8, CriticalityLevel.LOW)
    task3 = Task(3, 20, 3.0, 5.5, CriticalityLevel.HIGH)
    task4 = Task(4, 25, 2.5, 4.5, CriticalityLevel.HIGH)

    system = System.get_instance()
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)

    system.setup()

    print(f'system\'s hyper period: {system.hyper_period}')

    while True:
        system.step()


if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=main, daemon=True)
    scheduler_thread.start()

    adjuster = ExecutionTimeAdjuster(System.get_instance())
    adjuster.run()
