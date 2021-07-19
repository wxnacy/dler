#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from wpy.downloader.m3u8_downloader import M3u8Downloader
from wpy.db import FileStorage
from concurrent.futures import ThreadPoolExecutor

def start(task_id):
    downloader = M3u8Downloader(task_id)
    downloader.start()

def main():
    import sys

    task_table = FileStorage('~/Downloads/db').get_db('m3u8').get_table('task')
    tasks = task_table.find()
    task_ids = [ o.get("_id") for o in tasks if o.get("status") != 'success']
    task_ids = [ o.get("_id") for o in tasks ]
    print(task_ids)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for task_id in task_ids:
            #  start(task_id)
            pool.submit(start, task_id)
