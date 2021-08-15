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
