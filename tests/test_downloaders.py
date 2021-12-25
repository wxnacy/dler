#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import os
import requests
from random import randint

from dler.downloaders import download_url

def test_download_url():
    url = 'https://wxnacy.com/'
    path = f'/tmp/{randint(1, 1000)}'
    assert download_url(url, path)

    assert len(requests.get(url).content) == os.path.getsize(path)

