#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from concurrent.futures import ThreadPoolExecutor

from pydler.downloader.m3u8_downloader import M3u8Downloader
from pydler.downloader.models import Task

def start(task_id):
    downloader = M3u8Downloader(task_id)
    downloader.start()

def main():
    import sys
    url = sys.argv[1:][0]
    task_id = M3u8Downloader.add_task(url)
    downloader = M3u8Downloader(task_id)
    downloader.start()
