#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import os

def proxyon():
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

def proxyoff():
    os.environ['https_proxy'] = ''
    os.environ['http_proxy'] = ''
    os.environ['all_proxy'] = ''
