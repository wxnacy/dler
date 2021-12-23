#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""
服务端
"""

import time
from multiprocessing import Process

from .sockets import Client
from .sockets import Server
from .loggers import get_logger

logger = get_logger(__name__)

def heart():
    while True:
        time.sleep(2)

def main():
    Command().run()

class Command(object):

    def _heart(self):
        """发起一次心跳，并返回服务是否正常运行"""
        try:
            c = Client()
            c.connect()
            res = c.heart()
            c.close()
            return res.code == 0
        except:
            return False

    def stop(self):
        """停止服务"""
        try:
            c = Client()
            c.connect()
            c.stop_server()
            c.close()
        except:
            pass
        print('服务停止')

    def status(self):
        """查看服务状态"""
        is_start = self._heart()
        if is_start:
            print('服务状态：运行中')
        else:
            print('服务状态：已停止')


    def restart(self):
        """重启服务"""
        self.stop()
        self.start()

    def start(self):
        """运行服务"""
        is_start = self._heart()
        if is_start:
            print('服务已经在运行')
            return

        p = Process(target=heart)
        p.daemon = True
        p.start()

        Server().run()

    def run(self):
        import sys
        args = sys.argv[1:]
        typ = 'start'
        if args:
            typ = args[0]
        func_name = typ
        getattr(self, func_name)()

if __name__ == "__main__":
    main()
