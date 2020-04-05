#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler import config
from pydler.config import celery

import youtube_dl

PYDLER_QUEUE = 'pydler_queue'

DL_DIR = config.DL_DIR

@celery.task()
def download_url(url, dl_dir = ''):
    '''下载地址内容'''
    if not dl_dir:
        dl_dir = DL_DIR
    ydl_opts = {
        "proxy": "127.0.0.1:1080",
        "outtmpl": f"{dl_dir}/%(title)s.%(ext)s"
    }
    print(dl_dir)
    print(PYDLER_QUEUE)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.download([url])





