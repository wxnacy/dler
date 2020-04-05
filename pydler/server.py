#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from pydler.config import celery
from pydler import tasks

if __name__ == "__main__":
    celery.worker_main()
