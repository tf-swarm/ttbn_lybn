#!/usr/bin/env python
# -*- coding:utf8 -*-

import redis
import json

class RedisSingle(object):

    def __init__(self, db):
        self.__db = db
        self.connect()

    def connect(self):
        self.__host = '127.0.0.1'  # 127.0.0.1
        self.__port = '6380'  # 端口号
        # self.__password = ''

        self.__connections = 1000
        try:
            pool = redis.ConnectionPool(host=self.__host, port=self.__port, db=self.__db,
                                        max_connections=self.__connections)
            self.__redis = redis.Redis(connection_pool=pool)
        except Exception as e:
            print('连接redis失败,失败原因:%s' % e)

    def str_set(self, key, value, ex=None):
        try:
            res = self.__redis.set(key, value, ex)
        except Exception as e:
            print('添加key失败,失败原因:%s' % e)
        else:
            return res

    def str_get(self, key):
        if self.__redis.exists(key):
            return self.__redis.get(key)
        else:
            return None

    def str_delete(self, key):
        res = self.__redis.delete(key)
        if res:
            return res
        return None

    def hash_get(self, key, field):  # 获取hash类型key
        try:
            res = self.__redis.hget(key, field)
        except Exception as e:
            print('查询指定hash类型key失败,失败原因:%s' % e)
        else:
            if res:
                return res.decode()
            return None

    def hash_get_json(self, key, field, default=None):
        try:
            _ret = self.__redis.hget(key, field)
        except Exception as e:
            print('查询指定hash类型key失败,失败原因:%s' % e)
        else:
            if _ret is None:
                _ret = default
            else:
                _ret = json.loads(_ret)
            return _ret

    def hash_set(self, key, field, value):  # 添加hash类型key
        try:
            res = self.__redis.hset(key, field, value)
        except Exception as e:
            print('添加hash类型key,失败原因:%s' % e)
        else:
            return res

    def hash_incrby(self, key, field, delta=1):  # 添加hash类型key
        try:
            res = self.__redis.hincrby(key, field, delta)
        except Exception as e:
            print('添加hash类型incrby,失败原因:%s' % e)
        else:
            return res

    def hash_getall(self, key):  # 获取所有hash类型key
        try:
            res = self.__redis.hgetall(key)
        except Exception as e:
            print('查询所有hash类型key失败,失败原因:%s' % e)
        else:
            if res:
                new_data = {}
                for k, v in res.items():
                    new_data[k.decode()] = v.decode()
                return new_data
            else:
                return None

    def hget_keys(self, pattern):
        try:
            res = self.__redis.keys(pattern=pattern)
            # item_list = []
            # res = self.__redis.scan_iter(pattern, 10000)
            # for item in res:
            #     item_list.append(item)
        except Exception as e:
            print('查询数据库中所有key失败,失败原因:%s' % e)
        else:
            # return item_list
            return res

    def hash_del(self, key, keys):  # 删除hash类型key
        try:
            res = self.__redis.hdel(key, keys)
        except Exception as e:
            print('删除hash类型key失败,失败原因:%s' % e)
        else:
            if res:
                return res
            return None

    def hash_mget(self, key, keys,*args):
        try:
            res = self.__redis.hmget(key, keys, *args)
        except Exception as e:
            print('查询指定hash类型key失败,失败原因:%s' % e)
        else:
            return res

    def hash_mset(self, key,kwargs):
        try:
            res = self.__redis.hmset(key,kwargs)
        except Exception as e:
            print('添加hash类型key,失败原因:%s' % e)
        else:
            return res

    def list_lpush(self, key, *args):
        try:
            res = self.__redis.lpush(key,*args)
        except Exception as e:
            print('添加list在最左边添加值,失败原因:%s' % e)
        else:
            return res

    def list_rpush(self, key, *args):
        try:
            res = self.__redis.rpush(key,*args)
        except Exception as e:
            print('添加list在最右边添加值,失败原因:%s' % e)
        else:
            return res

    def delete(self, key):
        tag = self.__redis.exists(key) #判断这个Key是否存在
        if tag:
            self.__redis.delete(key)
        else:
            print('这个key不存在')

# RedisSingle = RedisSingle()