#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description:

#  from gevent import monkey
#  monkey.patch_all()
from gevent import monkey;
monkey.patch_all(thread=False)
import gevent
import time
import traceback
from gevent import pool

from pydantic import BaseModel, Field

from dler.multi_worker.models import (
    WorkModel,
    WorkerBuilder,
)

def run_work(work: WorkModel):

    if work.run_times >= 4:
        return
    try:
        is_succ = work.func(*work.func_args)
    except:
        traceback.print_exc()
        is_succ = False

    work.run_times += 1
    work.is_succ = is_succ

class MultiWorker():

    works: list = []
    _pool = None
    builder: WorkerBuilder = Field(WorkerBuilder())

    #  def __init__(self, *args, **kwargs):
        #  super().__init__(*args, **kwargs)
    def __init__(self, builder: WorkerBuilder = None):
        if not builder:
            builder = WorkerBuilder()
        self.builder = builder

        self._pool = pool.Pool(self.builder.pool_size)


    def add_work(self, func, *func_args ):
        """添加任务workeradd_workeradd_worker

        :func: TODO
        :*args: TODO
        :returns: TODO

        """
        work = WorkModel(
            work_id = len(self.works),
            func = func, func_args = func_args)
        self.works.append(work)

    def run(self):
        """运行
        """
        for i in range(self.builder.max_run_times):
            self._run_works()
            failed_count = len(list(filter(
                lambda x: not x.is_succ, self.works)))
            if not failed_count:
                break
            time.sleep(5)

    def _run_works(self):

        jobs = []
        for work in self.works:
            if work.is_succ:
                continue
            job = self._pool.spawn(run_work, work)
            jobs.append(job)
            if len(jobs) == self.builder.max_open_file_count:
                gevent.joinall(jobs, timeout = self.builder.timeout)
                jobs = []

        if jobs:
            gevent.joinall(jobs, timeout = self.builder.timeout)

    def print_response(self):
        print('Total:', len(self.works))
        print('Success:', len([o for o in self.works if o.is_succ]))

