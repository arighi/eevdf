#!/usr/bin/env python
# SPDX-License-Identifier: GPL-2.0
#
# EEVDF scheduler simulator.

# Default task weight
BASE_WEIGHT = 100


class Task:
    def __init__(self, name, weight, time_slice, use_slice):
        self.name = name
        self.weight = weight
        self.time_slice = time_slice
        self.use_slice = use_slice
        self.vruntime = 0
        self.deadline = 0
        self.lag = 0

    def __repr__(self):
        return f"{self.name}: weight={self.weight} vruntime={self.vruntime:.1f} deadline={self.deadline:.1f} time_slice={self.time_slice} use_slice={self.use_slice}, lag={self.lag:.1f}"


class EEVDFScheduler:
    def __init__(self, tasks):
        self.tasks = tasks
        self.time = 0

    def scale_inverse_fair(self, t, value):
        return value * BASE_WEIGHT / t.weight

    def compute_lag(self):
        """
        Compute lag as:
        lag = task's vruntime - average vruntime of all tasks
        """
        avg_vruntime = sum(t.vruntime for t in self.tasks) / len(self.tasks)
        for task in self.tasks:
            task.lag = avg_vruntime - task.vruntime

    def pick_next_task(self):
        """
        Pick the next task based on eligibility (lag >= 0) and earliest virtual deadline.
        """
        eligible_tasks = [t for t in self.tasks if t.lag >= 0]
        if not eligible_tasks:
            return None

        return min(eligible_tasks, key=lambda t: t.deadline)

    def run(self, time=1000):
        """
        Simulate the scheduling of tasks.
        """
        while self.time < time:
            task = self.pick_next_task()
            if not task:
                break

            runtime = task.use_slice

            # Update vruntime for the running task
            task.vruntime += self.scale_inverse_fair(task, runtime)
            task.deadline = task.vruntime + self.scale_inverse_fair(
                task, task.time_slice
            )

            # Update global vruntime
            self.time += runtime

            # Update lag values
            self.compute_lag()

            print(f"\n>> running {task.name} for {runtime}ms at time {self.time}ms")

            self.print_state()

    def print_state(self):
        """
        Print the current state of tasks.
        """
        for task in self.tasks:
            print(task)


if __name__ == "__main__":
    tasks = [
        Task("A", weight=100, time_slice=30, use_slice=15),
        Task("B", weight=200, time_slice=30, use_slice=30),
        Task("C", weight=100, time_slice=30, use_slice=40),
    ]

    scheduler = EEVDFScheduler(tasks)
    scheduler.run()
