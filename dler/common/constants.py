#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os

SERVER_PORT = 5002
SERVER_DOMAIN = '0.0.0.0'
SERVER_HOMEPAGE = 'http://{}:{}'.format(SERVER_DOMAIN, SERVER_PORT)
MAX_TASK_PROCESS = 2
MAX_SUB_TASK_PROCESS = 8

OLD_TASK_DIR = os.path.expanduser('~/.lfsdb/data/download')
