#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: 



class Base:
    class Config:
        name = 'test'
        url = 'test'


class Sub(Base):
    class Config(Base.Config):
        name = 'sub'


if __name__ == "__main__":
    print(Sub.Config.url)
