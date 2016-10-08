import pickle
import time
from model.job import Job
from functools import partial


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

    def generateJob(self, js, fs):
        for j in js:
            for f in fs:
                self.addJob(Job(j, f))

    def addJob(self, job):
        self.jobs.append(job)

    def removeJob(self, index):
        return self.jobs.pop(index)

    def removeJobs(self, xs):
        ks = range(len(self.jobs))
        js = [v for k, v in zip(ks, self.jobs) if k not in xs]
        self.jobs = js

    def clearTask(self):
        self.jobs = []

    def cleanState(self, xs):
        self.ts = int(time.time())
        for k in xs:
            self.jobs[k].reset()

    def hasExecutableJob(self):
        return self.nextJob < len(self.jobs)

    def getNextExecuteJob(self):
        if not self.hasExecutableJob():
            return None
        return self.jobs[self.nextJob]

    def current_job(self):
        if self.hasExecutableJob():
            return self.nextJob - 1
        return -1

    def getExecutor(self, index):
        ts = int(time.time())
        return partial(self.jobs[index].execute, ts)

    def getNextExecutor(self):
        if not self.hasExecutableJob():
            return None
        job = self.getExecutor(self.nextJob)
        self.nextJob = self.nextJob + 1
        return job

    def executeNextJob(self):
        if not self.hasExecutableJob():
            return None
        self.executeJob(self.nextJob)
        self.nextJob = self.nextJob + 1

    def executeJob(self, index):
        ts = int(time.time())
        self.jobs[index].execute(ts)

    def update_status(self):
        for j in self.jobs:
            j.update_status()
