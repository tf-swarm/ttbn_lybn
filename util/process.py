#!/usr/bin/env python
# -*- coding=utf-8 -*-

import random
from login_manage.models import ProductList
from gift_bag_shop.models import GiftInfo
from util.context import Context


class ProcessInfo(object):
    @classmethod
    def generate_verification_code(cls):
        code_list = []
        for i in range(10):  # 0-9数字
            code_list.append(str(i))
        for i in range(65, 91):  # A-Z
            code_list.append(chr(i))
        for i in range(97, 123):  # a-z
            code_list.append(chr(i))

        slice = random.sample(code_list, 6)
        verification_code = ''.join(slice)
        return verification_code

    @classmethod
    def deal_wheel_reward(cls, reward):
        reward_list = []
        for key,info in reward.items():
            new_info = cls.get_reward_info(info.get("reward",{}))
            new_info.update({"rate":info.get("rate",0)})
            reward_list.append(new_info)
        return reward_list


    @classmethod
    def deal_task_reward(cls, reward):
        reward_list = []
        for key, info in reward.items():
            new_info = cls.get_reward_info(info[5])
            new_info.update({"bid":info[2],"count":info[3],"status":info[1],"desc":info[6]})
            reward_list.append(new_info)
        return reward_list


    @classmethod
    def deal_rank_reward(cls, reward):
        reward_list = []
        for info in reward:
            new_info = cls.get_reward_info(info)
            reward_list.append(new_info)
        return reward_list

    @classmethod
    def deal_login_reward(cls, reward):
        reward_list = []
        led = 1
        length = 4
        for prop_dict in reward:
            props_list = cls.deal_gift_reward(prop_dict)
            pr_len = len(props_list)
            if pr_len < length:
                for i in range(0,length-pr_len):
                    props_list.append({"option": "chip", "value": "", "name": ""})

            reward_list.append({"led":led,"props_list":props_list})
            led = led + 1
        return reward_list

    @classmethod
    def deal_may_day_reward(cls, reward):
        reward_list = []
        for info in reward:
            product = info["product"]
            reward_list.append({"name":product.get("name",""),"count":product.get("count",0)})
        return reward_list

    @classmethod
    def deal_egg_reward(cls, reward,):
        give_list = [{"name":"鸟蛋","value":1},{"name":"钻石","value":2},{"name":"鸟券","value":3},{"name":"全屏冰冻","value":4},{"name":"狂暴无双","value":5},{"name":"超级武器","value":6},{"name":"赏金传送","value":7},{"name":"创房卡","value":8},{"name":"臭蛋","value":9}]
        reward_list = []
        index = 0
        for key, info in reward.items():
            give_dict = {}
            give_dict.update({"index":int(key),"min":info.get("min", 0),"max":info.get("max", 0),"rate": info.get("rate", 0)})
            give_dict.update(give_list[index])
            reward_list.append(give_dict)
            index = index + 1
        return reward_list

    @classmethod
    def deal_give_reward(cls, reward):
        reward_list = []
        give_name = ["中间","右上","左上","右下","左下"]
        rate = 0
        for key, info in reward.items():
            new_info = cls.get_reward_info(info)
            new_info.update({"need_pay": int(key), "award_name": give_name[rate]})
            reward_list.append(new_info)
            rate = rate + 1
        return reward_list

    @classmethod
    def get_reward_info(cls, reward):
        if 'power' in reward:
            name = "鸟蛋"
            value = reward["power"]
            return {"option": "power", "value": value, "name": name}
        if 'diamond' in reward:
            name = "钻石"
            value = reward['diamond']
            return {"option": "diamond", "value": value, "name": name}
        if 'target' in reward:
            name = "靶劵"
            value = reward['target']
            return {"option": "target", "value": value, "name": name}
        if 'coin' in reward:
            name = "金币"
            value = reward['coin']
            return {"option": "coin", "value": value, "name": name}
        if 'silver_coupon' in reward:
            name = "话费劵"
            value = reward['silver_coupon']
            return {"option": "silver_coupon", "value": value, "name": name}
        if 'auto_shot' in reward:
            name = "自动开炮"
            value = reward['auto_shot']
            return {"option": "auto_shot", "value": value, "name": name}
        if 'weapon' in reward:
            for info in reward['weapon']:
                if info == 20001:
                    return {"option": "20001", "value": "life"}
                if info == 20002:
                    return {"option": "20002", "value": "life"}
                if info == 20003:
                    return {"option": "20003", "value": "life"}
                if info == 20004:
                    return {"option": "20004", "value": "life"}
                if info == 20005:
                    return {"option": "20005", "value": "life"}
                if info == 20006:
                    return {"option": "20006", "value": "life"}
                if info == 20007:
                    return {"option": "20007", "value": "life"}
                if info == 20008:
                    return {"option": "20008", "value": "life"}
                if info == 20010:
                    return {"option": "20010", "value": "life"}
        if 'props' in reward:
            for pro in reward['props']:
                number = int(pro["id"])
                if number < 20001000:
                    if pro["id"] == 202:
                        name = "冰冻"
                        value = pro["count"]
                        return {"option": "202", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 203:
                        name = "狂暴"
                        value = pro["count"]
                        return {"option": "203", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 204:
                        name = "超级武器"
                        value = pro["count"]
                        return {"option": "204", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 205:
                        name = "召唤"
                        value = pro["count"]
                        return {"option": "205", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 206:
                        name = "加速"
                        value = pro["count"]
                        return {"option": "206", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 211:
                        name = "青铜宝箱"
                        value = pro["count"]
                        return {"option": "211", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 212:
                        name = "白银宝箱"
                        value = pro["count"]
                        return {"option": "212", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 213:
                        name = "黄金宝箱"
                        value = pro["count"]
                        return {"option": "213", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 214:
                        name = "至尊宝箱"
                        value = pro["count"]
                        return {"option": "214", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 215:
                        name = "绿灵石"
                        value = pro["count"]
                        return {"option": "215", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 216:
                        name = "蓝魔石"
                        value = pro["count"]
                        return {"option": "216", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 217:
                        name = "紫晶石"
                        value = pro["count"]
                        return {"option": "217", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 218:
                        name = "血精石"
                        value = pro["count"]
                        return {"option": "218", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 219:
                        name = "强化石"
                        value = pro["count"]
                        return {"option": "219", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 220:
                        name = "创房卡"
                        value = pro["count"]
                        return {"option": "220", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 301:
                        name = "灵魂宝石"
                        value = pro["count"]
                        return {"option": "301", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1303:
                        name = "风暴结晶"
                        value = pro["count"]
                        return {"option": "1303", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1304:
                        name = "逐风者的碎片"
                        value = pro["count"]
                        return {"option": "1304", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1302:
                        name = "大福袋"
                        value = pro["count"]
                        return {"option": "1302", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1305:
                        name = "礼盒"
                        value = pro["count"]
                        return {"option": "1305", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1311:
                        name = "神秘礼盒"
                        value = pro["count"]
                        return {"option": "1311", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1611:
                        name = "许愿卡"
                        value = pro["count"]
                        return {"option": "1611", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1328:
                        name = "白银钥匙"
                        value = pro["count"]
                        return {"option": "1328", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1329:
                        name = "黄金钥匙"
                        value = pro["count"]
                        return {"option": "1329", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1330:
                        name = "白金钥匙"
                        value = pro["count"]
                        return {"option": "1330", "value": value, "name": name, "bound": "2"}

                    if pro["id"] == 1331:
                        name = "白银宝箱"
                        value = pro["count"]
                        return {"option": "1331", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1332:
                        name = "黄金宝箱"
                        value = pro["count"]
                        return {"option": "1331", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1333:
                        name = "白金宝箱"
                        value = pro["count"]
                        return {"option": "1333", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1207:
                        name = "风暴狮角"
                        value = pro["count"]
                        return {"option": "1207", "value": value, "name": name, "bound": "2"}

                    if pro["id"] == 1351:
                        name = "龙舟券"
                        value = pro["count"]
                        return {"option": "1351", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1321:
                        name = "八宝粽子"
                        value = pro["count"]
                        return {"option": "1321", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 1327:
                        name = "捕鸟宝箱"
                        value = pro["count"]
                        return {"option": "1327", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 601:
                        name = "青铜宝箱"
                        value = pro["count"]
                        return {"option": "601", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 602:
                        name = "白银宝箱"
                        value = pro["count"]
                        return {"option": "602", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 603:
                        name = "黄金宝箱"
                        value = pro["count"]
                        return {"option": "603", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 604:
                        name = "青铜宝箱"
                        value = pro["count"]
                        return {"option": "604", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 701:
                        name = "毒龙蛋"
                        value = pro["count"]
                        return {"option": "701", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 702:
                        name = "冰龙蛋"
                        value = pro["count"]
                        return {"option": "702", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 703:
                        name = "火龙蛋"
                        value = pro["count"]
                        return {"option": "703", "value": value, "name": name, "bound": "2"}
                    if pro["id"] == 704:
                        name = "圣龙蛋"
                        value = pro["count"]
                        return {"option": "704", "value": value, "name": name, "bound": "2"}

                    if pro["id"] == 1201:
                        name = "锁定"
                        value = pro["count"]
                        return {"option": "1201", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1202:
                        name = "冰冻"
                        value = pro["count"]
                        return {"option": "1202", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1203:
                        name = "狂暴"
                        value = pro["count"]
                        return {"option": "1203", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1205:
                        name = "召唤"
                        value = pro["count"]
                        return {"option": "1205", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1206:
                        name = "加速"
                        value = pro["count"]
                        return {"option": "1206", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1301:
                        name = "灵魂宝石"
                        value = pro["count"]
                        return {"option": "1301", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1303:
                        name = "风暴结晶"
                        value = pro["count"]
                        return {"option": "1303", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1304:
                        name = "逐风者的碎片"
                        value = pro["count"]
                        return {"option": "1304", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1215:
                        name = "绿灵石"
                        value = pro["count"]
                        return {"option": "1215", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1216:
                        name = "蓝魔石"
                        value = pro["count"]
                        return {"option": "1216", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1217:
                        name = "紫晶石"
                        value = pro["count"]
                        return {"option": "1217", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1218:
                        name = "血精石"
                        value = pro["count"]
                        return {"option": "1218", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1219:
                        name = "强化石"
                        value = pro["count"]
                        return {"option": "1219", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1220:
                        name = "创房卡"
                        value = pro["count"]
                        return {"option": "1220", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1701:
                        name = "毒龙蛋"
                        value = pro["count"]
                        return {"option": "1701", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1702:
                        name = "冰龙蛋"
                        value = pro["count"]
                        return {"option": "1702", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1703:
                        name = "火龙蛋"
                        value = pro["count"]
                        return {"option": "1703", "value": value, "name": name, "bound": "1"}
                    if pro["id"] == 1704:
                        name = "圣龙蛋"
                        value = pro["count"]
                        return {"option": "1704", "value": value, "name": name, "bound": "1"}

                elif number > 200010000:
                    weapon = number / 10000
                    if weapon == 20001:
                        day = cls.deal_weapon_day(number)
                        name = "流沙之鳞{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20001", "need_type": "2", "value": value, "name": name}
                    if weapon == 20002:
                        day = cls.deal_weapon_day(number)
                        name = "冰翼猎手{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20002", "need_type": "2", "value": value, "name": name}
                    if weapon == 20003:
                        day = cls.deal_weapon_day(number)
                        name = "翡翠荆棘{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20003", "need_type": "2", "value": value, "name": name}
                    if weapon == 20004:
                        day = cls.deal_weapon_day(number)
                        name = "狂怒炎龙{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20004", "need_type": "2", "value": value, "name": name}
                    if weapon == 20005:
                        day = cls.deal_weapon_day(number)
                        name = "死亡之翼{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20005", "need_type": "2", "value": value, "name": name}
                    if weapon == 20006:
                        day = cls.deal_weapon_day(number)
                        name = "雷鸣宙斯{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20006", "need_type": "2", "value": value, "name": name}
                    if weapon == 20007:
                        day = cls.deal_weapon_day(number)
                        name = "暗夜魅影{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20007", "need_type": "2", "value": value, "name": name}
                    if weapon == 20008:
                        day = cls.deal_weapon_day(number)
                        name = "九五至尊{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20008", "need_type": "2", "value": value, "name": name}
                    if weapon == 20010:
                        day = cls.deal_weapon_day(number)
                        name = "恭贺新春{}分钟".format(day)
                        value = number % 10000
                        return {"option": "20010", "need_type": "2", "value": value, "name": name}
                else:
                    weapon = number / 1000
                    if weapon == 20001:
                        day = cls.deal_weapon_day(number)
                        name = "流沙之鳞{}天".format(day)
                        value = number % 1000
                        return {"option": "20001", "need_type": "1", "value": value, "name": name}
                    if weapon == 20002:
                        day = cls.deal_weapon_day(number)
                        name = "冰翼猎手{}天".format(day)
                        value = number % 1000
                        return {"option": "20002", "need_type": "1", "value": value, "name": name}
                    if weapon == 20003:
                        day = cls.deal_weapon_day(number)
                        name = "翡翠荆棘{}天".format(day)
                        value = number % 1000
                        return {"option": "20003", "need_type": "1", "value": value, "name": name}
                    if weapon == 20004:
                        day = cls.deal_weapon_day(number)
                        name = "狂怒炎龙{}天".format(day)
                        value = number % 1000
                        return {"option": "20004", "need_type": "1", "value": value, "name": name}
                    if weapon == 20005:
                        day = cls.deal_weapon_day(number)
                        name = "死亡之翼{}天".format(day)
                        value = number % 1000
                        return {"option": "20005", "need_type": "1", "value": value, "name": name}
                    if weapon == 20006:
                        day = cls.deal_weapon_day(number)
                        name = "雷鸣宙斯{}天".format(day)
                        value = number % 1000
                        return {"option": "20006", "need_type": "1", "value": value, "name": name}
                    if weapon == 20007:
                        day = cls.deal_weapon_day(number)
                        name = "暗夜魅影{}天".format(day)
                        value = number % 1000
                        return {"option": "20007", "need_type": "1", "value": value, "name": name}
                    if weapon == 20008:
                        day = cls.deal_weapon_day(number)
                        name = "九五至尊{}天".format(day)
                        value = number % 1000
                        return {"option": "20008", "need_type": "1", "value": value, "name": name}
                    if weapon == 20010:
                        day = cls.deal_weapon_day(number)
                        name = "恭贺新春{}天".format(day)
                        value = number % 1000
                        return {"option": "20010", "need_type": "1", "value": value, "name": name}

    @classmethod
    def deal_props_info(cls, name, number):
        if isinstance(name, list) and isinstance(number, list):
            reward = []
            for key, value in zip(name, number):
                prop = cls.get_for_deal(key, value)
                reward.append(prop)
        else:
            return cls.get_for_deal(name, number)

    @classmethod
    def deal_integral_info(cls, key_info, value):
        new_name = ""
        if key_info == "coin":
            new_name = "{}金币".format(value)
        if key_info == "diamond":
            new_name = "{}钻石".format(value)
        if key_info == "silver_coupon":
            new_name = "{}话费券".format(value)
        if key_info == "target":
            new_name = "{}靶场券".format(value)
        if key_info.isdigit():
            pro_info = int(key_info)
            if pro_info == 202:
                new_name = "全屏冰冻*{}".format(value)
            if pro_info == 203:
                new_name = "狂暴*{}".format(value)
            # if pro_info == 204:
            #     new_name = "超级武器（{}）".format(value)
            if pro_info == 205:
                new_name = "召唤*{}".format(value)
            if pro_info == 206:
                new_name = "加速*{}".format(value)
            if pro_info == 211:
                new_name = "青铜宝箱*{}".format(value)
            if pro_info == 212:
                new_name = "白银宝箱*{}".format(value)
            if pro_info == 213:
                new_name = "黄金宝箱*{}".format(value)
            if pro_info == 214:
                new_name = "至尊宝箱*{}".format(value)
            if pro_info == 215:
                new_name = "绿灵石*{}".format(value)
            if pro_info == 216:
                new_name = "蓝魔石*{}".format(value)
            if pro_info == 217:
                new_name = "紫晶石*{}".format(value)
            if pro_info == 218:
                new_name = "血精石*{}".format(value)
            if pro_info == 219:
                new_name = "强化精华*{}".format(value)
            if pro_info == 220:
                new_name = "创房卡*{}".format(value)
            if pro_info == 701:
                new_name = "毒龙蛋"
            if pro_info == 702:
                new_name = "冰龙蛋"
            if pro_info == 703:
                new_name = "火龙蛋"
            if pro_info == 704:
                new_name = "圣龙蛋"
            if pro_info == 601:
                new_name = "蓝色宝箱"
            if pro_info == 602:
                new_name = "紫色宝箱"
            if pro_info == 603:
                new_name = "钻石宝箱"
            if pro_info == 1328:
                new_name = "白银钥匙*{}".format(value)
            if pro_info == 1329:
                new_name = "黄金钥匙*{}".format(value)
            if pro_info == 1330:
                new_name = "白金钥匙*{}".format(value)
            if pro_info == 1331:
                new_name = "白银宝箱*{}".format(value)
            if pro_info == 1332:
                new_name = "黄金宝箱*{}".format(value)
            if pro_info == 1333:
                new_name = "白金宝箱*{}".format(value)
            if pro_info == 1207:
                new_name = "风暴狮角*{}".format(value)
            if pro_info == 1351:
                new_name = "龙舟券*{}".format(value)

        prop_data = cls.get_for_deal(key_info, value)
        return new_name, prop_data

    @classmethod
    def get_for_deal(cls, key, value, count=None):
        key_info = key.encode('utf-8')
        value = int(value)
        if key_info == "power":
            return {"power": value}
        if key_info == "diamond":
            return {"diamond": value}
        if key_info == "target":
            return {"target": value}
        if key_info == "coin":
            return {"coin": value}
        if key_info == "silver_coupon":
            return {"silver_coupon": value}
        if key_info.isdigit():
            prop = []
            keys = int(key_info)
            if keys > 20000:
                if count:
                    count_data = count
                else:
                    count_data = 1
                weapon = keys * 1000 + value
                prop.append({"id": weapon, "count": count_data})
                return {"props": prop}
            else:
                prop.append({"id": keys, "count": value})
                return {"props": prop}


    @classmethod
    def convert_reward(self, rewards_info):
        if 'chip' in rewards_info:
            chip = rewards_info['chip']
            return {"name":"chip","value":chip}
        if 'diamond' in rewards_info:
            diamond = rewards_info['diamond']
            return {"name": "diamond", "value": diamond}
        if 'fake_chip' in rewards_info:
            fake_chip = rewards_info['fake_chip']
            return {"name": "fake_chip", "value": fake_chip}
        if 'coupon' in rewards_info:
            coupon = rewards_info['coupon']
            return {"name": "coupon", "value": coupon}
        if 'target' in rewards_info:
            target = rewards_info['target']
            return {"name": "target", "value": target}
        if 'props' in rewards_info:
            one = rewards_info['props'][0]
            return {"name": str(one['id']), "value": one['count']}

    @classmethod
    def find_max_num(self, num_list):
        one = num_list[0]  # 最大
        second = 0  # 次大
        for i in range(1, len(num_list)):  # 从第二个元素开始对比
            if num_list[i] > one:
                second = one
                one = num_list[i]
            elif num_list[i] > second:
                second = num_list[i]
        return int(one)

    @classmethod
    def deal_product_id(self, product):
        if product == "100900":
            return {"discount":8.5,'price': 160,'name': u'恭贺新春(8.5折)','weaponid': 20010}
        elif product == "100901":
            return {"discount":8.5,'price': 75,'name': u'雷鸣宙斯(8.5折)','weaponid': 20006}
        elif product == "100902":
            return {"discount":8.5,'price': 109,'name': u'暗夜魅影(8.5折)','weaponid': 20007}
        elif product == "100903":
            return {"discount": 7, 'price': 132, 'name': u'恭贺新春(7折)', 'weaponid': 20010}
        elif product == "100904":
            return {"discount": 8, 'price': 150, 'name': u'恭贺新春(8折)', 'weaponid': 20010}
        elif product == "100905":
            return {"discount": 7, 'price': 62, 'name': u'雷鸣宙斯(7折)', 'weaponid': 20006}
        elif product == "100906":
            return {"discount": 8, 'price': 70, 'name': u'雷鸣宙斯(8折)', 'weaponid': 20006}
        elif product == "100907":
            return {"discount":7, 'price': 90, 'name': u'暗夜魅影(7折)', 'weaponid': 20007}
        elif product == "100908":
            return {"discount": 8, 'price': 102, 'name': u'暗夜魅影(8折)', 'weaponid': 20007}
        elif product == "100909":
            return {"discount": 7, 'price': 35, 'name': u'狂怒炎龙(7折)', 'weaponid': 20004}
        elif product == "100910":
            return {"discount": 8, 'price': 40, 'name': u'狂怒炎龙(8折)', 'weaponid': 20004}
        else:
            return {"discount": 8.5, 'price': 43, 'name': u'狂怒炎龙(8.5折)', 'weaponid': 20004}

    @classmethod
    def good_type_info(self,good_type):
        if good_type == 1:
            return "数码设备"
        elif good_type == 2:
            return "充值卡"
        elif good_type == 3:
            return "游戏道具"
        elif good_type == 4:
            return "卡密"
        elif good_type == 5:
            return "卡类实物"
        else:
            return "新类型"

    @classmethod
    def deal_gift_reward(cls, reward):
        reward_info = []
        prop_id = 1
        if 'power' in reward:
            name = "鸟蛋"
            value = reward["power"]
            reward_info.append({"option": "power", "value": value, "name": name, "prop_id": prop_id})
            prop_id += 1
        if 'diamond' in reward:
            name = "钻石"
            value = reward['diamond']
            reward_info.append({"option": "diamond", "value": value, "name": name, "prop_id": prop_id})
            prop_id += 1
        if 'target' in reward:
            name = "靶劵"
            value = reward['target']
            reward_info.append({"option": "target", "value": value, "name": name, "prop_id": prop_id})
            prop_id += 1
        if 'coin' in reward:
            name = "金币"
            value = reward['coin']
            reward_info.append({"option": "coin", "value": value, "name": name, "prop_id": prop_id})
            prop_id += 1
        if 'silver_coupon' in reward:
            name = "话费劵"
            value = reward['silver_coupon']
            reward_info.append({"option": "silver_coupon", "value": value, "name": name, "prop_id": prop_id})
            prop_id += 1
        if 'auto_shot' in reward:
            name = "自动开炮"
            value = reward['auto_shot']
            reward_info.append({"option": "auto_shot", "value": value, "name": name, "prop_id": prop_id})
            prop_id += 1
        if 'weapon' in reward:
            for info in reward['weapon']:
                if info == 20001:
                    reward_info.append({"option": "20001", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20002:
                    reward_info.append({"option": "20002", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20003:
                    reward_info.append({"option": "20003", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20004:
                    reward_info.append({"option": "20004", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20005:
                    reward_info.append({"option": "20005", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20006:
                    reward_info.append({"option": "20006", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20007:
                    reward_info.append({"option": "20007", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20008:
                    reward_info.append({"option": "20008", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20010:
                    reward_info.append({"option": "20010", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20011:
                    reward_info.append({"option": "20011", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20012:
                    reward_info.append({"option": "20012", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20013:
                    reward_info.append({"option": "20013", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20014:
                    reward_info.append({"option": "20014", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20015:
                    reward_info.append({"option": "20015", "value": "life", "prop_id": prop_id})
                    prop_id += 1
                if info == 20016:
                    reward_info.append({"option": "20016", "value": "life", "prop_id": prop_id})
                    prop_id += 1
        if 'props' in reward:
            for pro in reward['props']:
                number = int(pro["id"])
                if number < 20001000:
                    if pro["id"] == 201:
                        name = "锁定"
                        value = pro["count"]
                        reward_info.append({"option": "201", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 202:
                        name = "冰冻"
                        value = pro["count"]
                        reward_info.append({"option": "202", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 203:
                        name = "狂暴"
                        value = pro["count"]
                        reward_info.append({"option": "203", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 204:
                        name = "超级武器"
                        value = pro["count"]
                        reward_info.append({"option": "204", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 205:
                        name = "召唤"
                        value = pro["count"]
                        reward_info.append({"option": "205", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 206:
                        name = "加速"
                        value = pro["count"]
                        reward_info.append({"option": "206", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 211:
                        name = "青铜宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "211", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 212:
                        name = "白银宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "212", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 213:
                        name = "黄金宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "213", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 214:
                        name = "至尊宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "214", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 215:
                        name = "绿灵石"
                        value = pro["count"]
                        reward_info.append({"option": "215", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 216:
                        name = "蓝魔石"
                        value = pro["count"]
                        reward_info.append({"option": "216", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 217:
                        name = "紫晶石"
                        value = pro["count"]
                        reward_info.append({"option": "217", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 218:
                        name = "血精石"
                        value = pro["count"]
                        reward_info.append({"option": "218", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 219:
                        name = "强化石"
                        value = pro["count"]
                        reward_info.append({"option": "219", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 220:
                        name = "创房卡"
                        value = pro["count"]
                        reward_info.append({"option": "220", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 301:
                        name = "灵魂宝石"
                        value = pro["count"]
                        reward_info.append({"option": "301", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1

                    if pro["id"] == 1303:
                        name = "风暴结晶"
                        value = pro["count"]
                        reward_info.append({"option": "1303", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1

                    if pro["id"] == 1304:
                        name = "逐风者的碎片"
                        value = pro["count"]
                        reward_info.append({"option": "1304", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1

                    if pro["id"] == 1302:
                        name = "大福袋"
                        value = pro["count"]
                        reward_info.append({"option": "1302", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1305:
                        name = "礼盒"
                        value = pro["count"]
                        reward_info.append({"option": "1305", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1311:
                        name = "神秘礼盒"
                        value = pro["count"]
                        reward_info.append({"option": "1311", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1611:
                        name = "许愿卡"
                        value = pro["count"]
                        reward_info.append({"option": "1611", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1328:
                        name = "白银钥匙"
                        value = pro["count"]
                        reward_info.append({"option": "1328", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1329:
                        name = "黄金钥匙"
                        value = pro["count"]
                        reward_info.append({"option": "1329", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1330:
                        name = "白金钥匙"
                        value = pro["count"]
                        reward_info.append({"option": "1330", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1331:
                        name = "白银宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "1331", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1332:
                        name = "黄金宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "1332", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1333:
                        name = "白金宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "1333", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1207:
                        name = "风暴狮角"
                        value = pro["count"]
                        reward_info.append({"option": "1207", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1

                    if pro["id"] == 1351:
                        name = "龙舟券"
                        value = pro["count"]
                        reward_info.append({"option": "1351", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                    if pro["id"] == 1321:
                        name = "八宝粽子"
                        value = pro["count"]
                        reward_info.append({"option": "1321", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                    if pro["id"] == 1327:
                        name = "捕鸟宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "1327", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                    if pro["id"] == 601:
                        name = "青铜宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "601", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 602:
                        name = "白银宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "602", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 603:
                        name = "黄金宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "603", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 604:
                        name = "至尊宝箱"
                        value = pro["count"]
                        reward_info.append({"option": "604", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 701:
                        name = "毒龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "701", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 702:
                        name = "冰龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "702", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 703:
                        name = "火龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "703", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 704:
                        name = "圣龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "704", "value": value, "name": name, "bound": "2", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1201:
                        name = "锁定"
                        value = pro["count"]
                        reward_info.append({"option": "1201", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1202:
                        name = "冰冻"
                        value = pro["count"]
                        reward_info.append({"option": "1202", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1203:
                        name = "狂暴"
                        value = pro["count"]
                        reward_info.append({"option": "1203", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1205:
                        name = "召唤"
                        value = pro["count"]
                        reward_info.append({"option": "1205", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1206:
                        name = "加速"
                        value = pro["count"]
                        reward_info.append({"option": "1206", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1301:
                        name = "灵魂宝石"
                        value = pro["count"]
                        reward_info.append({"option": "1301", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1215:
                        name = "绿灵石"
                        value = pro["count"]
                        reward_info.append({"option": "1215", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1216:
                        name = "蓝魔石"
                        value = pro["count"]
                        reward_info.append({"option": "1216", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1217:
                        name = "紫晶石"
                        value = pro["count"]
                        reward_info.append({"option": "1217", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1218:
                        name = "血精石"
                        value = pro["count"]
                        reward_info.append({"option": "1218", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1219:
                        name = "强化石"
                        value = pro["count"]
                        reward_info.append({"option": "1219", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1220:
                        name = "创房卡"
                        value = pro["count"]
                        reward_info.append({"option": "1220", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1701:
                        name = "毒龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "1701", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1702:
                        name = "冰龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "1702", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1703:
                        name = "火龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "1703", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1
                    if pro["id"] == 1704:
                        name = "圣龙蛋"
                        value = pro["count"]
                        reward_info.append({"option": "1704", "value": value, "name": name, "bound": "1", "prop_id": prop_id})
                        prop_id += 1

                elif number > 200010000:
                    weapon = number / 10000
                    if weapon == 20001:
                        day = cls.deal_weapon_day(number)
                        name = "流沙之鳞{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20001", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20002:
                        day = cls.deal_weapon_day(number)
                        name = "冰翼猎手{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20002", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20003:
                        day = cls.deal_weapon_day(number)
                        name = "翡翠荆棘{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20003", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20004:
                        day = cls.deal_weapon_day(number)
                        name = "狂怒炎龙{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20004", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20005:
                        day = cls.deal_weapon_day(number)
                        name = "死亡之翼{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20005", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20006:
                        day = cls.deal_weapon_day(number)
                        name = "雷鸣宙斯{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20006", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20007:
                        day = cls.deal_weapon_day(number)
                        name = "暗夜魅影{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20007", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20008:
                        day = cls.deal_weapon_day(number)
                        name = "九五至尊{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20008", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20010:
                        day = cls.deal_weapon_day(number)
                        name = "恭贺新春{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20010", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20011:
                        day = cls.deal_weapon_day(number)
                        name = "工地之光{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20011", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20012:
                        day = cls.deal_weapon_day(number)
                        name = "翡翠梦境{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20012", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20013:
                        day = cls.deal_weapon_day(number)
                        name = "逐风者{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20013", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20014:
                        day = cls.deal_weapon_day(number)
                        name = "天炎之怒{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20014", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20015:
                        day = cls.deal_weapon_day(number)
                        name = "蓝魔冰晶{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20015", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20016:
                        day = cls.deal_weapon_day(number)
                        name = "夏日清檬{}分钟".format(day)
                        value = number % 10000
                        reward_info.append({"option": "20016", "need_type": "2", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                else:
                    weapon = number / 1000
                    if weapon == 20001:
                        day = cls.deal_weapon_day(number)
                        name = "流沙之鳞{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20001", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20002:
                        day = cls.deal_weapon_day(number)
                        name = "冰翼猎手{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20002", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20003:
                        day = cls.deal_weapon_day(number)
                        name = "翡翠荆棘{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20003", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20004:
                        day = cls.deal_weapon_day(number)
                        name = "狂怒炎龙{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20004", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20005:
                        day = cls.deal_weapon_day(number)
                        name = "死亡之翼{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20005", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20006:
                        day = cls.deal_weapon_day(number)
                        name = "雷鸣宙斯{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20006", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20007:
                        day = cls.deal_weapon_day(number)
                        name = "暗夜魅影{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20007", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20008:
                        day = cls.deal_weapon_day(number)
                        name = "九五至尊{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20008", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20010:
                        day = cls.deal_weapon_day(number)
                        name = "恭贺新春{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20010", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20011:
                        day = cls.deal_weapon_day(number)
                        name = "工地之光{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20011", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20012:
                        day = cls.deal_weapon_day(number)
                        name = "翡翠梦境{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20012", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20013:
                        day = cls.deal_weapon_day(number)
                        name = "逐风者{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20013", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20014:
                        day = cls.deal_weapon_day(number)
                        name = "天炎之怒{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20014", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20015:
                        day = cls.deal_weapon_day(number)
                        name = "蓝魔冰晶{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20015", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
                    if weapon == 20016:
                        day = cls.deal_weapon_day(number)
                        name = "夏日清檬{}天".format(day)
                        value = number % 1000
                        reward_info.append({"option": "20016", "need_type": "1", "value": value, "name": name, "prop_id": prop_id})
                        prop_id += 1
        return reward_info

    @classmethod
    def deal_weapon_day(cls, result):
        weapon = result / 1000
        hundreds = (result - weapon * 1000) / 100
        tens = (result - weapon * 1000 - hundreds * 100) / 10
        ones = (result - weapon * 1000 - hundreds * 100 - tens * 10) % 10
        day = int(hundreds * 100 + tens * 10 + ones)
        return day

    @classmethod
    def verify_productId(cls, product, price=None):
        activity_list = ["103201", "103202", "103203", "103204", "103205", "103206"]
        deal_list = ["102004", "103401"]
        old_data = ProductList.objects.filter(product_id=product).values('product_data').first()
        gift = GiftInfo.objects.filter(gift_id=product).values('gift_name').first()
        if old_data:
            json_info = Context.json_loads(old_data['product_data'])
            product_id = str(product)
            if product_id in deal_list:
                good_name = cls.good_product_id(product_id, price)
            else:
                good_name = json_info["name"]
            return good_name
        elif gift:
            return gift["gift_name"]
        else:
            product_Id = str(product)
            if product_Id in activity_list:
                product_name = cls.activity_gift_bag(product_Id)
            else:
                product_name = product
            return product_name

    @classmethod
    def good_product_id(cls, product_id, price):
        if product_id == "102004":
            return "每日{}元礼包".format(price)
        elif product_id == "103401":
            return "神秘礼盒x1"
        else:
            return product_id

    @classmethod
    def activity_gift_bag(cls, product_id):
        if product_id == "103201":
            return "专属礼包_超值宝石"
        elif product_id == "103202":
            return "专属礼包_超值强化"
        elif product_id == "103203":
            return "专属礼包_灵魂特惠"
        elif product_id == "103204":
            return "专属礼包_超值礼包"
        elif product_id == "103205":
            return "专属礼包_超值技能"
        elif product_id == "103206":
            return "专属礼包_金币特惠"
        else:
            return product_id

    @classmethod
    def deal_Dragon_Boat(cls, result):
        dragon_info = {}
        for index,data in result.items():
            boat = {}
            need = ["A","B","C","D"]
            if data.has_key("limit"):
                boat.update({"limit": data["limit"]})
            else:
                boat.update({"limit": ""})
            if data.has_key("need"):
                for letter in need:
                    if data["need"].has_key(letter):
                        continue
                    else:
                        data["need"].update({letter:""})
                boat.update({"need": data["need"]})
            else:
                boat.update({"need": {"A": "", "B": "", "C": "", "D": ""}})

            if data.has_key("reward"):
                reward_list = cls.deal_gift_reward(data["reward"])
                len_reward = len(reward_list)
                if len_reward != 2:
                    for n in range(0, 2-len_reward):
                        reward_list.append({"option": "chip", "value": ""})
                boat.update({"reward": reward_list})
            else:
                boat.update({"reward": [{"option": "chip", "value": ""},{"option": "chip", "value": ""}]})
            dragon_info.update({index: boat})

        return dragon_info

    @classmethod
    def deal_auto_shot_reward(cls, gift_name, gift_number, day_info=None, bound_info=None):  # day_info 炮的区分
        reward, prop, weapon_list = {}, [], []
        if day_info:
            day_list = day_info
        else:
            day_list = range(10, len(gift_name)+10)

        if bound_info:
            bound_list = bound_info
        else:
            bound_list = [2]*len(gift_name)

        for key, value, day, bound in zip(gift_name, gift_number, day_list, bound_list):
            day, bound = int(day), int(bound)
            props_info = {}
            key = key.encode('utf-8')
            values = value.encode('utf-8')
            if values == "life" and key.isdigit():
                if int(key) > 20000:
                    weapon_list.append(int(key))
                    reward.update({"weapon": weapon_list})
                    continue
                else:
                    return reward
            else:
                value = int(values)
                if key == "coin":
                    reward.update({key: value})
                if key == "diamond":
                    reward.update({key: value})
                if key == "target":
                    reward.update({key: value})
                if key == "power":
                    reward.update({key: value})
                if key == "silver_coupon":
                    reward.update({key: value})
                if key == "auto_shot":
                    reward.update({key: value})
                if key.isdigit():
                    key = int(key)
                    if key > 20000:
                        if bound == 1:
                            if day == 2:
                                pro_id = (key + 1000) * 10000 + value
                            else:
                                pro_id = (key + 1000) * 1000 + value
                        else:
                            if day == 2:
                                pro_id = key * 10000 + value
                            else:
                                pro_id = key * 1000 + value
                        props_info.update({"id": pro_id, "count": 1})
                    else:
                        if bound == 1:
                            bound_key = key + 1000
                        else:
                            bound_key = key
                        props_info.update({"id": bound_key, "count": value})
                    prop.append(props_info)
                    reward.update({"props": prop})
        return reward

    @classmethod
    def deal_props_reward(cls, name_list, number_list, day_list, slice=None):
        reward_list = []
        if slice:
            name_list = [name_list[i:i + slice] for i in range(0, len(name_list), slice)]
            number_list = [number_list[i:i + slice] for i in range(0, len(number_list), slice)]
            day_list = [day_list[i:i + slice] for i in range(0, len(day_list), slice)]
            for name_info, value_info, day_info in zip(name_list, number_list, day_list):
                result = cls.get_prop_reward(name_info, value_info, day_info)
                if len(result) > 0:
                    reward_list.append(result)
                else:
                    continue
        else:
            reward = cls.get_prop_reward(name_list, number_list, day_list)
            if len(reward) > 0:
                reward_list.append(reward)
        return reward_list

    @classmethod
    def get_prop_reward(cls, name_list, number_list, day_list):
        reward, weapon_list = {}, []
        for key, value, day in zip(name_list, number_list, day_list):
            props_info = {}
            key, values, day= key.encode('utf-8'), value.encode('utf-8'), day.encode('utf-8')
            if values == "life" and key.isdigit():
                if int(key) > 20000:
                    weapon_list.append(int(key))
                    reward.update({"weapon": weapon_list})
                else:
                    return reward
            elif values == "":
                return reward
            else:
                value = int(values)
                if key == "coin":
                    reward.update({key: value})
                if key == "diamond":
                    reward.update({key: value})
                if key == "target":
                    reward.update({key: value})
                if key == "power":
                    reward.update({key: value})
                if key == "silver_coupon":
                    reward.update({key: value})
                if key == "auto_shot":
                    reward.update({key: value})
                if key.isdigit():
                    key, day = int(key), int(day)

                    if key > 20000:
                        if day == 2:
                            pro_id = key * 10000 + value
                        else:
                            pro_id = key * 1000 + value
                        props_info.update({"id": pro_id, "count": 1})
                    else:
                        props_info.update({"id": key, "count": value})
                    if reward.has_key("props"):
                        reward["props"].append(props_info)
                    else:
                        reward["props"] = []
                        reward["props"].append(props_info)
        return reward

    @classmethod
    def get_good_cost(cls, pid):
        if not isinstance(pid, str):
            str_pid = str(pid)
        else:
            str_pid = pid
        cost = {
            "140001": 160,
            "140002": 129,
            "140003": 305,
            "140004": 306,
            "140005": 298,
            "140006": 245,
            "140007": 245,
            "140008": 179,
            "140009": 98,
            "140010": 128,
            "140011": 175,
            # "140012": 0,
            "140013": 326,
            "140014": 469,
            "140015": 100,
            "140016": 60,
            "140017": 60,
            "140018": 83,
            "140019": 75,
            "140020": 20,
            "140021": 20,
            "140022": 20,
            "140023": 60,
            "140024": 60,
            "140025": 60,
            # "140026": 0,
            "140027": 50,
            "140028": 50,
            "140029": 100,
            "140030": 100,
            # "140031": 0,
            # "140032": 0,
            # "140033": 0,
            # "140034": 0,
            # "140035": 0,
            "140036": 200,
            "140037": 500,
            "140038": 500,
            "150001": 50,
            "150002": 50,
            "150003": 50,
            "150004": 5000,
            "150005": 3000,
            "150006": 1000,
            "150007": 500,
            "150008": 200,
            "150009": 100,
        }
        if str_pid in cost:
            return cost[str_pid]
        else:
            return 0

    @classmethod
    def exchange_info(cls, good_type, result):
        if good_type == 1:
            name, express_number = result["name"], result["express_number"]
            led = "恭喜您兑换{}已发货，运单号为{}请注意查收，如有任何疑问，请联系客服咨询。客服微信：ttbn999".format(name, express_number)
        elif good_type == 3 or good_type == 5:
            name = result["name"]
            led = "恭喜您兑换{}，已到账，如有任何疑问，请联系客服咨询。客服微信：ttbn999".format(name)
        elif good_type == 2 or good_type == 4 or good_type == -1:
            name, card_number, card_secret = result["name"], result["card_number"], result["card_secret"]
            # led = "<size=30>亲爱的玩家:您兑换的<color=#FF0000>{}</color>已发放，卡密如下：<b>         卡号：{} 密码：{}</b>           我们建议您保留此邮件作为记录之用，如有任何疑问与<b>官方客服</b>（<b>客服微信：</b><color=#FF0000>ttbn789</color>）联系，谢谢~！</size>".format(name, card_number, card_secret)
            led = "<size=30>亲爱的玩家:\n您兑换的<color=#FF0000>{}</color>已发放，卡密如下：\n<b>卡号：{}\n密码：{}</b>\n 我们建议您保留此邮件作为记录之用，如有任何疑问与<b>官方客服</b>（<b>客服微信：</b><color=#FF0000>ttbn999</color>）联系，谢谢~！</size>".format(name, card_number, card_secret)
            # if good_type == -1:
            #     led = "恭喜您成功兑换{}，卡号：{},密码：{}  为了您的账号安全，请到兑换商城完善您的手机信息，如有任何疑问，请联系客服咨询。客服微信：ttbn789".format(name, card_number, card_secret)
            # else:
            #     led = "恭喜您成功兑换{}，卡号：{},密码：{}  请您尽快前往兑换，如有任何疑问，请联系客服咨询。客服微信：ttbn789".format(name, card_number, card_secret)
        else:
            name, express_number = result["name"], result["express_number"]
            led = "恭喜您兑换{}已发货，运单号为{}请注意查收，如有任何疑问，请联系客服咨询。客服微信：ttbn999".format(name, express_number)
        return led
