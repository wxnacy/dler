#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from concurrent.futures import ThreadPoolExecutor

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader.base import Downloader

def start(task_id):
    downloader = M3u8Downloader(task_id)
    downloader.start()

def main():
    import sys
    url = sys.argv[1:][0]
    Downloader.download(url)

    #  tasks = Task.db_col().find()
    #  task_ids = [ o.get("_id") for o in tasks if o.get("status") != 'success']
    #  task_ids = [ o.get("_id") for o in tasks ]
    #  print(task_ids)
    #  with ThreadPoolExecutor(max_workers=8) as pool:
        #  for task_id in task_ids:
            #  start(task_id)
            #  #  pool.submit(start, task_id)
    #  #  while True:
        #  #  pass
