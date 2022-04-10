#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: m3u8 tasker

from multitasker import MultiTasker, SubTaskModel

import os
import shutil
import json
from typing import List
from pydantic import BaseModel

from wpy.base import BaseEnum

class FSActionEnum(BaseEnum):
    COPY = 'copy'
    MOVE = 'move'


class FileSystemTasker(BaseModel, MultiTasker):

    action: str
    from_file: str
    to_file: str

    class Config:
        task_type = 'filesystem'

    def build_task(self) -> dict:

        return {}

    def build_sub_tasks(self) -> List[SubTaskModel]:
        func_name = f"build_{self.action}_sub_tasks"
        func = getattr(self, func_name)
        return func()

    def build_copy_sub_tasks(self) -> List[SubTaskModel]:
        if not os.path.exists(self.from_file):
            raise RuntimeError(f'File {self.from_file} is not exists')

        if os.path.exists(self.to_file) and os.path.isfile(self.to_file):
            raise RuntimeError(f"File {self.to_file} is exists")

        if os.path.isdir(self.from_file):
            to_dir = self.to_file
            if os.path.exists(self.to_file):
                to_dir = os.path.join(self.to_file, os.path.basename(self.from_file))
            if not os.path.exists(to_dir):
                os.mkdir(to_dir)

            sub_tasks = []
            for name in os.listdir(self.from_file):
                from_path = os.path.join(self.from_file, name)
                to_path = os.path.join(to_dir, name)

                sub_task = SubTaskModel(task_type = 'copy_copy',
                    detail = {"from_path": from_path, "to_path": to_path})
                sub_tasks.append(sub_task)
            return sub_tasks


        return []

class FSModel(BaseModel):
    from_path: str
    to_path: str

@FileSystemTasker.trigger_sub_task('copy_copy')
def sub_task_copy_copy(sub_task) -> bool:
    print(sub_task.detail)
    fs = FSModel(**sub_task.detail)

    shutil.copy(fs.from_path, fs.to_path)
    #  shutil.move()
    return True

if __name__ == "__main__":
    import time
    import sys
    args = sys.argv[1:]
    #  video_id = args[0]
    tasker = FileSystemTasker(action = 'copy',
        from_file = os.path.expanduser('~/Downloads/dltest'),
        to_file = '/tmp/test/dlt'
    )
    tasker.build()
    b = time.time()
    tasker.run()
    print(time.time() - b)


