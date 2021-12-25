#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""

from wsco import MessageHandler

class DownloadHandler(MessageHandler):

    def handle(self, request):
        print(request)
        return {}
