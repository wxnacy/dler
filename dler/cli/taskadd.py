#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader import DownloaderFactory

def main():
    import sys
    url = sys.argv[1:][0]
    Downloader = DownloaderFactory.get_downloader_by_url(url)
    Downloader.add_task(url)
