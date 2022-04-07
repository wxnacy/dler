#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: task 模型

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DATETIME, Enum
from dler.models import Base, BaseDB
from dler.task.enums import TaskStatusEnum

class TaskModel(Base, BaseDB):
    __tablename__ = 'task'

    id = Column(String(32), primary_key=True)
    name = Column(String(128))
    url = Column(String(1024))
    path = Column(String(512))
    status = Column(String(16), default=TaskStatusEnum.WAITING.value)
    filetype = Column(String(16), default='')
    success_count = Column(Integer(), default=0)
    total_count = Column(Integer(), default=0)
    progress = Column(Float(), default=0)
    create_time = Column(DATETIME(), default=datetime.now)
    update_time = Column(DATETIME(), default=datetime.now)

class SubTaskModel(BaseDB, Base):
    __tablename__ = 'sub_task'

    id = Column(String(32), primary_key=True)
    task_id = Column(String(32))
    url = Column(String(1024))
    path = Column(String(512))
    status = Column(String(16), default=TaskStatusEnum.WAITING.value)

