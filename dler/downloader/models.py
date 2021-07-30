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

#  class FSColumn(object):
    #  datatype = None
    #  default = None

    #  def __init__(self, datatype, **kwargs):
        #  self.datatype = datatype
        #  for k, v in kwargs.items():
            #  setattr(self, k, v)
        #  if self.default == None:
            #  if issubclass(datatype, int):
                #  self.default = 0

    #  def value(self):
        #  val = str(self.default()) if callable(self.default) else self.default
        #  if not val:
            #  val = self.datatype()
        #  return val

#  class FSModel(object):
    #  db = ''
    #  table = ''
    #  _db = None

    #  _id = FSColumn(str, default = uuid.uuid4)
    #  _create_time = FSColumn(datetime, default=datetime.now)
    #  _update_time = FSColumn(datetime, default=datetime.now)

    #  def __init__(self, **kwargs):
        #  init_data = self.__default_dict__()
        #  init_data.update(kwargs)
        #  for k, v in init_data.items():
            #  setattr(self, k, v)

    #  @classmethod
    #  def __default_dict__(cls):
        #  '''获取默认 dict'''
        #  res = {}
        #  classes = [cls]
        #  # 兼容父类的 __dict__
        #  classes.extend(cls.__bases__)
        #  for clz in classes:
            #  for k, v in clz.__dict__.items():
                #  if isinstance(v, FSColumn):
                    #  res[k] = v.value()
        #  return res

    #  @classmethod
    #  def db_col(cls, **kwargs):
        #  table = cls.table.format(**kwargs)
        #  return fs.get_db(cls.db).get_table(table)

    #  @classmethod
    #  def find_one_by_id(cls, _id, db_col=None):
        #  if not db_col:
            #  db_col = {}
        #  item = cls.db_col(**db_col).find_one_by_id(_id)
        #  return cls(**item) if item else None

    #  @classmethod
    #  def find(cls, query, db_col=None):
        #  if not db_col:
            #  db_col = {}
        #  items = cls.db_col(**db_col).find(query)
        #  return [cls(**item) for item in items]

    #  def save(self):
        #  data = self.__default_dict__()
        #  data.update(self.__dict__)
        #  db = self.db_col(**self.__dict__)
        #  item = db.find_one_by_id(self._id)
        #  if item:
            #  data.pop('_id', None)
            #  db.update({ "_id": self._id }, data)
        #  else:
            #  db.insert(data)

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
        #  cls.update_by_id(task_id, dict(
            #  success_count = success_count, total_count = total_count,
            #  progress = float('{:.2f}'.format(float(success_count) / total_count)
        #  )))
        task.save()
        return task

    @property
    def is_success(self):
        return self.status == TaskStatus.SUCCESS.value

    @classmethod
    def update_status(cls, task_id, status):
        cls.db_col().update({ "_id": task_id }, { "status": status })

    #  @classmethod
    #  def find_one_by_id(cls, task_id):
        #  item = cls.db_col().find_one_by_id(task_id)
        #  if not item:
            #  return item
        #  return cls(**item)

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
        items = cls.db_col(task_id = task_id).find()
        return [cls(**o) for o in items if o.get("status") not in (
            TaskStatus.SUCCESS.value, TaskStatus.PROCESS.value)]

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
