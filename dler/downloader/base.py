#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import abc
import m3u8
import os
import requests
import time

from enum import Enum

from .progress import progress, done_event
from dler.common.loggers import create_logger
from dler.common import constants

from .models import Task
from .models import SubTask
from .enum import TaskStatus

class Downloader(object, metaclass=abc.ABCMeta):
    logger = create_logger('Downloader')
    done = False
    success_count = 0
    inc_count = 0
    process_count = 0
    total_count = 0
    task_table = None
    sub_task_table = None
    download_root = os.path.expanduser('~/Downloads/jable')
    status = TaskStatus.WAITING.value
    _sleep_seconds = 0.01
    with_progress = True

    task_id = ''

    def __init__(self, task_id):
        self.task_id = task_id
        self.sub_task_table = SubTask.db_col(task_id = self.task_id)
        self.task_table = Task.db_col()
        self.start_time = time.time()

    def _build(self):
        self.total_count = len(self.sub_task_table.find({}))

    def wait_start(self):
        while self.status != TaskStatus.PROCESS.value:
            self.logger.info('task %s waiting', self.task_id)
            self.loop_task()
            time.sleep(1)
        self.start()

    def start(self):
        self.logger.info('task %s start', self.task_id)
        self._build()
        if self.with_progress:
            with progress:
                self.run()
        else:
            self.run()

    def loop_task(self):
        task = Task.find_one_by_id(self.task_id)
        self.set_status(task.status)

    def set_status(self, status):
        self.status = status
        self._sleep_seconds = 0.01
        if self.status == TaskStatus.SLEEP.value:
            self._sleep_seconds = 2

    @classmethod
    def _get_name(cls, url):
        name, _ = os.path.basename(url).split('.')
        return name

    @classmethod
    def _generate_task_id(cls, url):
        return cls._get_name(url)

    @classmethod
    @abc.abstractmethod
    def add_task(cls, url):
        """添加任务"""
        pass

    def run(self):
        self.task_table.update({ "_id": self.task_id },
                { "status": TaskStatus.PROCESS.value })
        self.set_status(TaskStatus.PROCESS.value)
        if self.with_progress:
            self.progress_task_id = progress.add_task('download',
                filename = self.task_id, start=False, total = self.total_count)
            progress.start_task(self.progress_task_id)
        self._update_success_count()
        while not self._check_done():
            self.loop_task()
            time.sleep(self._sleep_seconds)
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

            self.async_download_sub_task(_id)

    def async_download_sub_task(self, sub_id):
        self._update_sub_task_status(sub_id, TaskStatus.PROCESS.value)

        requests.get(
            'http://0.0.0.0:{}/api/task/{}/sub_task/{}/download'.format(
                constants.SERVER_PORT,
                self.task_id, sub_id
        ))

    def download_sub_task(self, sub_id):
        """下载子任务"""
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
        if self.status == TaskStatus.SLEEP.value:
            return True
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
        if self.with_progress:
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
