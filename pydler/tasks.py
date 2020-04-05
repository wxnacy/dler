#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler import config
from pydler import downloader
from pydler.config import celery

import youtube_dl

PYDLER_QUEUE = 'pydler_queue'

DL_DIR = config.DL_DIR

def download_yt(url):
    ydl_opts = {
        "proxy": "127.0.0.1:1080",
        "outtmpl": f"{DL_DIR}/%(title)s.%(ext)s"
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.download([url])

@celery.task()
def download_url(url, dl_dir = ''):
    '''下载地址内容'''
    if 'mmxzxl1' in url:
        url = downloader.parse_maomi_url(url)

    download_yt(url)






