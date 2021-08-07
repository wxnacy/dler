#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from wpy.functools import run_shell

from dler.downloader.models import Task
from dler.downloader.models import SubTask
from dler.downloader.enum import TaskStatus
from dler.downloader.progress import done_event, progress
from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.common.loggers import create_logger
from dler.common import utils

logger = create_logger('dlwatch')

workers = set()

POOL_SIZE = 32

def _watch():
    task_id = progress.add_task('process', filename='process',
            start=True, total = POOL_SIZE)
    process_count = 0
    while True:
        time.sleep(1)
        if done_event.is_set():
            break
        now_process_count = utils.cmd_count('dlm3')
        advance = now_process_count - process_count
        process_count = now_process_count
        progress.update(task_id, advance = advance)

def _watch_task(task_id):
    logger.info(task_id)
    downloader = M3u8Downloader(task_id)
    downloader.create_progress()

    while True:
        time.sleep(4)
        if downloader._is_watch_break():
            break
    downloader.print_result()

def find_not_worker():
    tasks = [Task(**o) for o in Task.db_col().find() if o.get(
        "status") != TaskStatus.SUCCESS.value ]
    tasks.sort(key = lambda x: x.success_count, reverse=True)
    for task in tasks:
        if task._id not in workers:
            return task
    return None

def main():
    import sys
    import time

    with progress:
        with ThreadPoolExecutor(max_workers=30) as pool:
            pool.submit(_watch)
            while True:
                if done_event.is_set():
                    break
                time.sleep(1)
                task = find_not_worker()
                if not task:
                    continue
                logger.info('watch %s', task)
                task_id = task._id
                workers.add(task_id)
                pool.submit(_watch_task, task_id)
