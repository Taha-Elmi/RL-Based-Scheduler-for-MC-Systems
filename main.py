from models import Task, System, CriticalityLevel
from ui import ExecutionTimeAdjuster
import threading
import time


def main():
    # task1 = Task(1, 5, 1, 1, CriticalityLevel.LOW)
    # task2 = Task(2, 10, 1, 1, CriticalityLevel.LOW)
    # task3 = Task(3, 5, 1, 1, CriticalityLevel.LOW)
    # task4 = Task(4, 10, 4, 6, CriticalityLevel.HIGH)

    task1 = Task(1, 7, 1.3, 5.2, CriticalityLevel.LOW)
    task2 = Task(2, 11, 4.8, 11, CriticalityLevel.LOW)
    task3 = Task(3, 17, 0.4, 1.6, CriticalityLevel.LOW)
    task4 = Task(4, 16, 2.2, 8.8, CriticalityLevel.HIGH)

    system = System.get_instance()
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)

    system.setup()

    print(f'system\'s hyper period: {system.hyper_period}')

    while True:
        system.step()
        # time.sleep(0.05)


if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=main, daemon=True)
    scheduler_thread.start()

    adjuster = ExecutionTimeAdjuster(System.get_instance())
    adjuster.run()
    # main()

