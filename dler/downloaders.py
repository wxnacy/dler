#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import m3u8
import uuid
import os
import requests
import gevent
from wpy.format import format_float

from dler.downloader.progress import progress as dl_progress

from dler.loggers import get_logger
from dler.task.models import TaskModel as  Task
from dler.task.models import SubTaskModel as SubTask

logger = get_logger('downloaders')

__all__ = ['download_url']

download_root = os.path.expanduser('~/Downloads')

class Downloader(object):
    pass


class M3u8Downloader(Downloader):
    filetype = 'm3u8'
    logger = get_logger('M3u8Downloader')

    @classmethod
    def add_task(cls, url, name=None, task_id=None):
        if not name:
            name = os.path.basename(url).split('.')[0]
        task = Task(id = str(uuid.uuid4()), url = url, name = name)
        m3 = m3u8.load(url)
        total_count = 0
        sub_tasks = []
        sub_path = os.path.join(download_root, name)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)
        for i, name in enumerate(m3.files):
            #  if i > 20:
                #  continue
            if not name:
                continue
            ts_url = name
            if not ts_url.startswith('http'):
                ts_url = os.path.join(m3.base_uri, ts_url)
            print(i, ts_url)
            _path = os.path.join(sub_path, os.path.basename(ts_url))
            sub = dict(
                id = str(uuid.uuid4()), url = ts_url,
                path = _path, task_id = task.id)
            sub_tasks.append(sub)
        SubTask.insert_many(sub_tasks)
        task.total_count = len(sub_tasks)
        task.save()
        # 最后插入任务
        print('insert task', task.id)
        return task.id

def download_url(url, path):
    """下载 url 到指定路径"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 "
            "Safari/537.36",
    }
    path = os.path.expanduser(path)
    if os.path.exists(path):
        return True
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    res = requests.get(url, headers = headers)
    status_code = res.status_code
    logger.info('download {} status {}'.format(url, status_code))
    if status_code != 200:
        return False
    with open(path, 'wb') as f:
        f.write(res.content)
    return True


def download_sub_task(sub_task_id):
    sub_task = SubTask.find_by_id(sub_task_id)
    status = sub_task.status
    if status == 'success':
        return True

    url = sub_task.url
    path = sub_task.path
    is_download = download_url(url, path)
    if is_download:
        SubTask.update_success(sub_task_id)

    return is_download

def download_task(task_id):
    with dl_progress:
        _download_task(task_id)

def _download_task(task_id):
    task = Task.find_by_id(task_id)
    total_count = task.total_count
    success_count = 0
    sub_tasks = SubTask.find({"task_id": task_id})
    pagesize = 20
    page = int(total_count / pagesize) + 1
    progress_task_id = dl_progress.add_task('download',
        filename = task_id, start=True, total = total_count)
    for i in range(page):
        # 二次分页
        start = i * pagesize
        end = start + pagesize
        _tasks = sub_tasks[start:end]
        if not _tasks:
            break
        # gevent 下载
        jobs = []
        for data in _tasks:
            job = gevent.spawn(download_sub_task, data.id)
            jobs.append(job)
        gevent.joinall(jobs, timeout=10)
        _success_count = len([job for job in jobs if job.value == True])

        # 更新进度
        dl_progress.update(progress_task_id, advance = _success_count)
        success_count += _success_count
        progress = format_float(success_count / total_count)
        Task.update({"id": task_id}, dict(
            success_count = success_count,
            progress = progress
        ))

    if success_count >= total_count:
        Task.update_success(task_id)
