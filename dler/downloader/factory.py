#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
from dler.common.loggers import create_logger

from .decorates import get_downloaders
from .enum import FileType

class DownloaderFactory(object):

    @classmethod
    def get_downloader(cls, filetype):
        """获取下载器"""
        flag = FileType.is_valid(filetype)
        if not flag:
            return None
        Downloader = get_downloaders().get(filetype) or None
        return Downloader

    @classmethod
    def get_downloader_by_url(cls, url):
        """根据地址获取下载器"""
        filetype = FileType.get_filetype_by_url(url)
        return cls.get_downloader(filetype)
