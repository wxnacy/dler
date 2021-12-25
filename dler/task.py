#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from .downloaders import download_url

class Task(object):
    url = None

    sub_tasks = []

    def run(self):
        """运行任务"""

        for sub_task in self.sub_tasks:
            url = sub_task.get("url")
            path = sub_task.get("path")
            if sub_task.get("is_download"):
                continue
            is_downlaod = download_url(url, path)
            sub_task['is_downlaod'] = is_downlaod
