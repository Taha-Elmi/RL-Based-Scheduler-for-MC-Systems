import enum


class CriticalityLevel(enum.Enum):
    HIGH = enum.auto()
    LOW = enum.auto()


class System:
    _instance = None

    def __init__(self):
        self.tasks = []
        self.jobs = []
        self.ready_queue = []
        self.criticality_level = CriticalityLevel.LOW
        self.utilization = {}
        self.vdf = 0
        self.time = 0

    def add_task(self, task):
        self.tasks.append(task)

    def calculate_utilization(self):
        for task_criticality_level in CriticalityLevel:
            for system_criticality_level in CriticalityLevel:
                if system_criticality_level == CriticalityLevel.HIGH and task_criticality_level == CriticalityLevel.LOW:
                    continue
                u = 0
                for task in self.tasks:
                    if task.criticality_level == task_criticality_level:
                        u += task.wcet[system_criticality_level] / task.period
                self.utilization[(task_criticality_level, system_criticality_level)] = u

    def update_vdf(self):
        self.vdf = (self.utilization[(CriticalityLevel.HIGH, CriticalityLevel.LOW)] /
                    (1 - self.utilization[(CriticalityLevel.LOW, CriticalityLevel.LOW)]))

    def release_job(self, task):
        new_job = Job(task)
        task.number_of_jobs += 1
        self.jobs.append(new_job)
        self.ready_queue.append(new_job)
        print(f'a job from task {task.id} has been released')

    def schedule(self):
        def deadline_and_criticality_sort_function(j1: Job, j2: Job) -> int:
            a = j1.get_deadline()
            b = j2.get_deadline()
            if a < b:
                return -1
            elif a == b:
                if j1.task.criticality_level == j2.task.criticality_level:
                    return 0
                if j1.task.criticality_level == CriticalityLevel.HIGH:
                    return -1
                return 1
            else:
                return 1

        from functools import cmp_to_key
        self.ready_queue.sort(key=cmp_to_key(deadline_and_criticality_sort_function))

    def step(self):
        for task in self.tasks:
            if (self.time % task.period == 0
                    and (self.criticality_level == CriticalityLevel.LOW or
                         task.criticality_level == CriticalityLevel.HIGH)):
                self.release_job(task)

        self.schedule()

        if len(self.ready_queue) > 0:
            chosen_job = self.ready_queue[0]
            chosen_job.execution_time += 1

            if (chosen_job.execution_time > chosen_job.task.wcet[System.get_instance().criticality_level]
                    and chosen_job.task.criticality_level == CriticalityLevel.HIGH):
                self.switch_mode_to_high()

            if chosen_job.execution_time >= chosen_job.generate_random_execution_time():
                chosen_job.is_done = True
                self.ready_queue.remove(chosen_job)
        elif self.criticality_level == CriticalityLevel.HIGH:
            self.switch_mode_to_low()

        self.time += 1

    def switch_mode_to_high(self):
        self.criticality_level = CriticalityLevel.HIGH
        for job in self.ready_queue[:]:
            if job.task.criticality_level == CriticalityLevel.LOW:
                print(f'a job from task {job.task.id} has been dropped.')
                self.ready_queue.remove(job)

    def switch_mode_to_low(self):
        self.criticality_level = CriticalityLevel.LOW

    @staticmethod
    def get_instance():
        if System._instance is None:
            System._instance = System()
        return System._instance


class Task:
    counter = 1

    def __init__(self, id, period, low_wcet, high_wcet, criticality_level):
        # self.id = Task.counter
        self.id = id
        self.period = period
        self.wcet = {CriticalityLevel.LOW: low_wcet, CriticalityLevel.HIGH: high_wcet}
        self.aet = 0
        self.number_of_jobs = 0
        self.criticality_level = criticality_level

        Task.counter += 1


class Job:
    def __init__(self, task: Task):
        self.task = task
        self.release_time = System.get_instance().time
        self.execution_time = 0
        self.is_done = False

    def generate_random_execution_time(self):
        return self.task.wcet[System.get_instance().criticality_level]

    def get_deadline(self):
        if System.get_instance().criticality_level == CriticalityLevel.HIGH or self.task.criticality_level == CriticalityLevel.LOW:
            return self.release_time + self.task.period
        else:
            return self.release_time + (System.get_instance().vdf * self.task.period)

    def __repr__(self):
        return f'[task_id: {self.task.id}, deadline: {self.get_deadline()}, wcet: {self.task.wcet}, execution_time: {self.execution_time}]\n'
