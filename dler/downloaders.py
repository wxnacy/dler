#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

import os
import requests

from dler.loggers import get_logger

logger = get_logger('downloaders')

__all__ = ['download_url']


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
    logger.info('download {} status {}'.format(url, status_code))
    if status_code != 200:
        return False
    with open(path, 'wb') as f:
        f.write(res.content)
    return True


