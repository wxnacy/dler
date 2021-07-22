#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from concurrent.futures import ThreadPoolExecutor

from dler.downloader.models import Task
from dler.downloader.models import SubTask
from dler.downloader.enum import TaskStatus
from dler.downloader.progress import done_event, progress
from dler.common.loggers import create_logger

logger = create_logger('dlwatch')

workers = set()

def watch_task(task_id):
    logger.info(task_id)
    task = Task.find_one_by_id(task_id)
    sub_tasks = task.find_sub_tasks()
    total_count = len(sub_tasks)
    progress_task_id = progress.add_task('download',
                filename = task_id, start=True, total = total_count)
    success_count = 0

    while True:
        if done_event.is_set():
            #  progress.stop_task(progress_task_id)
            break
        task = Task.find_one_by_id(task_id)
        if not task:
            print(task_id, 'delete')
            #  progress.stop_task(progress_task_id)
            break
        if task.is_success:
            print(task._id, 'success')
            #  progress.stop_task(progress_task_id)
            break
        sub_tasks = task.find_sub_tasks()
        total_count = len(sub_tasks)
        success_sub_tasks = task.find_sub_tasks(
            { "status": TaskStatus.SUCCESS.value })
        now_success_count = len(success_sub_tasks)

        inc_count = now_success_count - success_count
        logger.info('inc_count %s', inc_count)
        success_count = now_success_count
        progress.update(progress_task_id, total = total_count, advance = inc_count)

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

    with progress:
        with ThreadPoolExecutor(max_workers=30) as pool:
            while True:
                if done_event.is_set():
                    break
                task = find_not_worker()
                if not task:
                    continue
                logger.info('watch %s', task)
                task_id = task._id
                workers.add(task_id)
                pool.submit(watch_task, task_id)
