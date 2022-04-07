#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
import signal
import time
from threading import Event

from rich.progress import (
    BarColumn,
    DownloadColumn,
    FileSizeColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    "{task.completed}/{task.total}",
    #  "•",
    #  DownloadColumn(),
    #  "•",
    #  TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


done_event = Event()

def handle_sigint(signum, frame):
    done_event.set()

signal.signal(signal.SIGINT, handle_sigint)


#  def print_task_progress(task_id):
    #  with progress:
        #  _print_task_progress(task_id)

#  def _print_task_progress(task_id):
    #  sub_tasks = SubTaskModel.find({ "task_id": task_id })
    #  progress_task_id = progress.add_task(f'task_{task_id}',
        #  filename = task_id, start=True, total = len(sub_tasks))
    #  while True:

        #  progress.update(progress_task_id, advance = _success_count)

class DownloadProgress():

    total: int
    task_id: str
    progress: int = 0

    def __init__(self, name, total, progress_func, func_args=()):
        self.total = total
        self.func_args = func_args
        self.progress_func = progress_func
        self.task_id = progress.add_task('download',
            filename = name, start=True, total = self.total)

    def run(self):
        """
        """
        with progress:
            while self.progress < self.total:
                time.sleep(1)
                _prog = self.progress_func(*self.func_args)
                advance = _prog - self.progress
                progress.update(self.task_id, advance = advance)
                self.progress = _prog

