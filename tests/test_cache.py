#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com

from dler.cache import CACHE

def test_key():
    key = 'test'
    data =  { "name": "wxnacy" }
    CACHE.set(key, data)

    assert [key] == list(CACHE.keys())
    assert CACHE.get(key) == data

    assert data == CACHE.delete(key)

    assert CACHE.get(key) == None

def test_hset():
    key = 'test_hset'
    datas = [
            { "_id": "a", "name": "wxnacy" },
            { "_id": "b", "name": "wxn" },
            { "_id": "c", "name": "wen" },
            ]

    assert CACHE.hdrop(key) == 0

    for data in datas:
        field = data['_id']
        assert CACHE.hset(key, field, data) == 1

    for data in datas:
        field = data['_id']
        assert CACHE.hset(key, field, data) == 0

    assert list(CACHE.hkeys(key)) == [o['_id'] for o in datas]

    assert CACHE.hdel(key, 'a', 'b', 'd') == 2

    assert CACHE.hdrop(key) == 1

    assert CACHE.hget(key, 'a') == None

def test_list():
    key = 'test'
    data = ['a', 'b', 'c']

    assert CACHE.rpush(key, *data) == 3

    assert CACHE.lrange(key, 0, 10) == data

    assert CACHE.rpop(key) == 'c'
