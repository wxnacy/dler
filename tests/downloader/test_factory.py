#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from dler.downloader import DownloaderFactory
from dler.downloader.image_downloader import ImageDownloader
from dler.downloader.m3u8_downloader import M3u8Downloader
from dler.downloader.enum import FileType

def test_get_downloader():
    Downloader = DownloaderFactory.get_downloader(FileType.M3U8.value)
    assert issubclass(Downloader, M3u8Downloader)

    Downloader = DownloaderFactory.get_downloader(FileType.IMAGE.value)
    assert issubclass(Downloader, ImageDownloader)

    Downloader = DownloaderFactory.get_downloader('none')
    assert Downloader == None

def test_get_downloader():
    url = 'https://hls.videocc.net/f8f97d17d0/d/f8f97d17d0a21f1a1d84d214c5dcbfdd_1.m3u8'
    Downloader = DownloaderFactory.get_downloader_by_url(url)
    assert issubclass(Downloader, M3u8Downloader)

    Downloader = DownloaderFactory.get_downloader_by_url(FileType.M3U8.value)
    assert issubclass(Downloader, M3u8Downloader)

    Downloader = DownloaderFactory.get_downloader_by_url(FileType.IMAGE.value)
    assert issubclass(Downloader, ImageDownloader)

    Downloader = DownloaderFactory.get_downloader('none')
    assert Downloader == None
