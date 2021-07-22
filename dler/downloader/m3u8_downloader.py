#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
import m3u8
import os
import requests
from wpy.db import FileStorage
import time

from enum import Enum

from .progress import progress, done_event
from dler.common.loggers import create_logger
from dler.common import constants

from .models import Task
from .models import SubTask
from .enum import TaskStatus

class M3u8Downloader(object):
    logger = create_logger('M3u8Downloader')
    done = False
    success_count = 0
    inc_count = 0
    process_count = 0
    total_count = 0
    db = FileStorage('~/Downloads/db').get_db('m3u8')
    task_table = db.get_table('task')
    sub_task_table = None
    download_root = os.path.expanduser('~/Downloads/jable')
    status = TaskStatus.PROCESS.value

    task_id = ''

    def __init__(self, task_id):
        self.task_id = task_id
        self.sub_task_table = self.db.get_table('sub_task-{}'.format(self.task_id))
        self.start_time = time.time()

    def _build(self):
        self.total_count = len(self.sub_task_table.find({}))
        task = Task.db_col().find_one_by_id(self.task_id)
        self.m3 = m3u8.load(task.get("url"))
        self.progress_task_id = progress.add_task('download',
            filename = self.task_id, start=False, total = self.total_count)

    def start(self):
        with progress:
            self._build()
            self.run()

    @classmethod
    def _get_name(cls, url):
        name, _ = os.path.basename(url).split('.')
        return name

    @classmethod
    def _generate_task_id(cls, url):
        return cls._get_name(url)

    @classmethod
    def add_task(cls, url):
        _id = cls._generate_task_id(url)
        doc = cls.task_table.find_one_by_id(_id)
        task = {
            "url": url,
            "status": TaskStatus.WAITING.value,
        }
        if doc:
            cls.task_table.update({ "_id": _id }, task)
        else:
            task['_id'] = _id
            cls.task_table.insert(task)
        sub_task_table = cls.db.get_table('sub_task-{}'.format(_id))
        sub_task_table.drop()
        download_root = os.path.join(cls.download_root, _id)

        doc = {
            "download_url": url,
            "download_path": os.path.join(download_root, os.path.basename(url)),
            "status": TaskStatus.WAITING.value
        }
        sub_task_table.insert(doc)
        m3 = m3u8.load(url)
        for i, name in enumerate(m3.files):
            ts_url = name
            if not ts_url.startswith('http'):
                ts_url = os.path.join(m3.base_uri, ts_url)
            print(i, ts_url)
            _path = os.path.join(download_root, os.path.basename(ts_url))
            status = TaskStatus.WAITING.value
            if os.path.exists(_path):
                status = TaskStatus.SUCCESS.value
            doc = {
                "download_url": ts_url,
                "download_path": _path,
                "status": status
            }
            sub_task_table.insert(doc)
        return _id

    def run(self):
        self.task_table.update({ "_id": self.task_id },
                { "status": TaskStatus.PROCESS.value })
        progress.start_task(self.progress_task_id)
        self._update_success_count()
        #  self.success_count = SubTask.count_status(self.task_id, TaskStatus.SUCCESS.value) or 0
        #  progress.update(self.progress_task_id, advance = self.success_count)
        while not self._check_done():
            if self._is_continue():
                continue
            docs = SubTask.find_not_success_items(self.task_id)
            if not docs:
                continue
            doc = docs[0]
            _id = doc._id
            # 查看任务是否已经成功
            if doc.is_success():
                self._update_sub_task_status(_id, TaskStatus.SUCCESS.value)
                continue
            self._update_sub_task_status(_id, TaskStatus.PROCESS.value)

            #  with ThreadPoolExecutor(max_workers=8) as pool:
                #  pool.submit(self._download_by_web,  _id)
            self._download_by_web(_id)

        if self.done:
            self.task_table.update({ "_id": self.task_id },
                { "status": TaskStatus.SUCCESS.value })

    def _download_by_web(self, sub_id):
        requests.get(
            'http://0.0.0.0:{}/api/task/{}/sub_task/{}/download'.format(
                constants.SERVER_PORT,
                self.task_id, sub_id
        ))

    def download_sub_task(self, sub_id):
        return self._download_by_id(sub_id)

    def _download_by_id(self, sub_id):
        doc = self.sub_task_table.find_one_by_id(sub_id)

        status = TaskStatus.SUCCESS.value
        try:
            flag = self._download(doc.get("download_url"), doc.get("download_path"))
        except Exception as e:
            flag = False
            status = TaskStatus.FAILED.value
            self.sub_task_table.update({ "_id": sub_id },
                { "status": status, "error": str(e) })
        if flag:
            status = TaskStatus.SUCCESS.value
            #  progress.update(self.progress_task_id, advance = 1)
        else:
            status = TaskStatus.FAILED.value
        self._update_sub_task_status(sub_id, status)
        return status

    def _download(self, url, path):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        }
        if os.path.exists(path):
            return True
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        res = requests.get(url, headers = headers)
        status_code = res.status_code
        if status_code != 200:
            return False
        with open(path, 'wb') as f:
            f.write(res.content)
        return True

    def _update_sub_task_status(self, _id, status):
        self.sub_task_table.update({ "_id": _id }, { "status": status })

    def _is_continue(self):
        self.process_count = self.sub_task_table.count(
                { "status": TaskStatus.PROCESS.value })
        self.logger.info('process_count %s', self.process_count)
        if self.process_count >= 8:
            return True
        return False

    def _update_success_count(self):
        success_count = SubTask.count_status(
            self.task_id, TaskStatus.SUCCESS.value) or 0

        self.inc_count = success_count - self.success_count
        self.success_count = success_count
        progress.update(self.progress_task_id, advance = self.inc_count)

    def _check_done(self):
        self._update_success_count()
        if self.success_count >= self.total_count:
            self.status = TaskStatus.SUCCESS.value
        else:
            error_count = self.sub_task_table.count({ "status": TaskStatus.FAILED.value })
            if self.success_count + error_count >= self.total_count:
                self.status = TaskStatus.FAILED.value

        self.logger.info('success_count %s', self.success_count)
        if done_event.is_set():
            self.status = TaskStatus.STOP.value
            self.task_table.update({ "_id": self.task_id },
                { "status": self.status })

        self.done = self.status in (TaskStatus.SUCCESS.value,
                TaskStatus.FAILED.value, TaskStatus.STOP.value)
        if self.done:
            self.task_table.update({ "_id": self.task_id },
                { "status": self.status })
        return self.done

def start(task_id):
    downloader = M3u8Downloader(task_id)
    downloader.start()

if __name__ == "__main__":
    import random
    url = 'https://hls.videocc.net/f8f97d17d0/d/f8f97d17d0a21f1a1d84d214c5dcbfdd_1.m3u8'
    #  M3u8Downloader.add_task(url)
    task_table = FileStorage('~/Downloads/db').get_db('m3u8').get_table('task')
    tasks = task_table.find()
    task_ids = [ o.get("_id") for o in tasks ]
    print(task_ids)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for task_id in task_ids:
            start(task_id)

