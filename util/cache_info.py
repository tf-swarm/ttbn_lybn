#!/usr/bin/env python
# -*- coding=utf-8 -*-

class Cache_Info(object):
    def __init__(self):
        pass

    def set_recharge(self,result):
        self.start_time = result["start"]
        self.end_time = result["end"]

    def get_recharge(self):
        start_time = self.start_time
        end_time = self.end_time
        return start_time,end_time

    def set_integral_exchange(self,result):
        self.exchange_data = result

    def get_integral_exchange(self):
        return self.exchange_data

    def set_May_day_rank(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]

    def get_May_day_rank(self):
        start_time = self.start_time
        end_time = self.end_time
        return start_time, end_time

    def set_egg_query(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.channel = result["channel"]

    def get_egg_query(self):
        start_time = self.start_time
        end_time = self.end_time
        channel = self.channel
        return start_time, end_time,channel

    def set_fanfanle(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.game = result["game"]
        self.input_data = result["input_data"]

    def get_fanfanle(self):
        start_time = self.start_time
        end_time = self.end_time
        game = self.game
        input_data = self.input_data
        return start_time, end_time,game,input_data

    def set_rich_man(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.game = result["game"]
        self.input_data = result["input_data"]

    def get_rich_man(self):
        start_time = self.start_time
        end_time = self.end_time
        game = self.game
        input_data = self.input_data
        return start_time, end_time, game, input_data

    def set_target(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.game = result["game"]
        self.input_data = result["input_data"]

    def get_target(self):
        start_time = self.start_time
        end_time = self.end_time
        game = self.game
        input_data = self.input_data
        return start_time, end_time, game, input_data

    def set_tichu(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.game = result["game"]
        self.input_data = result["input_data"]

    def get_tichu(self):
        start_time = self.start_time
        end_time = self.end_time
        game = self.game
        input_data = self.input_data
        return start_time, end_time, game, input_data

    def set_game_general(self, result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.game = result["game"]
        self.sort = result["sort"]

    def get_game_general(self):
        start_time = self.start_time
        end_time = self.end_time
        game = self.game
        sort = self.sort
        return start_time, end_time, game, sort

    def set_data_collect(self, result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.channel = result["channel"]

    def get_data_collect(self):
        start_time = self.start_time
        end_time = self.end_time
        channel = self.channel
        return start_time, end_time, channel

    def set_period_data(self, result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.query_info = result["query_info"]
        self.input_data = result["input_data"]

    def get_period_data(self):
        start_time = self.start_time
        end_time = self.end_time
        query_info = self.query_info
        input_data = self.input_data
        return start_time, end_time,query_info, input_data

    def set_coupon_rate(self, result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]

    def get_coupon_rate(self):
        start_time = self.start_time
        end_time = self.end_time
        return start_time, end_time

    def set_grail_data(self, result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]

    def get_grail_data(self):
        start_time = self.start_time
        end_time = self.end_time
        return start_time, end_time

    def set_buried_point(self, result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]
        self.uid = result["uid"]

    def get_buried_point(self):
        start_time = self.start_time
        end_time = self.end_time
        uid = self.uid
        return start_time, end_time,uid

    def set_day_coupon(self,result):
        self.start_time = result["start_day"]
        self.end_time = result["end_day"]

    def get_day_coupon(self):
        start_time = self.start_time
        end_time = self.end_time
        return start_time,end_time

Cache_Info = Cache_Info()