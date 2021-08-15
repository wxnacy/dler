#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from dler.downloader.models import Task

def main():
    import sys
    status = sys.argv[1:][0]
    task_id = sys.argv[1:][1]
    Task.update_status(task_id, status)
