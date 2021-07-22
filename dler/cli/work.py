#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader.models import Task
from dler.downloader.models import SubTask
from dler.downloader.enum import TaskStatus
from dler.downloader.progress import done_event
from dler.common.loggers import create_logger

logger = create_logger('dlwork')

downloaders = {}
workers = set()
def start(downloaders, task_id):
    #  downloader = M3u8Downloader(task_id)
    logger.info('process')
    downloaders[task_id].wait_start()

def is_continue():
    tasks = [Task(**o) for o in Task.db_col().find()]
    process_count = len([o for o in tasks if o.status == TaskStatus.PROCESS.value])
    logger.info(process_count)
    if process_count >= 2:
        return True

    return False

def reload_download():
    tasks = Task.db_col().find({})
    tasks = [Task(**o) for o in tasks]
    for task in tasks:
        task_id = task._id
        if task_id not in downloaders:
            downloaders[task_id] = M3u8Downloader(task_id)
            downloaders[task_id].with_progress = False

def find_waiting_task():
    tasks = [Task(**o) for o in Task.db_col().find() if o.get(
        "status") not in (TaskStatus.SUCCESS.value, TaskStatus.PROCESS.value)]
    logger.info('waiting task count %s', len(tasks))
    return tasks[0] if tasks else None

#  def test():

def run_in_shell(task_id):
    os.system('nohup dlm3 {} > /tmp/dler.log 2>&1 &'.format(task_id))

def _main():
    import sys
    import time
    with Pool(processes = 30) as pool:
        while True:
            if done_event.is_set():
                Task.db_col().update({}, { "status": TaskStatus.WAITING.value })
                break
            reload_download()
            if is_continue():
                time.sleep(2)
                continue
            task = find_waiting_task()
            if not task:
                continue
            if task._id in workers:
                continue
            logger.info('task %s add', task._id)
            Task.update_status(task._id, TaskStatus.PROCESS.value)
            workers.add(task._id)
            run_in_shell(task._id)
            #  pool.apply_async(start, (downloaders, task._id,))

def find_not_worker():
    tasks = Task.db_col().find()
    for task in tasks:
        task = Task(**task)
        if task._id not in workers:
            return task
    return None

def main():
    import sys
    import time
    while True:
        if done_event.is_set():
            Task.db_col().update({}, { "status": TaskStatus.WAITING.value })
            break
        task = find_not_worker()
        if not task:
            continue
        logger.info('task %s add', task._id)
        workers.add(task._id)
        run_in_shell(task._id)
