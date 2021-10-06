#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader import DownloaderFactory

def main():
    import sys
    args = sys.argv[1:]
    url = args[0]
    arg_task_id = None
    if len(args) >= 2:
        arg_task_id = args[1]
    Downloader = DownloaderFactory.get_downloader_by_url(url)
    Downloader.add_task(url, arg_task_id)
