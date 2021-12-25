#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
数据缓存
"""

import sys

from collections import defaultdict

class Cache(object):
    _table_data = {}
    _list_data = defaultdict(list)
    _hset_data = defaultdict(dict)


    def set(self, key, data):
        """插入数据"""
        self._table_data[key] = data

    def get(self, key):
        """通过 id 查找"""
        return self._table_data.get(key)

    def delete(self, key):
        """删除"""
        return self._table_data.pop(key, None)

    def keys(self,):
        """列出 id 列表"""
        return self._table_data.keys()

    def hset(self, key, field, value):
        """在哈希表中赋值"""
        res = 1
        if field in self._hset_data[key]:
            res = 0
        self._hset_data[key][field] = value
        return res

    def hget(self, key, field):
        """从哈希表中取值"""
        return self._hset_data[key].get(field)

    def hkeys(self, key):
        """获取哈希表中的所有域"""
        return self._hset_data[key].keys()

    def hdel(self, key, *fields):
        """删除一个或多个哈希表字段"""
        count = 0
        for field in fields:
            if self._hset_data[key].pop(field, None):
                count += 1
        return count

    def hdrop(self, key):
        """清理哈希表"""
        count = 0
        if self._hset_data.pop(key, None):
            count = 1
        return count

    def rpush(self, key, *values):
        """在列表中添加一个或多个值"""
        self._list_data[key].extend(values)
        return len(self._list_data[key])

    def rpop(self, key):
        """移除列表的最后一个元素，返回值为移除的元素。"""
        return self._list_data[key].pop()

    def lrange(self, key, start, stop):
        return self._list_data[key][start:stop]

    def lpush(self, key, *values):
        for value in values:
            self._list_data[key].insert(0, value)
        return len(self._list_data[key])

    def memory(self):
        """内存"""
        return sys.getsizeof(self._table_data)

CACHE = Cache()

del Cache

if __name__ == "__main__":
    res = CACHE.lrange('test', 0, 10)
    print(res)
    # TODO 保存文件，加载文件
