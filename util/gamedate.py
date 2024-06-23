#!/usr/bin/env python
# -*- coding=utf-8 -*-

class RunAnalysis(object):
    @classmethod
    def contrast_info(cls):
        condition = [
            {"vale": "0", "content": "全部活跃"},
            {"vale": "online_vip", "content": "VIP"},
            {"vale": "no_vip", "content": "非VIP"},
            {"vale": "online_pay", "content": "付费"},
            {"vale": "no_pay", "content": "未付费"},
        ]
        return condition

    @classmethod
    def contrast_cycle(cls):
        cycle = [
            {"vale": "0", "content": "对比前日"},
            {"vale": "1", "content": "对比上周均值"},
            {"vale": "2", "content": "对比上周同日"},
        ]
        return cycle


class Data_Info(object):
    @classmethod
    def get_query_data(cls):
        data_info =[
            {"vale": "online_player", "content": "在线玩家"},
            {"vale": "active_player", "content": "活跃玩家"},
            {"vale": "pay_player", "content": "付费用户"},
            {"vale": "pay_active_player", "content": "付费活跃用户"},
            {"vale": "register_time", "content": "注册用户"},
            {"vale": "uid", "content": "玩家ID"},
            {"vale": "nick", "content": "玩家昵称"},
            # {"vale": "promoter", "content": "推广员"},
            {"vale": "phone", "content": "手机号码"},
        ]
        return data_info

    @classmethod
    def get_filter_info(cls, index):
        if index == 1:
            one_info = [
                {"vale": "uid", "content": "玩家ID"},
                {"vale": "all_pay_total", "content": "总充值额度"},
                {"vale": "day_pay_total", "content": "当日充值金额"},
                {"vale": "day_in_silver_coupon", "content": "当日话费券产出"},
                {"vale": "day_in_warhead", "content": "当日龙蛋产出"},
            ]
            return one_info
        else:
            two_info = [
                {"vale": "uid", "content": "玩家ID"},
                {"vale": "all_pay_total", "content": "总充值额度"},
                {"vale": "day_in_power", "content": "当日鸟蛋产出"},
            ]
            return two_info

    @classmethod
    def get_sort_info(cls):
        sort_info = [
            # {"vale": "0", "content": "默认排序"},
            {"vale": "1", "content": "正序"},
            {"vale": "2", "content": "倒序"},
        ]
        return sort_info

    @classmethod
    def get_mail_status(cls):
        status = [
            {"vale": "0", "content": "全部"},
            {"vale": "1", "content": "待审核"},
            {"vale": "2", "content": "审核通过"},
        ]
        return status

    @classmethod
    def get_pay_status(cls):
        pay_status = [
            {"vale": "0", "content": "全部"},
            {"vale": "6", "content": "已支付"},
            {"vale": "1", "content": "未支付"},
        ]
        return pay_status

    @classmethod
    def get_order_status(cls):
        order_status = [
            {"vale": "user_id", "content": "用户ID"},
            {"vale": "product_id", "content": "商品ID"},
            {"vale": "order_id", "content": "订单ID"},
        ]
        return order_status

    @classmethod
    def get_player_period(cls):
        period_data = [
            {"vale": "uid", "content": "玩家ID"},
            {"vale": "money", "content": "充值金额"},
        ]
        return period_data

    @classmethod
    def get_times_total(cls):
        times_total = [
            {"vale": "online", "content": "在线人数"},
            {"vale": "online_pay", "content": "在线付费人数"},
            {"vale": "online_vip", "content": "付费活跃人数"},
        ]
        return times_total

    @classmethod
    def get_strong_box(cls):
        strong_box = [
            {"vale": "1", "content": "存储用户ID"},
            {"vale": "2", "content": "取出用户ID"},
        ]
        return strong_box

    @classmethod
    def get_power_championship(cls):
        championship = [
            {"vale": "1", "content": "日积分"},
            {"vale": "2", "content": "周积分"},
        ]
        return championship

    @classmethod
    def get_user_pay_total(cls):
        pay_total = [
            {"vale": "1", "content": "龙蛋"},
            {"vale": "2", "content": "话费券"},
        ]
        return pay_total

    @classmethod
    def get_hardcore_info(cls):
        hardcore = [
            {"vale": "0", "content": "全部"},
            {"vale": "1", "content": "硬核渠道汇总"},
            {"vale": "2", "content": "CPL渠道汇总"},
            {"vale": "3", "content": "CPS渠道汇总"},
        ]
        return hardcore


class Arena_Info(object):

    @classmethod
    def get_arena_type(cls):
        arena_type = [
            {"vale": "1", "content": "快速赛"},
            # {"vale": "2", "content": "大炮赛"},
            # {"vale": "3", "content": "敬请期待"},
        ]
        return arena_type

    @classmethod
    def get_hour_interval(cls):
        hour_interval = [
            {"vale": "0", "hour": "00时"},
            {"vale": "1", "hour": "01时"},
            {"vale": "2", "hour": "02时"},
            {"vale": "3", "hour": "03时"},
            {"vale": "4", "hour": "04时"},
            {"vale": "5", "hour": "05时"},
            {"vale": "6", "hour": "06时"},
            {"vale": "7", "hour": "07时"},
            {"vale": "8", "hour": "08时"},
            {"vale": "9", "hour": "09时"},
            {"vale": "10", "hour": "10时"},
            {"vale": "11", "hour": "11时"},
            {"vale": "12", "hour": "12时"},
            {"vale": "13", "hour": "13时"},
            {"vale": "14", "hour": "14时"},
            {"vale": "15", "hour": "15时"},
            {"vale": "16", "hour": "16时"},
            {"vale": "17", "hour": "17时"},
            {"vale": "18", "hour": "18时"},
            {"vale": "19", "hour": "19时"},
            {"vale": "20", "hour": "20时"},
            {"vale": "21", "hour": "21时"},
            {"vale": "22", "hour": "22时"},
            {"vale": "23", "hour": "23时"},
            {"vale": "24", "hour": "24时"},
        ]
        return hour_interval

    @classmethod
    def get_minute_interval(cls):
        minute_interval = [
            {"vale": "0", "minute": "0分"},
            # {"vale": "10", "minute": "10分"},
            # {"vale": "20", "minute": "20分"},
            # {"vale": "30", "minute": "30分"},
            # {"vale": "40", "minute": "40分"},
            # {"vale": "50", "minute": "50分"},

        ]
        return minute_interval

    @classmethod
    def get_rake_info(cls):
        rake_info = {"rake": 0.1}, #抽成10%
        return rake_info


class Mini_Game_Info(object):

    @classmethod
    def get_vip_grade(cls):
        vip_grade =[
            {"vale": "0", "content": "vip_0"},
            {"vale": "1", "content": "vip-1"},
            {"vale": "2", "content": "vip-2"},
            {"vale": "3", "content": "vip-3"},
            {"vale": "4", "content": "vip-4"},
            {"vale": "5", "content": "vip-5"},
            {"vale": "6", "content": "vip-6"},
            {"vale": "7", "content": "vip-7"},
            {"vale": "8", "content": "vip-8"},
            {"vale": "9", "content": "vip-9"},
            {"vale": "10", "content": "vip-10"},
            {"vale": "11", "content": "vip-11"},
            {"vale": "12", "content": "vip-12"},
        ]
        return vip_grade

    @classmethod
    def get_game_type(cls):
        game_type = [
            {"vale": "1", "content": "靶场"},
            {"vale": "2", "content": "翻翻乐"},
            {"vale": "3", "content": "大富翁"},
            # {"vale": "4", "content": "斗地主"},
        ]
        return game_type


class Shop(object):

    @classmethod
    def shop_type_name(cls):
        """限时商城更新的商品类型"""
        shop_name = [
            {"vale": "1", "content": "生活实物"},
            {"vale": "2", "content": "卡类专区"},
            {"vale": "3", "content": "游戏道具"},
            {"vale": "5", "content": "活动专区"},
        ]
        return shop_name

    @classmethod
    def good_type_name(cls):  # 1、实物，2、充值卡，3、游戏道具，4、卡密
        shop_name = [
            {"vale": "1", "content": "实物"},
            {"vale": "2", "content": "充值卡"},
            {"vale": "3", "content": "游戏道具"},
            {"vale": "4", "content": "卡密"},
        ]
        return shop_name

    @classmethod
    def money_type(cls):
        currency = [
            {"vale": "7", "content": "话费券"},
            {"vale": "8", "content": "火龙蛋"},
            {"vale": "9", "content": "圣龙蛋"},
            {"vale": "10", "content": "冰龙蛋"},
            {"vale": "11", "content": "龙舟券"},
        ]
        return currency

    @classmethod
    def shop_status_name(cls):
        """商城发货详情"""
        status_name = [
            {"vale": "2", "content": "已发货"},
            {"vale": "1", "content": "未发货"},
        ]
        return status_name

    @classmethod
    def vip_grade(cls):
        """限时商城更新的vip等级"""
        vip_grade = [
            {"vale": "0", "content": "免费玩家"},
            {"vale": "1", "content": "VIP1"},
            {"vale": "2", "content": "VIP2"},
            {"vale": "3", "content": "VIP3"},
            {"vale": "4", "content": "VIP4"},
            {"vale": "5", "content": "VIP5"},
            {"vale": "6", "content": "VIP6"},
            {"vale": "7", "content": "VIP7"},
            {"vale": "8", "content": "VIP8"},
            {"vale": "9", "content": "VIP9"},
            {"vale": "10", "content": "VIP10"},
            {"vale": "11", "content": "VIP11"},
            {"vale": "12", "content": "VIP12"},
        ]
        return vip_grade

    @classmethod
    def shop_filter_name(cls):
        """限时商城筛选名称"""
        filter_name = [
            {"vale": "0", "content": "全部商品"},
            {"vale": "1", "content": "生活实物"},
            {"vale": "2", "content": "卡类专区"},
            {"vale": "3", "content": "游戏道具"},
            {"vale": "4", "content": "卡类专区"},
            {"vale": "5", "content": "活动专区"},
            {"vale": "-1", "content": "白送50元"},
        ]
        return filter_name

    @classmethod
    def get_card_supplier(cls):
        """供应商"""
        card_supplier =[
            {"vale": "0", "content": "全部供应商"},
            {"vale": "电信", "content": "电信"},
            {"vale": "联通", "content": "联通"},
            {"vale": "移动", "content": "移动"},
        ]
        return card_supplier

    @classmethod
    def get_card_price(cls):
        """价格"""
        card_price = [
            {"vale": "0", "content": "全部价格"},
            {"vale": "50", "content": "50元"},
            {"vale": "100", "content": "100元"},
            {"vale": "500", "content": "500元"},
        ]
        return card_price

    @classmethod
    def get_card_status(cls):
        """兑换状态"""
        card_status = [
            {"vale": "0", "content": "全部状态"},
            {"vale": "1", "content": "已兑换"},
            {"vale": "2", "content": "未兑换"},
        ]
        return card_status

    @classmethod
    def get_card_info(cls):
        """筛选条件"""
        card_info = [
            {"vale": "0", "content": "全部条件"},
            {"vale": "card_number", "content": "卡号"},
            {"vale": "card_secret", "content": "卡密"},
            {"vale": "player_id", "content": "玩家ID"},
            {"vale": "player_nick", "content": "玩家昵称"},
        ]
        return card_info

    @classmethod
    def get_inventory_info(cls):
        """剩余库存"""
        inventory_info = [
            {"vale": "50", "content": "50元"},
            {"vale": "100", "content": "100元"},
            {"vale": "500", "content": "500元"},
        ]
        return inventory_info

    @classmethod
    def get_convert_record(cls):
        """兑换记录筛选条件"""
        convert_record = [
            {"vale": "uid", "content": "玩家ID"},
            {"vale": "nick", "content": "玩家昵称"},
        ]
        return convert_record

    @classmethod
    def shop_switch(cls):
        """兑换记录筛选条件"""
        shop_switch = [
            {"vale": 0, "content": "商城开启"},
            {"vale": 1, "content": "商城关闭"},
        ]
        return shop_switch

    @classmethod
    def get_ship_status_data(cls):
        """发货状态筛选"""
        ship_status_data = [
            {"vale": '3', "content": "全部"},
            {"vale": '0', "content": "未审核"},
            {"vale": '1', "content": "未发货"},
            {"vale": '2', "content": "已发货"},
            {"vale": '6', "content": "审核异常"},
            {"vale": '7', "content": "暂不通过"},
        ]
        return ship_status_data

    @classmethod
    def gift_shop_type(cls):
        """礼包类型"""
        gift_type_info = [
            {"vale": '1', "content": "每日开放"},
            {"vale": '2', "content": "每周开放"},
            {"vale": '3', "content": "每月开放"},
            {"vale": '4', "content": "指定时间开放"},
            {"vale": '5', "content": "连续购买"},
            {"vale": '6', "content": "贵族特惠"},
            {"vale": '7', "content": "终身一次"},
        ]
        return gift_type_info


class Activity_Info(object):

    @classmethod
    def get_red_packet_type(cls):
        red_packet_type = [
            {"vale": "0", "content": "普通红包"},
            {"vale": "1", "content": "定时红包"},
        ]
        return red_packet_type

    @classmethod
    def get_gift_type(cls):
        get_gift_type = [
            {"vale": "1", "content": "活动礼包1"},
            {"vale": "2", "content": "活动礼包2"},
        ]
        return get_gift_type

    @classmethod
    def pay_status(cls):
        pay_status = [
            {"vale": "1", "content": "当前配置"},
            {"vale": "2", "content": "新的配置"},
        ]
        return pay_status

    @classmethod
    def get_hot_type(cls):
        get_hot_type = [
            {"vale": "0", "content": "默认"},
            {"vale": "1", "content": "最新"},
            {"vale": "2", "content": "推荐"},
            {"vale": "3", "content": "热门"},
            {"vale": "4", "content": "主题"},
        ]
        return get_hot_type

    @classmethod
    def gift_type(cls):
        gift_type = [
            {"vale": 1, "content": "每日一次"},
            {"vale": 2, "content": "终身一次"}
        ]
        return gift_type

    @classmethod
    def icon_type(cls):
        icon_type = [
            {"vale": 1, "content": "技能"},
            {"vale": 2, "content": "炮台"},
            {"vale": 3, "content": "金币"},
            {"vale": 4, "content": "宝石"},
            {"vale": 5, "content": "灵魂宝石"},
            {"vale": 6, "content": "强化石"},
        ]
        return icon_type

    @classmethod
    def get_open_time(cls):
        open_time = [
            {"vale": "1", "content": "每天"},
            {"vale": "7", "content": "每周"},
            {"vale": "30", "content": "每月"},
        ]
        return open_time

    @classmethod
    def get_total_pay(cls):
        activity_data = [
            {"vale": "0", "content": "保留活动数据"},
            {"vale": "1", "content": "删除活动数据"},
        ]
        return activity_data

    @classmethod
    def get_room_info(cls):
        room_info = [
            {"vale": "201", "content": "初级房"},
            {"vale": "202", "content": "中级房"},
            {"vale": "203", "content": "高级房"},
            {"vale": "209", "content": "VIP房"},
        ]
        return room_info

    @classmethod
    def get_select_info(cls):
        select_info = [
            {"vale": "0", "content": "全部"},
            {"vale": "1", "content": "循环"},
            {"vale": "2", "content": "手动"},
        ]
        return select_info

    @classmethod
    def give_props_data(cls):
        props_data = [
            {"vale": "coin", "content": "金币"},
            {"vale": "power", "content": "鸟蛋"},
            {"vale": "diamond", "content": "钻石"},
            {"vale": "silver_coupon", "content": "话费券"},
            {"vale": "201", "content": "锁定"},
            {"vale": "1201", "content": "绑定-锁定"},
            {"vale": "202", "content": "冰冻"},
            {"vale": "1202", "content": "绑定-冰冻"},
            {"vale": "203", "content": "狂暴"},
            {"vale": "1203", "content": "绑定-狂暴"},
            {"vale": "205", "content": "召唤"},
            {"vale": "1205", "content": "绑定-召唤"},
            {"vale": "206", "content": "加速"},
            {"vale": "1206", "content": "绑定-加速"},
            # {"vale": "204", "content": "超级武器"},
            # {"vale": "211", "content": "青铜宝箱"},
            # {"vale": "212", "content": "白银宝箱"},
            # {"vale": "213", "content": "黄金宝箱"},
            # {"vale": "214", "content": "至尊宝箱"},
            {"vale": "301", "content": "灵魂宝石"},
            {"vale": "1301", "content": "绑定-灵魂宝石"},
            {"vale": "1302", "content": "大福袋"},
            {"vale": "1303", "content": "风暴结晶"},
            {"vale": "1304", "content": "逐风者碎片"},
            {"vale": "1305", "content": "礼盒"},
            {"vale": "1311", "content": "神秘礼盒"},
            {"vale": "1611", "content": "许愿卡"},
            {"vale": "1328", "content": "白银钥匙"},
            {"vale": "1329", "content": "黄金钥匙"},
            {"vale": "1330", "content": "白金钥匙"},
            {"vale": "1331", "content": "白银宝箱"},
            {"vale": "1332", "content": "黄金宝箱"},
            {"vale": "1333", "content": "白金宝箱"},
            {"vale": "1207", "content": "风暴狮角"},
            {"vale": "1321", "content": "八宝粽子"},
            {"vale": "1351", "content": "龙舟券"},
            {"vale": "1327", "content": "捕鸟宝箱"},
            {"vale": "215", "content": "绿灵石"},
            {"vale": "1215", "content": "绑定-绿灵石"},
            {"vale": "216", "content": "蓝魔石"},
            {"vale": "1216", "content": "绑定-蓝魔石"},
            {"vale": "217", "content": "紫晶石"},
            {"vale": "1217", "content": "绑定-紫晶石"},
            {"vale": "218", "content": "血精石"},
            {"vale": "1218", "content": "绑定-血精石"},
            {"vale": "219", "content": "强化石"},
            {"vale": "1219", "content": "绑定-强化石"},
            {"vale": "220", "content": "创房卡"},
            {"vale": "1220", "content": "绑定-创房卡"},
            # {"vale": "601", "content": "青铜宝箱"},
            # {"vale": "602", "content": "白银宝箱"},
            # {"vale": "603", "content": "黄金宝箱"},
            {"vale": "701", "content": "毒龙蛋"},
            {"vale": "1701", "content": "绑定-毒龙蛋"},
            {"vale": "702", "content": "冰龙蛋"},
            {"vale": "1702", "content": "绑定-冰龙蛋"},
            {"vale": "703", "content": "火龙蛋"},
            {"vale": "1703", "content": "绑定-火龙蛋"},
            {"vale": "704", "content": "圣龙蛋"},
            {"vale": "1704", "content": "绑定-圣龙蛋"},
        ]
        return props_data

    @classmethod
    def give_weapon_data(cls):
        weapon_data = [
            {"vale": "20001", "content": "流沙之鳞"},
            {"vale": "20002", "content": "冰翼猎手"},
            {"vale": "20003", "content": "翡翠荆棘"},
            {"vale": "20004", "content": "狂怒炎龙"},
            {"vale": "20005", "content": "死亡之翼"},
            {"vale": "20006", "content": "雷鸣宙斯"},
            {"vale": "20007", "content": "暗夜魅影"},
            # {"vale": "20008", "content": "九五至尊"},
            {"vale": "20010", "content": "恭贺新春"},
            {"vale": "20011", "content": "工地之光"},
            {"vale": "20012", "content": "翡翠梦境"},
            {"vale": "20013", "content": "逐风者"},
            {"vale": "20014", "content": "天炎之怒"},
            {"vale": "20015", "content": "蓝魔冰晶"},
            {"vale": "20016", "content": "夏日清檬"},
            {"vale": "auto_shot", "content": "自动开炮"},
        ]
        return weapon_data

    @classmethod
    def login_reward_need(cls):
        reward_need = [
            {"vale": 1, "content": "人物等级"},
            {"vale": 2, "content": "炮倍数"},
            {"vale": 3, "content": "绑定手机"},
            {"vale": 4, "content": "充值"},
            {"vale": 5, "content": "VIP等级"},
        ]
        return reward_need

    @classmethod
    def need_time(cls):
        need_list = [
            {"vale": "1", "content": "天数"},
            {"vale": "2", "content": "分钟"},
        ]
        return need_list

    @classmethod
    def get_fallow_list(cls):
        fallow = [
            {"vale": "0", "content": "选择状态"},
            {"vale": "1", "content": "送分"},
            {"vale": "2", "content": "收分"},
        ]
        return fallow

    @classmethod
    def get_month(cls):
        month = [
            {"vale": "28", "content": "28天"},
            {"vale": "29", "content": "29天"},
            {"vale": "30", "content": "30天"},
            {"vale": "31", "content": "31天"},
        ]
        return month

    @classmethod
    def product_config(cls):
        product_config = {
            '100900': {
                        'price': 160,
                        'name': u'恭贺新春(8.5折)',
                        'weaponid': 20010,
                    },  # 炮台: 恭贺新春（活动打折8.5）
            '100901': {
                        'price': 75,
                        'name': u'雷鸣宙斯(8.5折)',
                        'weaponid': 20006,
                    },  # 炮台: 雷鸣宙斯（活动打折9）
            '100902': {
                        'price': 109,
                        'name': u'暗夜魅影(8.5折)',
                        'weaponid': 20007,
                    },  # 炮台: 暗夜魅影（活动打折8）
            '100903': {
                        'price': 132,
                        'name': u'恭贺新春(7折)',
                        'weaponid': 20010,
                    },  # 炮台: 恭贺新春（活动打折7）
            '100904':{
                    'price': 150,
                    'name': u'恭贺新春(8折)',
                    'weaponid': 20010,
                    },

            "100905":{
                    'price': 62,
                    'name': u'雷鸣宙斯(7折)',
                    'weaponid': 20006,
                },
            "100906":{
                    'price': 70,
                    'name': u'雷鸣宙斯(8折)',
                    'weaponid': 20006,
                },
            "100907": {
                    'price': 90,
                    'name': u'暗夜魅影(7折)',
                    'weaponid': 20007,
                },
            "100908": {
                    'price': 102,
                    'name': u'暗夜魅影(8折)',
                    'weaponid': 20007,
                    },
            "100909": {
                    'price': 35,
                    'name': u'狂怒炎龙(7折)',
                    'weaponid': 20004,
                    },
            "1009010": {
                    'price': 40,
                    'name': u'狂怒炎龙(8折)',
                    'weaponid': 20004,
                    },
            "100911": {
                    'price': 43,
                    'name': u'狂怒炎龙(8.5折)',
                    'weaponid': 20004,
                    },
            # '100778': {
            #             'price': 30,
            #             'name': u'周日团购',
            #             'week': 6,
            #             'content': {
            #                 'chip': 500000,
            #             }
            #         },  # 周日团购
            # '100779': {
            #             'price': 30,
            #             'name': u'周六团购',
            #             'week': 5,
            #             'content': {
            #                 'chip': 400000,
            #                 'props': [{'id': 204, 'count': 1}],
            #             }
            #         },  # 周六团购
            # '100785': {
            #             'price': 28,
            #             'name': u'超值礼包',
            #             'worth': 45,
            #             'content': {
            #                 'chip': 150000,
            #                 'diamond': 100,
            #                 'props': [{'id': 202, 'count': 5}, {'id': 205, 'count': 5}],
            #             }
            #         },  # 超值礼包
            # '100601': {
            #             'price': 30,
            #             'name': u'绿灵石*15',
            #             'exp': 200,
            #             'content': {
            #                 'props': [{'id': 215, 'count': 15}],
            #             }
            #         },  # 强化石,
            # '100602': {
            #             'price': 30,
            #             'name': u'血精石*15',
            #             'exp': 200,
            #             'content': {
            #                 'props': [{'id': 218, 'count': 15}],
            #             }
            #         },  # 强化石
            # '100603': {
            #             'price': 30,
            #             'name': u'蓝魔石*15',
            #             'exp': 200,
            #             'content': {
            #                 'props': [{'id': 216, 'count': 15}],
            #             }
            #         },  # 强化石
            # '100604': {
            #             'price': 30,
            #             'name': u'紫晶石*15',
            #             'exp': 200,
            #             'content': {
            #                 'props': [{'id': 217, 'count': 15}],
            #             }
            #         },  # 强化石
            #	'101001': product_101001, #狂暴无双*10（活动打折8）
        }
        return product_config

    @classmethod
    def get_shop_config(cls):
        product_info = {
            "chip_info":{
                '101807': {
                        'price': 10,
                        'name': u'10元捕鸟鸟蛋礼包(oppo新春)',
                        'desc': {
                            'display': u'加赠145%',
                            'addition': 145,
                            'amount': 50000,
                        },
                        'first': {
                            'diamond': 145,
                        },
                        'content': {
                            'chip': 50000,
                        }
                    },  # 10元捕鸟鸟蛋礼包（oppo新春）
                '100807': {
                        'price': 10,
                        'name': u'10元捕鸟鸟蛋礼包',
                        'desc': {
                            'display': u'加赠5%',
                            'addition': 5,
                            'amount': 50000,
                        },
                        'first': {
                            'diamond': 5,
                        },
                        'content': {
                            'chip': 50000,
                        }
                    },  # 10元捕鸟鸟蛋礼包
                '100806': {
                        'price': 30,
                        'name': u'30元捕鸟鸟蛋礼包',
                        'desc': {
                            'display': u'加赠10%',
                            'addition': 30,
                            'amount': 150000,
                        },
                        'first': {
                            'diamond': 30,
                        },
                        'content': {
                            'chip': 150000,
                        }
                    },  # 30元捕鸟鸟蛋礼包
                '100805': {
                        'price': 50,
                        'name': u'50元捕鸟鸟蛋礼包',
                        'desc': {
                            'display': u'加赠15%',
                            'addition': 75,
                            'amount': 250000,
                        },
                        'first': {
                            'diamond': 75,
                        },
                        'content': {
                            'chip': 250000,
                        }
                    },  # 50元捕鸟鸟蛋礼包
                '100804': {
                        'price': 100,
                        'name': u'100元捕鸟鸟蛋礼包',
                        'desc': {
                            'display': u'加赠20%',
                            'addition': 200,
                            'amount': 500000,
                        },
                        'first': {
                            'diamond': 200,
                        },
                        'content': {
                            'chip': 500000,
                        }
                    },  # 98元捕鸟鸟蛋礼包
                '100803': {
                        'price': 500,
                        'name': u'500元捕鸟鸟蛋礼包',
                        'desc': {
                            'display': u'加赠25%',
                            'addition': 1250,
                            'amount': 2500000,
                        },
                        'first': {
                            'diamond': 1250,
                        },
                        'content': {
                            'chip': 2500000,
                        }
                    },  # 488元捕鸟鸟蛋礼包
                '100802': {
                        'price': 1000,
                        'name': u'1000元捕鸟鸟蛋礼包',
                        'desc': {
                            'display': u'加赠30%',
                            'addition': 3000,
                            'amount': 5000000,
                        },
                        'first': {
                            'diamond': 3000,
                        },
                        'content': {
                            'chip': 5000000,
                        }
                    },
            },
            "diamond_info":{
                '100801': {
                        'price': 10,
                        'name': u'10元捕鸟钻石礼包',
                        'desc': {
                            'display': u'加赠5%',
                            'addition': 5,
                            'amount': 100
                        },
                        'first': {
                            'diamond': 5
                        },
                        'content': {
                            'diamond': 100
                        }
                    },  # 10元捕鸟钻石礼包
                '100800': {
                            'price': 30,
                            'name': u'30元捕鸟钻石礼包',
                            'desc': {
                                'display': u'加赠10%',
                                'addition': 30,
                                'amount': 300,
                            },
                            'first': {
                                'diamond': 30,
                            },
                            'content': {
                                'diamond': 300,
                            }
                        },  # 30元捕鸟钻石礼包
                '100799': {
                            'price': 50,
                            'name': u'50元捕鸟钻石礼包',
                            'desc': {
                                'display': u'加赠15%',
                                'addition': 75,
                                'amount': 500,
                            },
                            'first': {
                                'diamond': 75,
                            },
                            'content': {
                                'diamond': 500,
                            }
                        },  # 50元捕鸟钻石礼包
                '100798': {
                            'price': 100,
                            'name': u'100元捕鸟钻石礼包',
                            'desc': {
                                'display': u'加赠20%',
                                'addition': 200,
                                'amount': 1000,
                            },
                            'first': {
                                'diamond': 200,
                            },
                            'content': {
                                'diamond': 1000,
                            }
                        },  # 98元捕鸟钻石礼包
                '100797': {
                            'price': 300,
                            'name': u'300元捕鸟钻石礼包',
                            'desc': {
                                'display': u'加赠25%',
                                'addition': 750,
                                'amount': 3000,
                            },
                            'first': {
                                'diamond': 750,
                            },
                            'content': {
                                'diamond': 3000,
                            }
                        },
            },
            "gift_bag":{
                '100808': {
                        'price': 50,
                        'name': u'贵族礼包',
                        'content': {
                                'chip': 25000,
                                'diamond': 10,
                                'props': [{'id': 202, 'count': 2}],
                        }
                },  # 贵族礼包
                "100785":{
                        'price': 28,
                        'name': u'超值礼包',
                        'worth': 45,
                        'content': {
                            'chip': 150000,
                            'diamond': 100,
                            'props': [{'id': 202, 'count': 5}, {'id': 205, 'count': 5}],
                        }
                },
            },
        }
        return product_info


    @classmethod
    def get_bird_type(self):
        big_type_map = {
            0: {'point': 1, 'name': u'鸟'},
            101: {'point': 2, 'name': u'鹧鸪'},
            102: {'point': 3, 'name': u'麻雀'},
            103: {'point': 4, 'name': u'猫头鹰'},
            104: {'point': 5, 'name': u'翠鸟'},
            105: {'point': 6, 'name': u'八哥'},
            106: {'point': 7, 'name': u'黄鹂'},
            107: {'point': 8, 'name': u'画眉'},
            108: {'point': 9, 'name': u'杜鹃'},
            109: {'point': 10, 'name': u'鹦鹉'},
            110: {'point': 12, 'name': u'海鸥'},
            111: {'point': 15, 'name': u'乌鸦'},
            112: {'point': 18, 'name': u'飞龙'},
            113: {'point': 20, 'name': u'秃鹫'},
            114: {'point': 25, 'name': u'蝙蝠'},
            115: {'point': 30, 'name': u'仙鹤'},
            116: {'point': 35, 'name': u'极乐鸟'},
            117: {'point': 40, 'name': u'凤凰'},
            161: {'point': 10, 'name': u'惊弓之鸟'},
            176: {'point': 50, 'name': u'奖金海鸥'},
            177: {'point': 60, 'name': u'奖金乌鸦'},
            178: {'point': 70, 'name': u'奖金飞龙'},
            179: {'point': 80, 'name': u'奖金秃鹫'},
            180: {'point': 90, 'name': u'奖金蝙蝠'},
            181: {'point': 100, 'name': u'奖金仙鹤'},
            182: {'point': 125, 'name': u'奖金极乐鸟'},
            183: {'point': 150, 'name': u'奖金凤凰'},

            201: {'point': 200, 'name': u'生命巨龙'},
            202: {'point': 250, 'name': u'魔法巨龙'},
            203: {'point': 300, 'name': u'雷霆神龙'},
            204: {'point': 350, 'name': u'天界神龙'},
            205: {'point': 400, 'name': u'赤红炎龙'},
            206: {'point': 500, 'name': u'寒霜冰龙'},

            451: {'point': 0, 'name': u'风雷领主'},
            452: {'point': 0, 'name': u'炼狱主宰'},
            501: {'point': 0, 'name': u'鸟卷怪'},
            511: {'point': 0, 'name': u'靶卷怪'},
            521: {'point': 0, 'name': u'钻石怪'},
            551: {'point': 0, 'name': u'同类炸弹怪'},
            552: {'point': 80, 'name': u'区域炸弹怪'},
            553: {'point': 300, 'name': u'全屏炸弹怪'},
            601: {'point': 0, 'name': u'青铜宝箱怪'},
            602: {'point': 0, 'name': u'白银宝箱怪'},
            603: {'point': 0, 'name': u'黄金宝箱怪'},
            701: {'point': 168, 'name': u'招财金猪'},
        }
        return big_type_map


class redeem_Info(object):

    @classmethod
    def get_redeem_money(cls):
        redeem_money = [
            {"vale": "0", "content": "免费码"},
            {"vale": "2", "content": "2元兑换码"},
            {"vale": "10", "content": "10元兑换码"},
            {"vale": "20", "content": "20元兑换码"},
            {"vale": "30", "content": "30元兑换码"},
            {"vale": "40", "content": "40元兑换码"},
            {"vale": "50", "content": "50元兑换码"},
            {"vale": "100", "content": "100元兑换码"},
            {"vale": "200", "content": "200元兑换码"},
            {"vale": "500", "content": "500元兑换码"},
            {"vale": "1000", "content": "1000元兑换码"},
        ]
        return redeem_money

    @classmethod
    def get_employ_status(cls):
        employ = [
            {"vale": "0", "content": "全部"},
            {"vale": "1", "content": "已使用"},
            {"vale": "2", "content": "未使用"},
        ]
        return employ
