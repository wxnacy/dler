#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""
socket 模块
"""

import socket               # 导入 socket 模块
import signal
import json
import traceback
import pickle

from threading import Event

from wpy.base import BaseObject
from wpy.base import BaseEnum
from dler.loggers import get_logger

done_event = Event()

def handle_sigint(signum, frame):
    done_event.set()

signal.signal(signal.SIGINT, handle_sigint)

class ServerStopException(Exception):
    """服务停止的异常"""
    pass

# 获取本机主机名
localhost = socket.gethostname()

class SocketConstants(object):
    PORT = 60609
    HOST = localhost

    FRAGMENT_SIZE = 16 * 1024 * 1024

class Client(object):
    logger = get_logger('SocketClient')

    def __init__(self, *args, **kwargs):
        self.socket = socket.socket()

    def connect(self):
        self.socket.connect(
            (SocketConstants.HOST, SocketConstants.PORT)
        )

    def exec(self, db, table, method, params):
        """执行"""
        basic_params = locals()
        basic_params.pop('self', None)
        sq = SocketRequest(**basic_params)
        self.socket.send(sq.dumps())

        res = self.receive_message()
        print(res.data, type(res.data))
        return res

    def stop_server(self):
        """停止服务"""
        data = SocketRequest().build_stop().dumps()
        self.socket.send(data)
        res = self.receive_message()
        print(res.data)
        return res

    def heart(self):
        """发送心跳信息"""
        data = SocketRequest().build_heart().dumps()
        self.socket.send(data)
        return self.receive_message()

    def close(self):
        self.socket.close()

    def receive_message(self):
        """接收消息"""
        data = b''
        while True:
            fragment = self.socket.recv(SocketConstants.FRAGMENT_SIZE)
            if not fragment:
                break
            data += fragment
        self.logger.debug('接收服务端信息 %s', data)
        res = SocketResponse.loads(data)
        self.logger.debug('接收服务端信息 %s', res.to_dict())
        return res


class PickleModel(BaseObject):

    def dumps(self):
        '''序列化'''
        return pickle.dumps(self.to_dict())

    @classmethod
    def loads(cls, bytes_data):
        """加载"""
        data = pickle.loads(bytes_data)
        return cls(**data)

class SRAction(BaseEnum):
    EXEC = 'exec'   # 执行语句
    STOP = 'stop'   # 停止服务
    HEART = 'heart' # 心跳监听


class SocketRequest(PickleModel):
    logger = get_logger('SocketRequest')
    _db_dict = {}

    action = SRAction.EXEC.value
    db = None
    table = None
    method = None
    params = None

    def is_stop(self):
        """是否为停止"""
        return self.action == SRAction.STOP.value

    def is_heart(self):
        """是否为心跳信息"""
        return self.action == SRAction.HEART.value

    def is_unkown(self):
        """是否不明确的信息"""
        return self.action not in SRAction.values()

    @classmethod
    def build_stop(cls):
        return cls(action = SRAction.STOP.value)

    @classmethod
    def build_heart(cls):
        return cls(action = SRAction.HEART.value)

    def get_db(self):
        """获取数据库"""
        key = '{}-{}'.format(self.db, self.table)
        if key not in self._db_dict:
            self._db_dict[key] = FileStorage(None).get_db(self.db
                ).get_table(self.table)
        return self._db_dict[key]

    def run(self):
        """运行结果"""
        data = getattr(self.get_db(), self.method)(**self.params)
        print(data)
        return SocketResponse(data = data)

class SocketResponse(PickleModel):
    code = 0
    data = None
    e = None
    error_name = None

    def json(self):
        """将数据格式化为 dict 结构"""
        if isinstance(self.data, dict) or \
                isinstance(self.data, list):
            return self.data
        else:
            try:
                return json.loads(self.data)
            except:
                return None
        return None

    @classmethod
    def build_unkown(cls):
        """构建 unkown 回复"""
        return cls(code = 1, data='unkown message')

    @classmethod
    def build_error(cls, e):
        return cls(code = 1, error_name = e.NAME, data = str(e))



class Server(object):
    logger = get_logger('SockerServer')

    def __init__(self, *args, **kwargs):
        self.socket = socket.socket()

    def run(self):
        """运行服务
        """
        print("开始运行服务")
        # 处理 TCP 断开后端口占用问题
        # https://blog.csdn.net/Jason_WangYing/article/details/105420659
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.socket.bind(
            (SocketConstants.HOST, SocketConstants.PORT)
        )
        self.socket.listen(5)

        while True:
            if done_event.is_set():
                print('服务停止')
                break
            try:
                self.accept()
            except ServerStopException:
                break
            except:
                print(traceback.format_exc())
                print(traceback.format_stack())

    def accept(self):
        """接收客户端信息"""
        c,addr = self.socket.accept()     # 建立客户端连接
        print('连接地址：', c, addr)
        self._accept(c)
        #  except LfsdbError as e:
            #  self.logger.error(traceback.format_exc())
            #  self.logger.error(traceback.format_stack())
            #  c.send(SocketResponse.build_error(e).dumps())
        c.close()                # 关闭连接

    def _accept(self, socket):
        """接收客户端信息"""
        req = self.receive_message(socket)
        if req.is_unkown():
            socket.send(SocketResponse.build_unkown().dumps())
            return

        # 回复心跳信息
        if req.is_heart():
            socket.send(SocketResponse().dumps())
            return

        if req.is_stop():
            print('服务停止')
            socket.send(SocketResponse(data = '服务停止').dumps())
            raise ServerStopException()
        print(req.to_dict())
        res = req.run()
        socket.send(res.dumps())

    def receive_message(self, receive_socket: socket.socket):
        """接收消息"""
        data = receive_socket.recv(SocketConstants.FRAGMENT_SIZE)
        return SocketRequest.loads(data)

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if args[0] == 'server':
        Server().run()

    client = Client()
    client.connect()
    params = {
        "query": { "_id": "20210806152807_1628234887" }
    }
    #  client.exec('wush', 'version', 'find', params)
    client.stop_server()
    #  client.heart()

    client.close()

    #  client = Client()
    #  client.connect()
    #  params = {
        #  "query": { "_id": "20210806152807_1628234887" }
    #  }
    #  #  client.exec('wush', 'version', 'find', params)
    #  #  client.stop_server()
    #  client.heart()

    #  client.close()
