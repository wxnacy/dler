#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
客户端
"""
from gevent import monkey; monkey.patch_all()
import gevent
from gevent import pool
import os
import random
import json
from dler.downloaders import download_url
from wpy.format import format_float
from dler.downloader.progress import progress as dl_progress



def find_task(task_id):
    path = f'/Users/wxnacy/.lfsdb/data/download/task/{task_id}'
    with open(path) as f:
        return json.loads(''.join(f.readlines()))

def update_task(task_id, **update_data):
    data = find_task(task_id)
    data.update(update_data)
    path = f'/Users/wxnacy/.lfsdb/data/download/task/{task_id}'
    with open(path ,'w') as f:
        f.write(json.dumps(data, indent=4))


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

def update_sub_task(task_id, sub_task_id, **update_data):
    data = find_sub_task(task_id, sub_task_id)
    data.update(update_data)
    path = f'/Users/wxnacy/.lfsdb/data/download/sub_task-{task_id}/{sub_task_id}'
    with open(path ,'w') as f:
        f.write(json.dumps(data, indent=4))

def download_sub_task(task_id, data):
    status = data.get("status")
    _id = data.get("_id")
    if status == 'success':
        return True
    #  return False

    url = data.get("download_url")
    path = data.get("download_path")
    is_download = download_url(url, path)
    if is_download:
        update_sub_task(task_id, _id, status = 'success')

    return is_download

def download_task(task_id):
    task = find_task(task_id)
    total_count = task.get("total_count")
    #  success_count = task.get("success_count")
    success_count = 0
    sub_tasks = find_sub_tasks(task_id)
    pagesize = 20
    page = int(total_count / pagesize) + 1
    progress_task_id = dl_progress.add_task('download', filename = task_id,
            start=True, total = total_count)
    for i in range(page):
        start = i * pagesize
        end = start + pagesize
        _tasks = sub_tasks[start:end]
        if not _tasks:
            break
        jobs = []
        for data in _tasks:
            job = gevent.spawn(download_sub_task, task_id, data)
            jobs.append(job)
        gevent.joinall(jobs, timeout=10)
        _success_count = len([job for job in jobs if job.value == True])
        dl_progress.update(progress_task_id, advance = _success_count)
        success_count += _success_count
        progress = format_float(success_count / total_count)
        update_task(task_id, success_count = success_count,
            progress = progress)

    if success_count >= total_count:
        update_task(task_id, status = 'success')

def main():
    with dl_progress:
        download_task('15761')


if __name__ == "__main__":
    import time
    b = time.time()
    main()
    print(time.time() - b)
