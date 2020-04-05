#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from celery import Celery
import typer
import os
import redis

HOME = os.getenv("HOME")
CONF_DIR = f'{HOME}/.config/pydler'
ARCHIVE = f'{CONF_DIR}/archive'
QUEUE = f'{CONF_DIR}/queue'
QUEUE_DIR = f'{CONF_DIR}/queue_files'
DL_DIR= os.getenv("PYDLER_DLDIR") or f'{HOME}/Downloads'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = os.getenv("PYDLER_REDIS_DB") or 6


def init():
    '''初始化文件和配置'''
    if not os.path.exists(CONF_DIR):
        os.makedirs(CONF_DIR)
    if not os.path.exists(QUEUE_DIR):
        os.makedirs(QUEUE_DIR)


def make_celery():
    conf = {
        'CELERY_BROKER_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'CELERY_RESULT_BACKEND': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    }
    celery = Celery('pydler', broker=conf['CELERY_BROKER_URL'])
    celery.conf.update(conf)
    return celery

init()

echo = typer.echo
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
db = redis.Redis(connection_pool=pool)
celery = make_celery()
