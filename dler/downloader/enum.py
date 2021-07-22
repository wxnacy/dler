#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from enum import Enum

class TaskStatus(Enum):
    WAITING = 'waiting'
    SUCCESS = 'success'
    FAILED = 'failed'
    PROCESS = 'process'
    STOP = 'stop'
    SLEEP = 'sleep'
