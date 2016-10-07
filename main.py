from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.listview import ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
from pathlib import Path
from model.task import Task
import asyncio
import sys


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class JobDialog(FloatLayout):
    add = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    list_jobs = ObjectProperty(None)
    lbl_progress = ObjectProperty(None)
    btn_execute = ObjectProperty(None)
    taskfile = "default.job"
    task = Task()
    loop = None

    def task_args_converter(self, index, rec):
        return {"text": rec.list_name(),
                "height": 25,
                }

    def update_list(self):
        self.list_jobs.adapter = \
            ListAdapter(data=self.task.jobs, cls=ListItemButton,
                        args_converter=self.task_args_converter,
                        selection_mode="multiple"
                        )

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_add(self):
        content = JobDialog(add=self.add, cancel=self.dismiss_popup)
        self._popup = Popup(title="Add jobs", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def add(self, js, fs):
        self.task.generateJob(js, fs)
        self.dismiss_popup()
        self.update_list()

    def load(self, path, filename):
        self.taskfile = str(Path(path, filename))
        self.task.load(self.taskfile)
        self.dismiss_popup()
        self.update_list()

    def save(self, path, filename):
        self.taskfile = str(Path(path, filename))
        self.task.save(self.taskfile)
        self.dismiss_popup()
        self.update_list()

    def remove_jobs(self, xs):
        ys = [len(self.task.jobs) - k - 1 for k in xs]
        self.task.removeJobs(ys)
        self.update_list()

    def reset_jobs(self, xs):
        ys = [len(self.task.jobs) - k - 1 for k in xs]
        self.task.cleanState(ys)
        self.update_list()

    def execute(self):
        self.btn_execute.disabled = True
        while self.task.hasExecutableJob():
            job = self.task.getNextExecuteJob()
            self.set_state("Running job: {}".format(job.formatted_name()))
            self.task.executeNextJob()
            self.task.save(self.taskfile)
            self.update_list()
        self.set_msg("Simulation Done.")
        self.btn_execute.disabled = False
        self.update_list()

    def start_execution(self):
        if not self.task.hasExecutableJob():
            return
        self.loop = asyncio.get_event_loop()
        if sys.platform == 'win32':
            self.loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(self.loop)
        self.btn_execute.disabled = True
        self.loop.run_forever()
        Clock.schedule_interval(lambda dt: self.update_queue(), 60)

    def update_queue(self):
        k = self.task.current_job()
        if k > -1:
            self.task.update_status()
            self.update_list()
            if self.task.jobs[k].running:
                return
        job = self.task.getNextExecutor()
        if job is not None:
            self.loop.call_soon(job)
            return
        self.set_msg("Simulation Done.")
        self.btn_execute.disabled = False
        self.loop.stop()
        self.loop.close()
        self.update_list()

    def stop_execution(self):
        if self.loop is not None:
            self.loop.stop()

    def resume_execution(self):
        if self.loop is not None:
            self.loop.run_forever()

    def set_state(self, state):
        text = "[b]Status[/b]:{}".format(state)
        self.lbl_progress.text = text

    def set_msg(self, state, color="ff3333"):
        text = "[b]Status[/b]:[color={}]{}[/color]".format(color, state)
        self.lbl_progress.text = text


class Simulator(App):
    pass

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
Factory.register('JobDialog', cls=JobDialog)

if __name__ == '__main__':
    Simulator().run()
