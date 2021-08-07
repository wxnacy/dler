#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader.factory import DownloaderFactory
from dler.downloader.models import Task
from dler.downloader.progress import done_event

def download(filetype, task_id, sub_task_id):
    DL = DownloaderFactory.get_downloader(task.filetype)
    downloader = DL(task_id)
    downloader.download_sub_task(sub_task_id)

def main():
    import sys
    url = sys.argv[1:][0]
    task_id = url
    task = Task.find_one_by_id(task_id)
    pool = multiprocessing.Pool(32)
    for sub_task in task.find_sub_tasks():
        #  print(sub_task._id)
        pool.apply_async(download, (task.filetype, task_id, sub_task._id,))
    pool.close()
    pool.join()

    while True:
        time.sleep(4)
        if done_event.is_set():
            break
        task = Task.check_and_update_progress(task_id)
        print(task_id, task.progress)
