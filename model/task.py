import pickle
import time


class Task:
    def __init__(self, outdir="./output"):
        self.jobs = []
        self.nextJob = 0
        self.ts = int(time.time())

    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.jobs, f)

    def load(self, filename):
        with open(filename, "rb") as f:
            self.jobs = pickle.load(f)

    def addJob(self, job):
        self.jobs.append(job)

    def removeJob(self, index):
        return self.jobs.pop(index)

    def removeJobs(self, xs):
        ks = range(len(self.jobs))
        js = [v for k, v in zip(self.jobs, ks) if k not in xs]
        self.jobs = js

    def clearTask(self):
        self.jobs = []

    def cleanState(self, xs):
        self.ts = int(time.time())
        for k in xs:
            self.jobs[k].reset()

    def executeNextJob(self):
        if self.nextJob >= len(self.jobs):
            return True
        self.executeJob(self.nextJob)
        self.nextJob = self.nextJob + 1

    def executeJob(self, index):
        self.jobs[index].execute(self.ts)
