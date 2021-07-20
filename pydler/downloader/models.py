#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from wpy.db import FileStorage

fs = FileStorage('~/Downloads/db')

class BaseModel(object):
    db = 'm3u8'
    table = ''
    _db = None

    @classmethod
    def db_col(cls, **kwargs):
        table = cls.table.format(**kwargs)
        return fs.get_db(cls.db).get_table(table)

class Task(BaseModel):
    table = 'task'

    @classmethod
    def update_status(cls, task_id, status):
        cls.db_col().update({ "_id": task_id }, { "status": status })


class SubTask(BaseModel):
    table = 'sub_task-{task_id}'

    @classmethod
    def update_status(cls, task_id, sub_task_id, status):
        cls.db_col(task_id = task_id).update({ "_id": sub_task_id },
            { "status": status })

    @classmethod
    def count_status(cls, task_id, status):
        return cls.db_col(task_id = task_id).count({ "status": status })
