from models import Task, Job, System, CriticalityLevel


if __name__ == '__main__':
    task1 = Task(1, 7, 1.3, CriticalityLevel.LOW)
    task2 = Task(2, 11, 4.8, CriticalityLevel.LOW)
    task3 = Task(3, 17, 0.4, CriticalityLevel.LOW)
    task4 = Task(4, 16, 2.2, CriticalityLevel.HIGH)

    system = System.get_instance()
    system.add_task(task1)
    system.add_task(task2)
    system.add_task(task3)
    system.add_task(task4)

    while True:
        print(f't = {system.time}, criticality level = {system.criticality_level}')
        print(system.ready_queue)
        system.step()
        input('----------------------------------------')
