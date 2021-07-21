#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

#  import typer

#  app = typer.Typer()


#  @app.command()
#  def hello(name: str):
    #  '''添加下载地址到队列'''
    #  typer.echo(f"Hello {name}")


#  @app.command()
#  def goodbye(name: str, formal: bool = False):
    #  if formal:
        #  typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    #  else:
        #  typer.echo(f"Bye {name}!")


#  if __name__ == "__main__":
    #  app()k.

from pydler.downloader.models import Task
from pydler.downloader.models import SubTask
from pydler.downloader.m3u8_downloader import TaskStatus


if __name__ == "__main__":
    count = SubTask.db_col(task_id = '17290').count({})
    print(count)
    tasks = SubTask.db_col(task_id = '17290').find({})
    #  for task in tasks:
        #  if task.get("status") == TaskStatus.SUCCESS.value:
            #  continue
        #  print(task)
