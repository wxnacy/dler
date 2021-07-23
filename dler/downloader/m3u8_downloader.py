#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import m3u8
import os
import time

from dler.common.loggers import create_logger

from .models import Task
from .models import SubTask
from .enum import TaskStatus
from .base import Downloader

class M3u8Downloader(Downloader):
    logger = create_logger('M3u8Downloader')

    @classmethod
    def add_task(cls, url):
        _id = cls._generate_task_id(url)
        sub_task_table = SubTask.db_col(task_id = _id)
        sub_task_table.drop()
        download_root = os.path.join(cls.download_root, _id)

        print('insert sub_task')
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
        # 最后插入任务
        print('insert task')
        task_table = Task.db_col()
        doc = task_table.find_one_by_id(_id)
        task = {
            "url": url,
            "status": TaskStatus.WAITING.value,
        }
        if doc:
            task_table.update({ "_id": _id }, task)
        else:
            task['_id'] = _id
            task_table.insert(task)
        return _id
