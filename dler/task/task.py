#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description:


import os
import json
from dler.common import constants
from dler.multi_worker.multi_worker import MultiWorker
from dler.task.models import SubTaskModel

class Task():
    def __init__(self, task_id):
        self.task_id = task_id


    def find_sub_tasks(self):
        dirname = f'{constants.OLD_TASK_DIR}/sub_task-{self.task_id}'
        items = []
        for name in os.listdir(dirname):
            path = os.path.join(dirname, name)
            data = self._read(path)
            items.append(data)
        return items

    def _read(self, path):
        with open(path) as f:
            return json.loads(''.join(f.readlines()))

    def find_sub_task(self, sub_task_id):
        path = f'{constants.OLD_TASK_DIR}/sub_task-{self.task_id}/{sub_task_id}'
        return self._read(path)

    def _conver_sub_task(self, sub_task):
        data = {}
        old_keys, new_keys = (
                ('_id', 'download_url', 'download_path', 'status'),
                ('id', 'url', 'path', 'status'))
        for i, old_key in enumerate(old_keys):
            data[new_keys[i]] = sub_task.get(old_key)

        data['task_id'] = self.task_id
        return SubTaskModel(**data)

    def run(self):
        """

        """
        mw = MultiWorker()
        sub_tasks = self.find_sub_tasks()
        for sub_task in sub_tasks:
            sub_task = self._conver_sub_task(sub_task)
            print(sub_task.dict())
            #  sub_task = SubTask(**sub_task)
            #  mw.add_work(download_task, task_id, sub_task._id)
        #  mw.run()
        #  mw.print_response()



if __name__ == "__main__":
    task = Task('18580')
    task.run()
