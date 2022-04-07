#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from concurrent.futures import ThreadPoolExecutor

from dler.downloaders import M3u8Downloader
from dler.downloaders import download_task

def main():
    import sys
    args = sys.argv[1:]
    url = args[0]
    arg_task_id = None
    if len(args) >= 2:
        arg_task_id = args[1]

    print(url, arg_task_id)
    #  return
    task_id = url
    if url.startswith('http'):
        task_id = M3u8Downloader.add_task(url, arg_task_id)
    download_task(task_id)
