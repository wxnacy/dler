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
    failed_count = 0
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
        self.total_count = self._get_tatal_count()

    def wait_start(self):
        while self.status != TaskStatus.PROCESS.value:
            self.logger.info('task %s waiting', self.task_id)
            self._update_data()
            time.sleep(1)
        self.start()

    def start(self):
        self.logger.info('task %s start', self.task_id)
        if self.with_progress:
            with progress:
                self.run()
        else:
            self.run()

    def set_status(self, status, sync_task=False):
        """设置状态"""
        self.status = status
        self._sleep_seconds = 0.01
        if self.status == TaskStatus.SLEEP.value:
            self._sleep_seconds = 2
        if sync_task:
            self.task_table.update({ "_id": self.task_id },
                { "status": self.status })

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

    def _find_next_sub_task(self):
        docs = SubTask.find_not_success_items(self.task_id)
        if not docs:
            return None
        doc = docs[0]
        _id = doc._id
        # 查看任务是否已经成功
        if doc.is_success():
            self._update_sub_task_status(_id, TaskStatus.SUCCESS.value)
            return None
        return doc

    def create_progress(self):
        """创建进度条"""
        if self.with_progress:
            self.progress_task_id = progress.add_task('download',
                filename = self.task_id, start=True, total = self._get_tatal_count())

    def run(self):
        self.set_status(TaskStatus.PROCESS.value, True)
        if self.with_progress:
            self.create_progress()
        while True:
            if self._is_break():
                break
            time.sleep(self._sleep_seconds)
            if self._is_continue():
                continue
            doc = self._find_next_sub_task()
            if not doc:
                continue

            self.async_download_sub_task(doc._id)
        self.print_result()

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
        """修改子任务状态"""
        self.sub_task_table.update({ "_id": _id }, { "status": status })

    def _get_tatal_count(self):
        """获取总数量"""
        return len(self.sub_task_table.find({}))

    def _update_data(self):
        """更新数据"""
        # 获取任务最新状态
        task = Task.find_one_by_id(self.task_id)
        # 修改当前状态
        self.set_status(task.status)
        total_count = self._get_tatal_count()
        # 更新总数量
        if total_count != self.total_count:
            self.total_count = total_count
            if self.with_progress:
                progress.update(self.progress_task_id, total = self.total_count)
        self.update_progress()

    def update_progress(self):
        """更新成功数量"""
        success_count = SubTask.count_status(
            self.task_id, TaskStatus.SUCCESS.value) or 0

        self.inc_count = success_count - self.success_count
        self.success_count = success_count
        if self.with_progress:
            progress.update(self.progress_task_id, advance = self.inc_count)

    def _is_break(self):
        """是否终止"""
        task = Task.find_one_by_id(self.task_id)
        # 任务被删除
        if not task:
            return True
        # 更新数据
        self._update_data()
        self.logger.info('success_count %s', self.success_count)

        # 根据状态判断是否退出
        if self.status in (TaskStatus.SUCCESS.value,
                TaskStatus.FAILED.value, TaskStatus.STOP.value):
            return True

        # 检查是否外部停止该程序
        if done_event.is_set():
            self.set_status(TaskStatus.STOP.value, True)
            return True
        # 检查是成功还是失败
        if self.success_count >= self.total_count:
            self.set_status(TaskStatus.SUCCESS.value, True)
            return True
        else:
            self.failed_count = self.sub_task_table.count(
                { "status": TaskStatus.FAILED.value })
            if self.success_count + self.failed_count >= self.total_count:
                self.set_status(TaskStatus.FAILED.value, True)
                return True

        return False

    def print_result(self):
        print('{} is done {} success {} failed'.format(
            self.task_id, self.success_count, self.failed_count))

    def _is_continue(self):
        """是否继续"""
        if self.status == TaskStatus.SLEEP.value:
            return True
        self.process_count = self.sub_task_table.count(
                { "status": TaskStatus.PROCESS.value })
        self.logger.info('process_count %s', self.process_count)
        if self.process_count >= 8:
            return True
        return False