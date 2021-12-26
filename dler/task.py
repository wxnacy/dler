#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""
负责下载任务的执行
"""

import os
from wpy.base import BaseObject
from wpy.files import FileUtils
from wpy.security import md5

from .constants import Constants
from .downloaders import download_url

__all__ = ['run_task', 'Task']

class Task(BaseObject):
    task_id = None
    url = None
    sub_tasks = []

    def __init__(self, url, sub_tasks=None, **kwargs):
        self.task_id = md5(url)
        self.url = url
        if sub_tasks and isinstance(sub_tasks, list):
            self.sub_tasks = sub_tasks

    def run(self):
        """运行任务"""
        #  for sub_task in self.sub_tasks:
            #  if sub_task.get("is_download"):
                #  continue
            #  is_downlaod = download_url(url, path)
            #  sub_task['is_downlaod'] = is_downlaod

        for sub_task in self._iter_todo_sub_task():
            url = sub_task.get("url")
            path = sub_task.get("path")
            download_url(url, path)

    def _iter_todo_sub_task(self):
        """遍历需要完成的子任务"""
        for sub_task in self.sub_tasks:
            if sub_task.get("is_download"):
                yield sub_task

    @classmethod
    def _create_task_path(cls, task_id):
        """创建任务路径"""
        return os.path.join(Constants.DOWNLOAD_DIR, 'dler', str(task_id))

    @classmethod
    def load(cls, task_id):
        """加载本地任务"""
        filepath = cls._create_task_path(task_id)
        data = FileUtils.read_dict(filepath)
        return cls(**data)

    def dump(self):
        """辈分任务"""
        filepath = self._create_task_path(self.task_id)
        FileUtils.write_dict(filepath, self.to_dict())
        return filepath


def run_task(task_id):
    """运行任务"""
    return Task.load(task_id).run()

def create_task(url):
    pass

