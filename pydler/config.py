#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import typer
import os
import redis

HOME = os.getenv("HOME")
CONF_DIR = f'{HOME}/.config/pydler'
ARCHIVE = f'{CONF_DIR}/archive'
QUEUE = f'{CONF_DIR}/queue'
QUEUE_DIR = f'{CONF_DIR}/queue_files'
DL_DIR=f'{HOME}/Downloads'

#  YDL_ARCHIVE=f'{HOME}/.pydler-archive'
#  YDL_OPTS = {
    #  "proxy": "127.0.0.1:1080",
    #  #  "download_archive": YDL_ARCHIVE,
    #  "outtmpl": f"{DL_DIR}/%(title)s.%(ext)s"
#  }

def init():
    '''初始化文件和配置'''
    if not os.path.exists(CONF_DIR):
        os.makedirs(CONF_DIR)
    if not os.path.exists(QUEUE_DIR):
        os.makedirs(QUEUE_DIR)

init()

echo = typer.echo

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
db = redis.Redis(connection_pool=pool)
