#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: m3u8 tasker

from multitasker import MultiTasker, SubTaskModel
import requests

import os
import shutil
import time
from typing import List
from pydantic import BaseModel, Field

from dler.downloaders import download_url
from dler.constants import SEGMENT_SIZE
from .base import BaseConfig, BaseTasker
from .models import (
    DownloadTaskModel,
    MergeTaskModel
)
from . import tasktools

class HeaderModel(BaseModel):
    content_length: int = Field(..., alias='Content-Length')
    accept_ranges: str = Field(None, alias='Accept-Ranges')


class FileDetailModel(BaseModel):
    headers: HeaderModel


class FileTasker(MultiTasker, BaseTasker):
    filepath: str
    #  download_dir: str
    cache_dir: str
    detail: FileDetailModel

    class Config(BaseConfig):
        task_type: str = 'video'

    def build_task(self) -> dict:
        detail = {}

        #  filename = 'test'
        filename = self.filename or os.path.basename(self.url)
        self.cache_dir = os.path.join(self.Config.download_dir,
            f'.dler/{filename}')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        res = requests.head(self.url)
        headers = dict(res.headers)
        header = HeaderModel(**headers)
        self.detail = FileDetailModel(headers = header)
        self.filepath = os.path.join(self.Config.download_dir, filename)

        return self.detail.dict()

    def build_sub_tasks(self) -> List[SubTaskModel]:

        sub_tasks = []
        headers = self.detail.headers
        if headers.accept_ranges == 'bytes':
            length = headers.content_length
            merge_files = []
            total_page = int(length / SEGMENT_SIZE) + 1
            # 分拆下载子任务
            for i in range(total_page):
                begin = i * SEGMENT_SIZE
                if begin >= length:
                    break
                end = (i + 1) * SEGMENT_SIZE - 1
                if end >= length:
                    end = length - 1

                header_range = f'bytes={begin}-{end}'
                path = os.path.join(self.cache_dir, f'{begin}-{end}')

                sub_detail = DownloadTaskModel(url = self.url, path = path,
                    headers = { "Range": header_range })
                sub_task = SubTaskModel(
                    task_type = 'download', detail = sub_detail.dict())
                sub_tasks.append(sub_task)
                merge_files.append(path)

            # 增加 merge 子任务
            merge_task = MergeTaskModel(
                filepath = self.filepath, merge_files = merge_files,
                cache_dir = self.cache_dir
            )
            sub_tasks.append(SubTaskModel(
                task_type = 'merge', detail = merge_task.dict()
            ))

        return sub_tasks


FileTasker.trigger_sub_task('download')(tasktools.download)

@FileTasker.trigger_sub_task('merge')
def sub_task_merge(sub_task) -> bool:
    task = MergeTaskModel(**sub_task.detail)
    merge_map = {}

    while len(merge_map) != len(task.merge_files):
        for merge_file in task.merge_files:
            if os.path.exists(merge_file):
                merge_map[merge_file] = True

        print(len(merge_map))
        time.sleep(1)

    with open(task.filepath, 'wb') as wf:
        for merge_file in task.merge_files:
            print(merge_file)
            with open(merge_file, 'rb') as rf:
                wf.write(rf.read())

    shutil.rmtree(task.cache_dir)
    return True
