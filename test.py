#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from dler.downloader.models import BaseModel
from dler.downloader.models import Task
from dler.downloader.models import SubTask
from dler.downloader.m3u8_downloader import TaskStatus


if __name__ == "__main__":
    import json
    #  task = Task(_id = 1)
    #  print(BaseModel.__default_dict__())
    #  print(task.__dict__)
    #  print(Task.__default_dict__())
    #  print(Task.__dict__)
    tasks = [Task(**o) for o in Task.db_col().find({})]
    tasks.sort(key = lambda x: x.success_count, reverse=True)
    for task in tasks:
        print(task._id, task.success_count, task.status)
        #  #  print(task)
        #  task = Task(**task)
        #  print(task._id, task.status)
        #  Task.update_status(task._id, TaskStatus.WAITING.value)
        #  SubTask.db_col(task_id = task._id).update({}, { "status": TaskStatus.WAITING.value })
        #  #  print(task)
