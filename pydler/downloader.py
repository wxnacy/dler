#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

'''

https://mmxzxl1.com/common/new/zw/2018-04/28/w8vb6ued.mp4
https://s1.maomibf1.com/common/new/zw/2018-04/28/w8vb6ued/w8vb6ued.m3u8
https://mmxzqxl1.com/common/all/201906/PBxFHaCc/PBxFHaCc.rmvb
https://s1.maomibf1.com/common/all/201906/PBxFHaCc.m3u8
'''
import os
import ffmpeg
from pydler import config

def parse_maomi_url(url):
    '''解析地址'''
    url = url.replace('www.mmxzxl1.com', 'mmxzxl1.com')
    url = url.replace('mmxzxl1.com', 's1.maomibf1.com')
    url = url.replace('.mp4', '')
    basename = os.path.basename(url)
    url = url.replace(basename, f'{basename}/{basename}.m3u8')

    return url

def download_m3u8(url):
    '''下载 m3u8'''
    basename = os.path.basename(url).replace('.m3u8', '.mp4')
    filepath = f'{config.DL_DIR}/{basename}'
    ffmpeg.input(url).output(filepath).run()


if __name__ == "__main__":
    url = 'https://mmxzxl1.com/common/new/zw/2018-04/28/w8vb6ued.mp4'
    res = parse_maomi_url(url)
    print(res)
    download_m3u8(res)
    
