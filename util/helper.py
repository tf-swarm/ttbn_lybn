#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: likebeta <ixxoo.me@gmail.com>
# Create: 2015-05-06

import os
import commands
from util.tool import Time
from util.context import Context


class ConfigHelper(object):
    _ALL_CONFIG = {}
    _ALL_CMD = []
    _ROOM_MAP = {}

    @classmethod
    def add_game_config(cls, gameId, attr, value, force=True):
        cls.__add_config_item('configitem', 'game:%d:%s' % (gameId, attr), value)

    @classmethod
    def get_game_config(cls, gameId, attr, deault=None):
        return cls.__get_config_item('configitem', 'game:%d:%s' % (gameId, attr), deault)

    @classmethod
    def add_room_map(cls, gameId, roomType, serverId):
        if gameId not in cls._ROOM_MAP:
            cls._ROOM_MAP[gameId] = {}
        if roomType not in cls._ROOM_MAP[gameId]:
            cls._ROOM_MAP[gameId][roomType] = []
        if isinstance(serverId, (list, tuple)):
            cls._ROOM_MAP[gameId][roomType].extend(serverId)
        else:
            cls._ROOM_MAP[gameId][roomType].append(serverId)

    @classmethod
    def get_room_map(cls, gameId, roomType=None):
        if gameId not in cls._ROOM_MAP:
            return []
        if not roomType:
            return cls._ROOM_MAP[gameId]
        if roomType not in cls._ROOM_MAP[gameId]:
            return []
        return cls._ROOM_MAP[gameId][roomType]

    @classmethod
    def __add_config_item(cls, key, attr, value):
        if key not in cls._ALL_CONFIG:
            cls._ALL_CONFIG[key] = {}
        cls._ALL_CONFIG[key][attr] = value
        if isinstance(value, (tuple, list, dict)):
            value = Context.json_dumps(value)
        cls._ALL_CMD.append(['HSET', key, attr, value])

    @classmethod
    def __get_config_item(cls, key, attr, default):
        try:
            return cls._ALL_CONFIG[key][attr]
        except KeyError, e:
            return default

    @classmethod
    def add_config(cls, attr, value):
        cls.__add_config_item('configitem', attr, value)

    @classmethod
    def get_config(cls, attr, deault=None):
        return cls.__get_config_item('configitem', attr, deault)

    @classmethod
    def add_global_config(cls, attr, value):
        cls.__add_config_item('configitem', 'global:%s' % attr, value)

    @classmethod
    def get_global_config(cls, attr, deault=None):
        return cls.__get_config_item('configitem', 'global:%s' % attr, deault)

    @classmethod
    def save_config(cls, fdir, fname):
        cls.add_global_config('game.list', cls._ROOM_MAP.keys())
        for gameId, item in cls._ROOM_MAP.iteritems():
            cls.add_game_config(gameId, 'room.map', item)
            roomtype = item.keys()
            cls.add_game_config(gameId, 'room.type', sorted(roomtype))
            gamelist = set()
            for _, servers in item.iteritems():
                gamelist.update(servers)
        data = Context.json_dumps(cls._ALL_CMD)
        File.write_file(fdir, fname, data)


class Global(object):
    __run_mode = None
    __http_game = None

    @property
    def run_mode(self):
        return self.__run_mode

    @run_mode.setter
    def run_mode(self, mode):
        self.__run_mode = mode

    @property
    def http_game(self):
        return self.__http_game

    @http_game.setter
    def http_game(self, hg):
        self.__http_game = hg


Global = Global()


class File(object):
    @classmethod
    def write_file(cls, fdir, fname, content):
        cls.make_dirs(fdir)
        fpath = fdir + '/' + fname
        with open(fpath, 'w') as _f:
            _f.write(content)
            _f.close()

    @classmethod
    def read_file(cls, fpath):
        with open(fpath) as f:
            data = f.read()
            f.close()
        return data

    @classmethod
    def make_dirs(cls, fdir):
        if not os.path.exists(fdir):
            os.makedirs(fdir)

    @classmethod
    def touch(cls, fpath):
        if os.path.isfile(fpath):
            return
        fdir = os.path.dirname(fpath)
        cls.make_dirs(fdir)
        f = file(fpath, 'w')
        f.close()

    @classmethod
    def find_py_files(cls, srcpath, extname='.py', converttoimport=False):
        file_list = []
        srcpath = os.path.abspath(srcpath)
        cutlen = len(srcpath) + 1
        extlen = len(extname)
        for root, _, files in os.walk(srcpath, True):
            for name in files:
                fpath = os.path.join(root, name)
                fpath = fpath[cutlen:]
                if fpath.find('-') < 0 \
                        and fpath.find('dyn_') < 0 \
                        and fpath.find('/dyn/') < 0 \
                        and fpath.find('dynamic') < 0 \
                        and fpath.find('/tools/') < 0 \
                        and fpath[-extlen:] == extname \
                        and fpath.lower().find('test') < 0 \
                        and fpath.find('script/') != 0:

                    if converttoimport:
                        fpath = fpath[0:-extlen]
                        fpath = fpath.replace('/', '.')
                        fpath = 'import ' + fpath
                    file_list.append(fpath)
        return file_list


class Log(object):
    @classmethod
    def log(cls, *args):
        prefix = Time.datetime_now()
        msg = [str(arg) for arg in args]
        print '%s | %s' % (prefix, ' '.join(msg))


class Util(object):
    @classmethod
    def is_local_ip(cls, ip):
        sts, text = commands.getstatusoutput('ifconfig')
        if sts:
            sts, text = commands.getstatusoutput('/sbin/ifconfig')
        if sts:
            raise Exception(text)
        if text.find('addr:' + str(ip) + ' ') < 0:
            if text.find('inet ' + str(ip) + ' ') < 0:
                if text.find('inet 地址:' + str(ip) + ' ') < 0:
                    return False
        return True


def add_game_config(gid, attr, value, force=True):
    key_info = {}
    game_key = 'game_redis:{}:{}'.format("system", "config")
    res = Context.RedisMatch.hash_mget(game_key, ["config_list"])
    print("----------res", res)
    config_list = (Context.json_loads(res[0]) if res[0] else [])
    key_info["key"] = "game:{}:{}".format(gid, attr)
    config_list.append(key_info)
    print("------add_game--------", gid, attr)
    config = {"config_list": Context.json_dumps(config_list)}
    keys = 'game_redis:{}:{}'.format("system", "config")
    Context.RedisMatch.hash_mset(keys, config)

    ConfigHelper.add_game_config(gid, attr, value, force)


def add_room_map(gid, roomType, serverId):
    ConfigHelper.add_room_map(gid, roomType, serverId)


def get_room_map(gid, roomType=None):
    return ConfigHelper.get_room_map(gid, roomType)


def add_global_config(attr, value):
    ConfigHelper.add_global_config(attr, value)


def get_game_config(gid, attr, default=None):
    return ConfigHelper.get_game_config(gid, attr, default)


def get_global_config(attr, default=None):
    return ConfigHelper.get_global_config(attr, default)


__all__ = ['add_game_config', 'add_global_config',
           'add_room_map', 'get_room_map',
           'get_game_config', 'get_global_config', 'Global']
