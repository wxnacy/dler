#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os

__all__ = ['Constants']

class Constants():
    SERVER_PORT = 60609
    SERVER_HOST = 'localhost'
    MAX_TASK_PROCESS = 2
    MAX_SUB_TASK_PROCESS = 8
    DOWNLOAD_DIR = os.path.expanduser('~/Downloads')
    DB_PATH = os.path.expanduser('~/.dler.db')