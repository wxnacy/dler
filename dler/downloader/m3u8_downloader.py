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
from .decorates import downloader_register

@downloader_register()
class M3u8Downloader(Downloader):
    filetype = 'm3u8'
    logger = create_logger('M3u8Downloader')

    @classmethod
    def add_task(cls, url, task_id=None):
        _id = cls._generate_task_id(url)
        if task_id:
            _id = task_id
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
        total_count = 0
        for i, name in enumerate(m3.files):
            if not name:
                continue
            if not name.endswith('.ts'):
                continue
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
            total_count += 1
        # 最后插入任务
        print('insert task')
        cls.insert_task(_id, url, total_count = total_count + 1)
        return _id
