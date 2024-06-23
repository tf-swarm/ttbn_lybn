#!/usr/bin/env python
# -*- coding=utf-8 -*-
import time
import md5
import json
import requests
import urllib2
import ssl
from log import Logger

class Controller(object):
    gameId = 2
    protected = 'aXh4b28ubWVAZ21haWwuY29tCg=='
    url = 'http://47.92.72.109:9000' #47.92.72.109
    headers = {'content-type': "application/json"}

    def getTs(self):
        return int(time.time())

    def getSign(self):
        time1 = self.getTs()
        signString = "gameId=%d&token=%s&ts=%s" % (self.gameId, self.protected, str(time1))
        a = md5.md5(signString)
        sign = a.hexdigest()
        return sign

    #传入字典
    def msgPack(self, msg):
        pack = {
            'gameId': self.gameId,
            'sign': self.getSign(),
            'ts': self.getTs(),
        }
        t_dict = pack.copy()
        t_dict.update(msg)
        content = json.dumps(t_dict)
        return content

    # 发起请求，等待相应
    def request(self, url, msg):
        content = self.msgPack(msg)
        request_url = self.url + url
        try:
            ret = requests.post(request_url, data=content, headers=self.headers, timeout=6000)
            return ret
        except Exception:
            Logger.exception()

    def urllib2_get(self, url):
        context = ssl._create_unverified_context()
        request = urllib2.Request(url)
        response = urllib2.urlopen(request, context=context)
        json_info = json.loads(response.read())
        return json_info


Controller = Controller()

def test():
    url = '/v1/shell/addcdkey'
    msg = {'reward':{'props': [{'id': 215, 'count': 1}, {'id': 216, 'count': 1}, {'id': 217, 'count': 1}, {'id': 218, 'count': 1}]},
            'count':1000,
            'time':int(time.time()),
            'detail':'test sdkey'}
    r = Controller.request(url, msg)
    print(r)
