#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
下载器装饰器
"""

_register_dict = {}

from dler.common.loggers import create_logger

logger = create_logger('decorates')

def downloader_register(active=True):
    def decorate(func):
        logger.info('register active=%s func %s.%s', active, func.__module__,
            func)
        #  print('running register(active=%s)->decorate(%s)'
                #  % (active, func))
        if isinstance(func, str):
            raise Exception('test')
        if active:
            _register_dict[func.filetype] = func
        else:
            _register_dict.pop(func.filetype, None)

        return func
    return decorate

def get_downloaders():
    return dict(_register_dict)
