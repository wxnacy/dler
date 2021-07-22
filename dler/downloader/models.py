#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os
from wpy.db import FileStorage

from .enum import TaskStatus

fs = FileStorage('~/Downloads/db')

class BaseModel(object):
    db = 'm3u8'
    table = ''
    _db = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def db_col(cls, **kwargs):
        table = cls.table.format(**kwargs)
        return fs.get_db(cls.db).get_table(table)

class Task(BaseModel):
    table = 'task'

    _id = ''
    url = ''
    status = ''

    @property
    def is_success(self):
        return self.status == TaskStatus.SUCCESS.value

    @classmethod
    def update_status(cls, task_id, status):
        cls.db_col().update({ "_id": task_id }, { "status": status })

    @classmethod
    def find_one_by_id(cls, task_id):
        item = cls.db_col().find_one_by_id(task_id)
        if not item:
            return item
        return cls(**item)

    def find_sub_tasks(self, query=None):
        items = SubTask.db_col(task_id = self._id).find(query)
        return [SubTask(**o) for o in items if o]

class SubTask(BaseModel):
    table = 'sub_task-{task_id}'

    _id = ''
    task_id = ''
    download_url = ''
    download_path = ''
    status = ''

    @classmethod
    def update_status(cls, task_id, sub_task_id, status):
        cls.db_col(task_id = task_id).update({ "_id": sub_task_id },
            { "status": status })

    @classmethod
    def count_status(cls, task_id, status):
        return cls.db_col(task_id = task_id).count({ "status": status })

    @classmethod
    def find_not_success_items(cls, task_id):
        items = cls.db_col(task_id = task_id).find()
        return [cls(**o) for o in items if o.get("status") not in (
            TaskStatus.SUCCESS.value, TaskStatus.PROCESS.value)]

    def is_success(self):
        if self.status == TaskStatus.SUCCESS.value:
            return True
        return os.path.exists(self.download_path)
