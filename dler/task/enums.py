#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: task 枚举模块

from wpy.base import BaseEnum

class TaskStatusEnum(BaseEnum):
    WAITING = 'waiting'
    SUCCESS = 'success'
    FAILED = 'failed'
    PROCESS = 'process'
    STOP = 'stop'
    SLEEP = 'sleep'

