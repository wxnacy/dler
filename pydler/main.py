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

def download(queue_name, dl_dir = ''):
    '''下载地址内容'''
    url = get_last_url(queue_name)
    if not url:
        return
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

@app.command()
def add(url: str, queue_name: str = ''):
    #  insert_msg = f'{url}\n'
    #  filename = f'{config.QUEUE_DIR}/{time.time()}-{url}'
    #  filename = f'{config.QUEUE_DIR}/{time.time()}'
    #  if not queue_name:
        #  queue_name = PYDLER_QUEUE
    #  db.rpush(queue_name, url)
    tasks.download_url.delay('https://www.youtube.com/watch?v=j8ULt1P9rxY')
    config.echo(f'添加地址 {url} 到队列中，可以使用 `pydler start` 开始任务')

def get_last_url(queue_name = PYDLER_QUEUE):
    #  names = os.listdir(config.QUEUE_DIR)
    #  yield f'{config.QUEUE_DIR}/{names[0]}'
    res = db.lpop(queue_name)
    if res:
        res = res.decode()
    return res

def get_queue():
    '''获取队列信息'''
    #  res = []
    #  if not os.path.exists(config.QUEUE):
        #  return res
    #  with open(config.QUEUE, 'r') as f:
        #  lines = f.readlines()
        #  for line in lines:
            #  url = line.strip('\n')
            #  if url:
                #  res.append(url)
    #  print(res)
    ranges = db.lrange(PYDLER_QUEUE, 0, 1000)
    res = []
    for r in ranges:
        res.append(r.decode())
    return res

@app.command()
def start():
    config.echo('Hello World')
    celery.worker_main()

#  @app.command()
#  def start(url: str = '', dl_dir: str = '', queue_name: str = ''):
    #  config.echo('Hello World')
    #  celery.worker_main()
    #  config.echo(url)
    #  if not queue_name:
        #  queue_name = PYDLER_QUEUE
    #  if not dl_dir:
        #  dl_dir = DL_DIR

    #  pool = mp.Pool(processes=4)

    #  while True:
        #  pool.apply_async(download, (queue_name, dl_dir))

if __name__ == "__main__":
    #  celery.worker_main()
    app()
