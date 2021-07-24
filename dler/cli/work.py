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

def find_next_task():
    tasks = [Task(**o) for o in Task.db_col().find() if o.get(
        "_id") not in workers]
    process_count = len([o for o in tasks if o.status == TaskStatus.PROCESS.value])
    if process_count >= 8:
        return None
    return tasks[0] if tasks else None

def run_in_shell(task_id):
    os.system('nohup dlm3 {} > /tmp/dler.log 2>&1 &'.format(task_id))

def main():
    import sys
    import time
    while True:
        if done_event.is_set():
            Task.db_col().update({}, { "status": TaskStatus.WAITING.value })
            break
        task = find_next_task()
        if not task:
            continue
        logger.info('task %s add', task._id)
        workers.add(task._id)
        run_in_shell(task._id)
