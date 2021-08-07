#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os
import uuid
from lfsdb import FileStorage
from lfsdb import FSModel
from lfsdb import FSColumn
from datetime import datetime

from .enum import TaskStatus

fs = FileStorage()

class BaseModel(FSModel):
    db = 'download'
    table = ''
    _db = None

    @classmethod
    def iter(cls, col, query, projection=None, sort=None):
        if not col:
            col = {}
        items = cls.db_col(**col).find(query, projection = projection)
        items = [cls(**o) for o in items]
        return items

    def insert_ins(self):
        '''保存实例'''
        doc = dict(self.__dict__)
        doc.pop('table', None)
        _id = self.db_col().insert(doc)
        self._id = _id

    def insert_or_update_ins(self):
        '''保存实例'''
        doc = dict(self.__dict__)
        doc.pop('table', None)
        _id = self._id
        item = self.db_col().find_one_by_id(_id)
        if item:
            doc.pop('_id', None)
            self.db_col().update({ "_id": _id }, doc)
        else:
            self.db_col().insert(doc)

class Task(BaseModel):
    table = 'task'

    _id = ''
    url = FSColumn(str, )
    status = FSColumn(str, default=TaskStatus.WAITING.value)
    filetype = FSColumn(str, )
    success_count = FSColumn(int, )
    total_count = FSColumn(int, )
    progress = FSColumn(float, default=0)

    @classmethod
    def check_and_update_progress(cls, task_id):
        task = cls.find_one_by_id(task_id)
        if not task:
            return None
        subtasks = SubTask.find({}, db_col = { "task_id": task_id })
        success_count = 0
        for sub in subtasks:
            #  total_count += 1
            sub.check_and_update_status()
            if sub.status == TaskStatus.SUCCESS.value:
                success_count += 1
        task.success_count = success_count
        task.progress = float('{:.2f}'.format(float(success_count) / task.total_count))
        task.save()
        return task

    @property
    def is_success(self):
        return self.status == TaskStatus.SUCCESS.value

    @classmethod
    def update_status(cls, task_id, status):
        cls.db_col().update({ "_id": task_id }, { "status": status })

    def find_sub_tasks(self, query=None):
        items = SubTask.db_col(task_id = self._id).find(query)
        return [SubTask(**o) for o in items if o]

    @classmethod
    def insert_or_update(cls, doc):
        """插入或更新"""
        _id = doc.get("_id")
        item = cls.db_col().find_one_by_id(_id)
        if item:
            doc.pop('_id', None)
            cls.db_col().update({ "_id": _id }, doc)
        else:
            cls.db_col().insert(doc)

    @classmethod
    def count_status(cls, status):
        return cls.db_col().count({ "status": status })

    @classmethod
    def update_by_id(cls, task_id, update_data):
        return cls.db_col().update({ "_id": task_id }, update_data)

    @classmethod
    def find_need_download_tasks(cls, work_ids=None):
        """查找需要下载的任务列表"""
        if not work_ids:
            work_ids = []
        work_ids = [str(o) for o in work_ids]
        query = {
            #  "_id": { "$nin": list(work_ids) },
            "status": { "$in": [
                TaskStatus.WAITING.value,
                TaskStatus.PROCESS.value,
                TaskStatus.STOP.value,
                ] }
        }
        items = cls.find(query, sorter = [('success_count', -1)])
        items = list(filter(lambda x: x._id not in work_ids, items))
        return items

class SubTask(BaseModel):
    table = 'sub_task-{task_id}'

    task_id = FSColumn(str, )
    proxyon = FSColumn(bool, default = False)
    download_url = FSColumn(str, )
    download_path = FSColumn(str, )
    status = FSColumn(str, default=TaskStatus.WAITING.value)

    @classmethod
    def update_status(cls, task_id, sub_task_id, status):
        cls.db_col(task_id = task_id).update({ "_id": sub_task_id },
            { "status": status })

    @classmethod
    def count_status(cls, task_id, status):
        return cls.db_col(task_id = task_id).count({ "status": status })

    @classmethod
    def find_not_success_items(cls, task_id):
        query = { "status": TaskStatus.WAITING.value }
        items = cls.find(query, db_col={ "task_id": task_id })
        return items

    def is_success(self):
        if self.status == TaskStatus.SUCCESS.value:
            return True
        return os.path.exists(self.download_path)

    def check_and_update_status(self):
        if self.status == TaskStatus.SUCCESS.value:
            return
        if os.path.exists(self.download_path):
            self.status = TaskStatus.SUCCESS.value
            self.save()
