#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from dler.downloader.m3u8_downloader import M3u8Downloader

def main():
    import sys
    url = sys.argv[1:][0]
    M3u8Downloader.add_task(url)
