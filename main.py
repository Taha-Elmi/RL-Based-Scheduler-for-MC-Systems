from models import Task, Job, System, CriticalityLevel
from ui import ExecutionTimeAdjuster, GraphVisualizer
import threading
import time


def main():
    task1 = Task(1, 5, 1, 1, CriticalityLevel.LOW)
    task2 = Task(2, 10, 1, 1, CriticalityLevel.LOW)
    task3 = Task(3, 5, 1, 1, CriticalityLevel.LOW)
    task4 = Task(4, 10, 4, 6, CriticalityLevel.HIGH)

    system = System.get_instance()
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)

    system.setup()

    print(system.utilization)
    print(system.vdf)

    while True:
        print(f't = {system.time}, criticality level = {system.criticality_level}')
        print(system.ready_queue)
        system.step()
        time.sleep(0.5)
        # input('----------------------------------------')


def graph_visualizer():
    while True:
        system = System.get_instance()
        graph = GraphVisualizer(system)
        graph.update()


if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=main, daemon=True)
    scheduler_thread.start()

    # visualizer_thread = threading.Thread(target=graph_visualizer, daemon=True)
    # visualizer_thread.start()

    adjuster = ExecutionTimeAdjuster(System.get_instance())
    adjuster.run()

