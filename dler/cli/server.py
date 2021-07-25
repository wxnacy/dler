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
import gevent

from flask import Flask
from flask import request

import logging

from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.common.loggers import create_logger

app = Flask(__name__)

logger = create_logger('dler')

@app.route('/api/task/<string:task_id>/sub_task/<string:sub_id>/download')
def sub_task_download(task_id, sub_id):
    downloader = M3u8Downloader(task_id)
    gevent.spawn(downloader.download_sub_task, sub_id)
    return 'success'

@app.route('/test', methods=['post', 'get'])
def test():
    #  logging.info('test')
    logger.info('test')
    res = {
        "args": request.args,
        "json": request.json,
        "data": str(request.data),
        "headers": dict(request.headers),
    }
    import time
    time.sleep(3)
    return res

def run_server(port=None):
    if not port:
        port = PORT
    app.run(host = '0.0.0.0', port=port)
    return app

def start_gunicorn():
    import dler
    module_path = dler.__path__[0]
    config_path = os.path.join(module_path, 'cli/gunicorn_config.py')
    os.system('nohup gunicorn -c {} dler.cli.server:app >/tmp/dler.log 2>&1 &'.format(config_path))

def stop_gunicorn():
    os.system("nohup ps -ef | grep 'gunicorn.*dler' | awk '{ print $2 }' | xargs kill -9 >/tmp/dler.log 2>&1 &")

def run_with_gunicorn():
    import sys
    cmd = 'start'
    try:
        cmd = sys.argv[1:][0]
    except:
        pass
    if cmd == 'start':
        start_gunicorn()
    elif cmd == 'stop':
        stop_gunicorn()
    else:
        stop_gunicorn()
        start_gunicorn()

if __name__ == "__main__":
    run_server()
