import multiprocessing
import subprocess
import shutil
import tailer
import os
from pathlib import Path


class Job:
    max_cpus = multiprocessing.cpu_count()

    def __init__(self, jobFile, fortranFile, cpus=max_cpus,
                 executed=False, success=""):
        self.jobFile = jobFile
        self.fortranFile = fortranFile
        self.cpus = cpus
        self.executed = executed
        self.success = success
        self.ts = 0

    def status(self):
        if self.executed:
            return self.success
        return "Not executed."

    def execute(self, ts, outdir="./output"):
        if self.executed:
            return True
        self.ts = ts
        name = "{}-{}".format(Path(self.jobFile).stem, ts)
        jobFile = self.prepareJobTempFile()
        fortranFile = self.prepareFortranTmpFile()

        prog = "C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat"
        cmd = "{} job=\"{}\" user=\"{}\" int cpus={}"\
            .format(prog, jobFile, fortranFile, self.cpus)

        subprocess.run(cmd)
        self.executed = True
        with open("{}.sta".format(name)) as f:
            line = tailer.tail(f, 1)
        self.success = line.find("NOT") == -1

        config = {
            "result": ["dat", "inp", "odb", "sta"],
            "log": ["msg"],
            "del": ["prt", "com", "sim"]
        }

        for k, v in config:
            os.makedirs(Path(outdir, k), exist_ok=True)
            for f in v:
                fname = "{}.{}".format(name, f)
                shutil.move(fname, Path(outdir, k, fname))

        shutil.rmtree(Path(outdir, "del"))
        return self.success

    def prepareJobTempFile(self):
        name = "{}-{}".format(Path(self.jobFile).stem, self.ts)
        tmp_jobFile = "{}.{}".format(name, Path(self.jobFile).suffix)
        jobFile = Path(tmp_jobFile)
        shutil.copyfile(self.jobFile, jobFile)
        return jobFile

    def prepareFortranTmpFile(self):
        name = "{}-{}".format(Path(self.fortranFile).stem, self.ts)
        tmp_fortranFile = "{}.{}".format(name, Path(self.fortranFile).suffix)
        fortranFile = Path(tmp_fortranFile)
        shutil.copyfile(self.fortranFile, fortranFile)
        return fortranFile

    def reset(self):
        self.executed = False
        self.success = ""
