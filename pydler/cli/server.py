#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
from gevent import monkey
monkey.patch_all()
#  monkey.patch_all(ssl=False)
import json
import os
import logging
#  import gevent
import requests
from enum import Enum

from flask import Flask
from flask import request

from wpy.db import FileStorage
from wpy.tools import randoms
import logging

app = Flask(__name__)

db = FileStorage('~/Downloads/db').get_db('m3u8')
task_table = db.get_table('task')

class CustomerFilter(logging.Filter):

    def filter(self, record):
        if ':' not in record.filename:
            record.filename = '{}:{}'.format( record.filename, record.lineno)
        return True

logging.basicConfig(
    #  filename='/tmp/wpy.log',
    format="[%(asctime)s] [%(levelname)-5s] [%(filename)-20s] %(message)s",
    level=logging.DEBUG
)

def create_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(CustomerFilter())
    return logger

logger = create_logger('pydler')

class TaskStatus(Enum):
    WAITING = 'waiting'
    SUCCESS = 'success'
    FAILED = 'failed'
    PROCESS = 'process'
    STOP = 'stop'

def download(url, path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
    }
    if os.path.exists(path):
        return True
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    res = requests.get(url, headers = headers)
    status_code = res.status_code
    if status_code != 200:
        return False
    with open(path, 'wb') as f:
        f.write(res.content)
    return True

@app.route('/api/task/<string:task_id>/sub_task/<string:sub_id>/download')
def sub_task_download(task_id, sub_id):
    sub_task_table = db.get_table('sub_task-{}'.format(task_id))

    doc = sub_task_table.find_one_by_id(sub_id)

    status = TaskStatus.SUCCESS.value
    try:
        flag = download(doc.get("download_url"), doc.get("download_path"))
    except Exception as e:
        import traceback
        logger.info(traceback.format_exc())
        flag = False
        status = TaskStatus.FAILED.value
        sub_task_table.update({ "_id": sub_id },
            { "status": status, "error": str(e) })
    if flag:
        status = TaskStatus.SUCCESS.value
    else:
        status = TaskStatus.FAILED.value
    sub_task_table.update({ "_id": sub_id }, { "status": status})
    return status

@app.route('/test', methods=['post', 'get'])
def test():
    logging.info('test')
    print('test')
    res = {
        "args": request.args,
        "json": request.json,
        "data": str(request.data),
        "headers": dict(request.headers),
    }
    import time
    time.sleep(3)
    return res

PORT = 12000 + int(randoms.random_int(3, 1))
app.debug= True

def run_server(port=None):
    if not port:
        port = PORT
    app.run(host = '0.0.0.0', port=port)

if __name__ == "__main__":
    run_server()
