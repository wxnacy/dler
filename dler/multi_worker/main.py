#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: 

from dler.multi_worker.multi_worker import MultiWorker
import os
import json
import requests
import multiprocessing as mp
from wpy.base import BaseObject
from dler.downloaders import download_url
from dler.downloader.progress import DownloadProgress


def find_sub_tasks(task_id):
    dirname = f'/Users/wxnacy/.lfsdb/data/download/sub_task-{task_id}'
    items = []
    for name in os.listdir(dirname):
        path = os.path.join(dirname, name)
        with open(path) as f:
            data = json.loads(''.join(f.readlines()))
            items.append(data)
    return items

def _read(path):
    with open(path) as f:
        return json.loads(''.join(f.readlines()))

def find_sub_task(task_id, sub_task_id):
    path = f'/Users/wxnacy/.lfsdb/data/download/sub_task-{task_id}/{sub_task_id}'
    return _read(path)

class SubTask(BaseObject):
    _id: str
    download_url: str
    download_path: str
    is_succ: bool

def download_task(task_id, sub_id) -> bool:

    task = find_sub_task(task_id, sub_id)
    st = SubTask(**task)

    url = st.download_url
    path = f"/Users/wxnacy/Downloads/dltest/{os.path.basename(url)}"
    print(url, path)
    is_succ = download_url(url, path)
    task['is_succ'] = is_succ

    return is_succ

def single_run(task_id, count):
    sub_tasks = find_sub_tasks(task_id)
    for sub_task in sub_tasks[:count]:
        sub_task = SubTask(**sub_task)
        download_task(task_id, sub_task._id)

def multi_run(task_id, count):
    mw = MultiWorker()
    sub_tasks = find_sub_tasks(task_id)
    for sub_task in sub_tasks[:count]:
        sub_task = SubTask(**sub_task)
        mw.add_work(download_task, task_id, sub_task._id)
    mw.run()
    mw.print_response()

def find_task_progress(task_id):
    find_sub_tasks(task_id)


def print_progress(task_id):
    sub_tasks = find_sub_tasks(task_id)
    DownloadProgress(task_id, len(sub_tasks), )


if __name__ == "__main__":
    import time
    b = time.time()
    task_id = '18580'
    count = 200
    p = mp.Process(target=run_server, args=(task_id,), daemon=True)
    p.start()
    multi_run(task_id, count)
    p.terminate()

    print(time.time() - b)
