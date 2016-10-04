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
        self.jobName = "{}_{}".format(Path(jobFile).stem, Path(fortranFile).stem)
        self.cpus = cpus
        self.executed = executed
        self.success = success
        self.ts = 0

    def status(self):
        if self.success != "":
            return self.success
        return "Not executed."

    def name(self):
        return "{}-{}".format(self.jobName, self.ts)

    def execute(self, ts, outdir="./output"):
        if self.executed:
            return True
        self.ts = ts
        name = self.name()
        jobFile = self.prepareJobTempFile()
        fortranFile = self.prepareFortranTmpFile()

        prog = "C:\\SIMULIA\\Abaqus\\Commands\\abaqus.bat"
        cmd = "{} job=\"{}\" user=\"{}\" int cpus={}"\
            .format(prog, jobFile, fortranFile, self.cpus)

        try:
            subprocess.run(cmd)
            self.executed = True
            with open("{}.sta".format(name)) as f:
                line = tailer.tail(f, 1)
            if line.find("NOT") == -1:
                self.success = "Succeed"
            else:
                self.success = "Fail"
        except subprocess.SubprocessError:
            print("Processing Error")
            self.success = "Error"
        except FileNotFoundError:
            print ("File/Command not found")
            self.success = "File not found"
        finally:
            config = {
                "result": ["dat", "inp", "odb", "sta"],
                "log": ["msg"],
                "del": ["prt", "com", "sim"]
            }

            for k in config:
                os.makedirs(str(Path(outdir, k)), exist_ok=True)
                for f in config[k]:
                    fname = "{}.{}".format(name, f)
                    try:
                        shutil.move(fname, str(Path(outdir, k, fname)))
                    except:
                        pass
            try:
                shutil.move(fortranFile, str(Path(outdir, "result", fortranFile)))
            except:
                pass

            shutil.rmtree(str(Path(outdir, "del")), ignore_errors=True)

        return self.success

    def prepareJobTempFile(self):
        tmp_jobFile = "{}{}".format(self.name(), Path(self.jobFile).suffix)
        jobFile = str(Path(tmp_jobFile))
        shutil.copyfile(self.jobFile, jobFile)
        return jobFile

    def prepareFortranTmpFile(self):
        tmp_fortranFile = "{}{}".format(self.name(), Path(self.fortranFile).suffix)
        fortranFile = str(Path(tmp_fortranFile))
        shutil.copyfile(self.fortranFile, fortranFile)
        return fortranFile

    def reset(self):
        self.executed = False
        self.success = ""

    def list_name(self):
        jobFile = Path(self.jobFile).name
        fortranFile = Path(self.fortranFile).name
        return "Job:{} - Fortran:{} - State:{}" \
               .format(jobFile, fortranFile, self.status())

    def formatted_name(self):
        jobFile = Path(self.jobFile).name
        fortranFile = Path(self.fortranFile).name
        return "[b]Job[/b]:[color=ff3333]{}[/color] - [b]Fortran[/b]:[color=ff3333]{}[/color]" \
               .format(jobFile, fortranFile, self.status())
