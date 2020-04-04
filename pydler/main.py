#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler import config
from pydler.config import db

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

def download(url, dl_dir = DL_DIR):
    '''下载地址内容'''
    #  config.YDL_OPTS['progress_hooks'] = [ydl_hook]
    #  YDL_ARCHIVE=f'{HOME}/.pydler-archive'
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
    insert_msg = f'{url}\n'
    filename = f'{config.QUEUE_DIR}/{time.time()}-{url}'
    filename = f'{config.QUEUE_DIR}/{time.time()}'
    if queue_name:
        PYDLER_QUEUE = queue_name
    print(PYDLER_QUEUE)
    db.rpush(PYDLER_QUEUE, url)
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
def start(url: str = '', dl_dir: str = '', queue_name: str = ''):
    config.echo('Hello World')
    config.echo(url)
    if dl_dir:
        DL_DIR = dl_dir
    if queue_name:
        PYDLER_QUEUE = queue_name
    #  if url:
        #  pool.apply_async(download, (url,))
    pool = mp.Pool(processes=4)

    #  for u in [
        #  'https://www.youtube.com/watch?v=COMHDRqAvYE',
        #  'https://www.youtube.com/watch?v=jOxzAsnx9-0',
        #  'https://www.youtube.com/watch?v=6d0v2InyN_w',
        #  ]:
        #  pool.apply_async(download, (u,))

    while True:
        u = get_last_url(PYDLER_QUEUE)
        if u:
            pool.apply_async(download, (u,DL_DIR))



if __name__ == "__main__":
    app()
    
