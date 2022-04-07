#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

#  import multiprocessing
#  import time
#  from concurrent.futures import ThreadPoolExecutor

#  from dler.downloader.m3u8_downloader import M3u8Downloader
#  from dler.downloader.factory import DownloaderFactory
#  from dler.downloader.models import Task
from dler.downloader.progress import done_event

#  def download(filetype, task_id, sub_task_id):
    #  DL = DownloaderFactory.get_downloader(task.filetype)
    #  downloader = DL(task_id)
    #  downloader.download_sub_task(sub_task_id)

#  def main():
    #  import sys
    #  url = sys.argv[1:][0]
    #  task_id = url
    #  task = Task.find_one_by_id(task_id)
    #  pool = multiprocessing.Pool(32)
    #  for sub_task in task.find_sub_tasks():
        #  #  print(sub_task._id)
        #  pool.apply_async(download, (task.filetype, task_id, sub_task._id,))
    #  pool.close()
    #  pool.join()

    #  while True:
        #  time.sleep(4)
        #  if done_event.is_set():
            #  break
        #  task = Task.check_and_update_progress(task_id)
        #  print(task_id, task.progress)

from gevent import monkey; monkey.patch_all()
import gevent
import requests
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

def find_video(task_id):
    url = f'http://localhost:8093/myvideos/{task_id}/progress'
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception('服务未运行')
    return res.json().get("data")

def download_task(task_id):
    task = find_task(task_id)
    total_count = task.get("total_count")
    #  success_count = task.get("success_count")
    success_count = 0
    sub_tasks = find_sub_tasks(task_id)
    pagesize = 10
    page = int(total_count / pagesize) + 1
    progress_task_id = dl_progress.add_task('download', filename = task_id,
            start=True, total = total_count)

    progress_success_count = 0
    for i in range(page):
        if done_event.is_set():
            break
        start = i * pagesize
        end = start + pagesize
        _tasks = sub_tasks[start:end]
        if not _tasks:
            break
        jobs = []
        for data in _tasks:
            job = gevent.spawn(download_sub_task, task_id, data)
            jobs.append(job)
        gevent.joinall(jobs, timeout=5)
        print([job for job in jobs if job.value == True])
        _success_count = len([job for job in jobs if job.value == True])

        video_data = find_video(task_id)
        #  print(video_data)
        #  download_count = video_data.get("download_count")
        #  advance = download_count - progress_success_count
        #  progress_success_count = download_count
        #  dl_progress.update(progress_task_id, advance = _success_count)
        dl_progress.update(progress_task_id, advance = _success_count)
        success_count += _success_count
        progress = format_float(success_count / total_count)
        update_task(task_id, success_count = success_count,
            progress = progress)

    if success_count >= total_count:
        update_task(task_id, status = 'success')

def main():
    import sys
    task_id = sys.argv[1:][0]
    with dl_progress:
        for i in range(10):
            if done_event.is_set():
                break
            download_task(task_id)
            task = find_task(task_id)
            if task.get("status") == 'success':
                break


if __name__ == "__main__":
    import time
    b = time.time()
    main()
    print(time.time() - b)
