#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import os
import time

from dler.common.loggers import create_logger
from wpy.tools import randoms

from .base import Downloader
from .decorates import downloader_register
from .enum import TaskStatus
from .models import Task
from .models import SubTask

@downloader_register()
class ImageDownloader(Downloader):
    filetype = 'image'
    logger = create_logger('ImageDownloader')

    @classmethod
    def add_task(cls, url, path=None):
        task_id = 'image'
        #  sub_id = cls._generate_task_id(url)
        sub_id = randoms.random_str(6)
        sub_task_table = SubTask.db_col(task_id = task_id)
        download_root = os.path.join(cls.download_root, _id)

        print('insert sub_task')
        doc = {
            "download_url": url,
            "download_path": os.path.join(download_root, os.path.basename(url)),
            "status": TaskStatus.WAITING.value
        }
        sub_task_table.insert(doc)
        # 最后插入任务
        print('insert task')
        task = {
            "status": TaskStatus.WAITING.value,
            "_id": task_id
        }
        Task.insert_or_update(task)
        return _id
