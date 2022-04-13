#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: m3u8 tasker

from multitasker import MultiTasker, SubTaskModel

import os
import json
import m3u8
from typing import List
from pydantic import BaseModel

from dler.downloaders import download_url


class DownloadTask(BaseModel):
    url: str
    path: str


class M3u8Tasker(BaseModel, MultiTasker):
    download_dir: str = ""

    url: str
    #  video_id: str = ""

    class Config:
        task_type: str = 'm3u8'
        #  download_dir: str = os.path.expanduser('~/Downloads')
        download_dir: str = os.path.expanduser('/Users/wxnacy/Downloads/website/static/jable/m3u8')

    def build_task(self) -> dict:
        detail = {}
        if self.url:
            detail['url'] = self.url
            self.download_dir = self.build_download_dir()

        return {}

    def build_sub_tasks(self) -> List[SubTaskModel]:

        sub_tasks = []
        if self.url:
            sub_tasks.append(self.build_main_sub_task())
            for ts_url in self.generate_ts_paths():
                _path = os.path.join(self.download_dir,
                    os.path.basename(ts_url))
                detail = DownloadTask(url = ts_url, path = _path).dict()
                st = SubTaskModel(detail = detail, task_type = 'download_ts')
                sub_tasks.append(st)
            return sub_tasks

        return []

    def build_main_sub_task(self) -> SubTaskModel:
        _path = os.path.join(self.download_dir,
            os.path.basename(self.url))
        detail = DownloadTask(url = self.url, path = _path).dict()
        return SubTaskModel(detail = detail, task_type = 'download_ts')


    def build_download_dir(self):
        dl_dir = os.path.join(self.Config.download_dir,
            os.path.basename(self.url).split('.')[0])
        if not os.path.exists(dl_dir):
            os.mkdir(dl_dir)
        return dl_dir

    def generate_ts_paths(self):
        m3 = m3u8.load(self.url)
        for i, name in enumerate(m3.files):
            if not name:
                continue
            ts_url = name
            if not ts_url.startswith('http'):
                ts_url = os.path.join(m3.base_uri, ts_url)
            print(i, ts_url)
            yield ts_url


@M3u8Tasker.trigger_sub_task('download_ts')
def sub_task_download_ts(sub_task) -> bool:
    #  return True
    task = DownloadTask(**sub_task.detail)
    #  print(task.download_path)
    #  path = os.path.basename(task.download_path)
    #  path = os.path.expanduser('~/Downloads/dltest/') + path
    path = task.path
    #  print(path)
    return download_url(task.url, path)


if __name__ == "__main__":
    import time
    import sys
    args = sys.argv[1:]
    video_id = args[0]
    tasker = M3u8Tasker(url = video_id)
    tasker.build()
    b = time.time()
    tasker.run()
    print(time.time() - b)


