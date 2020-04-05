#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler import config
from pydler.config import db
from pydler.config import celery
from pydler import tasks

import multiprocessing as mp

import youtube_dl
import typer
import os
import time

app = typer.Typer()

PYDLER_QUEUE = 'pydler_queue'

DL_DIR = config.DL_DIR


def ydl_hook(d):
    print(d['status'])

@celery.task()
def download_url(url, dl_dir = ''):
    '''下载地址内容'''
    if not dl_dir:
        dl_dir = DL_DIR
    ydl_opts = {
        "proxy": "127.0.0.1:1080",
        "outtmpl": "{}/%(title)s.%(ext)s".format(dl_dir)
    }
    print(dl_dir)
    print(PYDLER_QUEUE)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.download([url])

@app.command()
def add(url):
    tasks.download_url.delay(url)
    config.echo(f'添加地址 {url} 到队列中，可以使用 `pydler start` 开始任务')

@app.command()
def start(url):
    tasks.download_url.delay(url)
    config.echo(f'添加地址 {url} 到队列中，可以使用 `pydler start` 开始任务')

if __name__ == "__main__":
    #  celery.worker_main()
    app()
