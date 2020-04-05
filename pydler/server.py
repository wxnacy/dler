#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler import config
from pydler.config import celery
from pydler import tasks

def run():
    print(f'下载目录：{config.DL_DIR}')
    celery.worker_main()

if __name__ == "__main__":
    run()
