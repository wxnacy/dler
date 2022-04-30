#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import typer
from typer import (
    Argument
)

from dler.tasker.m3u8_tasker import M3u8Tasker

app = typer.Typer()

@app.command()
def start(url: str = Argument(..., help="URL 路径")):
    """开始下载任务"""
    tasker = M3u8Tasker(url = url)
    tasker.build()
    tasker.run()

@app.command()
def run():
    print('test')

if __name__ == "__main__":
    app()
