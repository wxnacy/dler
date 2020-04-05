#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler.config import celery
from pydler import tasks

def run():
    celery.worker_main()

if __name__ == "__main__":
    run()
