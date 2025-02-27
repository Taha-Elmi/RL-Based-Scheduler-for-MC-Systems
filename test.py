import random
from math import gcd
from os import system, name

# Clear console screen
def clear_screen():
    """Clears the console screen based on the operating system."""
    system('cls' if name == 'nt' else 'clear')

# Read task set from file
def read_task_set(file_path):
    """
    Reads tasks from a file and returns a list of tasks.
    Each task is represented as [Task ID, C(LO), C(HI), D, P, L, RT].
    """
    tasks = []
    with open(file_path, 'r') as file:
        file.readline()  # Skip header
        for line in file:
            task_data = list(map(int, line.strip().split(',')))
            task_id = len(tasks) + 1
            release_time = 0  # Default release time
            period = task_data[3]  # Period = Deadline
            tasks.append([task_id, *task_data, release_time])
    return tasks

# Calculate X-parameter
def calculate_x_parameter(tasks):
    """
    Computes the X-parameter for EDF-VD scheduling.
    X ensures schedulability under both low and high-criticality modes.
    """
    u_lo_lo = u_hi = u_lo_hi = 0
    for task in tasks:
        if task[5] == 0:  # Low-criticality task
            u_lo_lo += task[1] / task[4]
        elif task[5] == 1:  # High-criticality task
            u_hi += task[2] / task[4]
            u_lo_hi += task[1] / task[4]
    x = u_lo_hi / (1 - u_lo_lo)
    if x * u_lo_lo + u_hi <= 1:
        return round(x, 2)
    return 1

# Calculate hyperperiod (LCM of all task periods)
def calculate_hyperperiod(tasks):
    """Computes the hyperperiod as the LCM of all task periods."""
    periods = [task[4] for task in tasks]
    lcm = periods[0]
    for period in periods[1:]:
        lcm = lcm * period // gcd(lcm, period)
    return lcm

# Display task set
def display_tasks(tasks, x):
    """Displays the task set with virtual deadlines."""
    print("TID\tC(LO)\tC(HI)\tD\tP\tL\tRT\tVD")
    for task in tasks:
        if task[5] == 1:  # High-criticality task
            vd = x * task[3]
        else:
            vd = '-'
        print(f"{task[0]}\t{task[1]}\t{task[2]}\t{task[3]}\t{task[4]}\t{task[5]}\t{task[6]}\t{vd}")

# EDF-VD Scheduler
def edf_vd_scheduler(tasks, hyperperiod, x):
    """
    Simulates the EDF-VD scheduling algorithm.
    Outputs the schedule for the given task set.
    """
    time_left = [task[1] for task in tasks]  # Remaining execution time
    timeline = []
    criticality = 0  # System criticality mode (0: LO, 1: HI)

    for time in range(hyperperiod):
        # Update task deadlines and remaining execution times
        for i, task in enumerate(tasks):
            if time % task[4] == 0 and time >= task[6]:
                time_left[i] = task[1] if criticality == 0 else task[2]

        # Find the task with the earliest deadline
        next_task = None
        for i, task in enumerate(tasks):
            if time_left[i] > 0:
                if next_task is None or task[3] < tasks[next_task][3]:
                    next_task = i

        # Schedule the task
        if next_task is not None:
            timeline.append((time, time + 1, tasks[next_task][0], criticality))
            time_left[next_task] -= 1
        else:
            timeline.append((time, time + 1, '-', 'I'))  # Idle time

        # Handle overruns (switch to high-criticality mode)
        if criticality == 0 and any(task[5] == 1 and time_left[i] > 0 for i, task in enumerate(tasks)):
            if random.randint(1, 100000) == 1:  # Simulate overrun signal
                print(f"Overrun detected at time {time + 1}. Switching to high-criticality mode.")
                criticality = 1
                for i, task in enumerate(tasks):
                    if task[5] == 1:
                        time_left[i] = task[2] - task[1]  # Adjust remaining execution time

    # Display the schedule
    print("\nSchedule:")
    print("*********************************************************************")
    print("Start Time\tEnd Time\tTask ID\tSystem Criticality")
    for entry in timeline:
        print(f"{entry[0]}\t\t{entry[1]}\t\t{entry[2]}\t\t{entry[3]}")
    print("*********************************************************************")

# Main function
def main():
    clear_screen()
    file_path = 'Tasks.txt'  # Path to the task set file
    tasks = read_task_set(file_path)
    x = calculate_x_parameter(tasks)
    hyperperiod = calculate_hyperperiod(tasks)

    print("Task Set:")
    display_tasks(tasks, x)
    print(f"\nHyperperiod: {hyperperiod}")
    print(f"X-parameter: {x}")

    edf_vd_scheduler(tasks, hyperperiod, x)

if __name__ == "__main__":
    main()
