#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

#  from concurrent.futures import ThreadPoolExecutor

#  from dler.downloader.m3u8_downloader import M3u8Downloader
#  from dler.downloader.base import Downloader

#  def start(task_id):
    #  downloader = M3u8Downloader(task_id)
    #  downloader.start()

from dler.tasker.m3u8_tasker import M3u8Tasker

def main():
    import sys
    url = sys.argv[1:][0]
    if url.endswith('m3u8'):
        tasker = M3u8Tasker(url = url)

    tasker.build()
    tasker.run()

