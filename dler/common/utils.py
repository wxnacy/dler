#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import os
from wpy.functools import run_shell

def proxyon():
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

def proxyoff():
    os.environ['https_proxy'] = ''
    os.environ['http_proxy'] = ''
    os.environ['all_proxy'] = ''

def cmd_count(cmd):
    res, _ = run_shell('ps -ef | grep {} | wc -l'.format(cmd))
    now_process_count = 0
    try:
        now_process_count = int(res.decode('utf-8').strip().strip('\n')) - 2
    except:
        pass
    return now_process_count

def dlm3_count():
    return cmd_count('bin/dlm3')

def download_url(url, path):
    """下载 url 到指定路径"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 "
            "Safari/537.36",
    }
    path = os.path.expanduser(path)
    if os.path.exists(path):
        return True
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    res = requests.get(url, headers = headers)
    status_code = res.status_code
    #  logger.info('download {} status {}'.format(url, status_code))
    if status_code != 200:
        return False
    with open(path, 'wb') as f:
        f.write(res.content)
    return True
