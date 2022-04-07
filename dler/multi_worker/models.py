#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description:

#  import uuid
from inspect import signature
from pydantic import BaseModel, Field, validator
from typing import (
    Callable,
    Optional,
    Union
)

class WorkerBuilder(BaseModel):
    pool_size: int = 10
    max_open_file_count: int = 128
    max_run_times: int = 10
    timeout: int = 10


class WorkModel(BaseModel):
    work_id: Union[str, int]
    run_times: int = 0
    func: Callable[[], bool]
    func_args: Optional[list] = []
    is_succ: bool = False

    @validator('func')
    def check_func_signature(cls, v):
        """检查方法签名"""
        cls_type = signature(v).return_annotation
        if cls_type.__name__ != 'bool':
            raise ValueError("func must return bool")
        return v

#  class MultiWorkerBuilder(BaseModel):
    #  pool_size: int = 8
    #  max_open_file_count: int = 128
    #  max_run_times: int = 10
    #  timeout: int = 10

#  class Worker(BaseModel):
    #  worker_id: Union[str, int] = Field(default_factory = uuid.uuid4)
    #  run_times: int = 0
    #  func: Callable[[], bool]
    #  args: Optional[list] = []
    #  is_succ: bool = False

    #  @validator('func')
    #  def check_func_signature(cls, v):
        #  """检查方法签名"""
        #  cls_type = signature(v).return_annotation
        #  if cls_type.__name__ != 'bool':
            #  raise ValueError("func must return bool")
        #  return v

#  class Response(BaseModel):
    #  worker_id: Union[str, int]
    #  is_succ: bool


def test(a: int, b: int) -> bool:
    pass

if __name__ == "__main__":
    w = WorkModel(func = test)
    print(w)
