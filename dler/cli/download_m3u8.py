#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from concurrent.futures import ThreadPoolExecutor

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader.models import Task

def main():
    import sys
    url = sys.argv[1:][0]
    task_id = url
    if url.startswith('http'):
        task_id = M3u8Downloader.add_task(url)
    downloader = M3u8Downloader(task_id)
    #  downloader.is_async = False
    downloader.start()
