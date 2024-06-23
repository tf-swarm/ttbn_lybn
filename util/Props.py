#!/usr/bin/env python
# -*- coding=utf-8 -*-

import random
from util.context import Context


class BirdProps():
    PROP_LOCK_BIRD = 201        # 锁定
    PROP_FREEZE = 202           # 冰冻
    PROP_VIOLENT = 203          # 狂暴
    PROP_SUPER_WEAPON = 204     # 超级武器
    PROP_PORTAL = 205           # 召唤
    PROP_QUICK = 206            # 加速

    PROP_EGG_BRONZE = 211       # 青铜宝箱
    PROP_EGG_SILVER = 212       # 白银宝箱
    PROP_EGG_GOLD = 213         # 黄金宝箱
    PROP_EGG_COLOR = 214        # 至尊宝箱
    GREEN_STONE = 215           # 绿灵石
    YELLOW_STONE = 216          # 血精石
    VIOLET_STONE = 217          # 蓝魔石
    RED_STONE = 218             # 紫晶石
    GEM = 219                   # 强化精华
    CREATE_TABLE_CARD = 220     # 创房卡


    # 新增掉落测试
    PROP_COUPON = 3             # 鸟卷掉落
    TARGET_COUPON = 4             # 靶卷掉落

    PRICE_DICT = {
        202: 2500,
        203: 25000,
        204: 100000,
        205: 2500,
        211: 150000,
        212: 300000,
        213: 500000,
        214: 1000000,
        215: 10000,
        216: 10000,
        217: 10000,
        218: 10000,
        219: 25000,
        220: 5000,
        'diamond': 500,
        'coupon': 5000,
        'target': 20000,
    }

    @classmethod
    def get_props_desc(cls, pid):
        if pid == cls.PROP_LOCK_BIRD:
            return u'锁定'
        elif pid == cls.PROP_FREEZE:
            return u'冰冻'
        elif pid == cls.PROP_VIOLENT:
            return u'狂暴'
        elif pid == cls.PROP_PORTAL:
            return u'召唤'
        elif pid == cls.PROP_QUICK:
            return u'加速'

        elif pid == cls.PROP_EGG_BRONZE:
            return u'青铜宝箱'
        elif pid == cls.PROP_EGG_SILVER:
            return u'白银宝箱'
        elif pid == cls.PROP_EGG_GOLD:
            return u'黄金宝箱'
        elif pid == cls.PROP_EGG_COLOR:
            return u'至尊宝箱'
        elif pid == cls.GREEN_STONE:
            return u'绿灵石'
        elif pid == cls.RED_STONE:
            return u'血精石'
        elif pid == cls.YELLOW_STONE:
            return u'蓝魔石'
        elif pid == cls.VIOLET_STONE:
            return u'紫晶石'
        elif pid == cls.GEM:
            return u'强化精华'
        elif pid == cls.CREATE_TABLE_CARD:
            return u'创房卡'

        # 新增掉落测试
        elif pid == cls.PROP_COUPON:
            return u'鸟券'
        elif pid == cls.TARGET_COUPON:
            return u'靶券'
        elif pid == 220:
            return u'创房卡'
        elif pid == 20000:
            return u'零式火炮'
        elif pid == 20001:
            return u'流沙之鳞'
        elif pid == 20002:
            return u'冰翼猎手'
        elif pid == 20003:
            return u'翡翠荆棘'
        elif pid == 20004:
            return u'狂怒炎龙'
        elif pid == 20005:
            return u'死亡之翼'
        elif pid == 20006:
            return u'雷鸣宙斯'
        elif pid == 20007:
            return u'暗夜魅影'
        elif pid == 20008:
            return u'九五至尊'
        elif pid == 20010:
            return u'恭贺新春'

        # 限时炮道具
        elif pid >= 20000*1000 and pid <= 30000*1000:
            props_id = int(pid/1000)
            props_day = int(pid % 1000)
            name = u''
            if props_id == 20000:
                name += u'零式火炮'
            if props_id == 20001:
                name += u'流沙之鳞'
            if props_id == 20002:
                name += u'冰翼猎手'
            if props_id == 20003:
                name += u'翡翠荆棘'
            if props_id == 20004:
                name += u'狂怒炎龙'
            if props_id == 20005:
                name += u'死亡之翼'
            if props_id == 20006:
                name += u'雷鸣宙斯'
            if props_id == 20007:
                name += u'暗夜魅影'
            if props_id == 20008:
                name += u'九五至尊'
            if props_id == 20010:
                name += u'恭贺新春'
            name = name + u'%d天'%(props_day)
            return name

    @classmethod
    def get_reward_str(cls, reward):
        desc = []
        keys = ['chip', 'diamond', 'coupon','target']
        names = [u'鸟蛋', u'钻石', u'鸟券', u'靶券']
        for key, name in zip(keys, names):
            if key in reward:
                desc.append(u'%d%s' % (reward[key], name))

        prop = reward.get('props')
        if prop:
            for one in prop:
                _ = props.get_props_desc(one['id']) + u'%d个' % one['count']
                desc.append(_)
        auto_shot = reward.get('auto_shot')
        if auto_shot:
            desc.append(u'自动开炮%d天'%auto_shot)
        weapon = reward.get(u'weapon')
        if weapon:
            for i in weapon:
                n = "{}永久".format(props.get_props_desc(i))
                desc.append(n)
        return u', '.join(desc)

    @classmethod
    def get_zongzi_name(cls, field):
        if field == "A":
            return "大枣粽"
        elif field == "B":
            return "红豆粽"
        elif field == "C":
            return "蛋黄粽"
        elif field == "D":
            return "鲜肉粽"
        else:
            return ""

    # 获取商品的鸟蛋价值
    @classmethod
    def get_props_price(cls, rewards_info):
        result = 0
        if 'chip' in rewards_info:
            result += int(rewards_info['chip'], 0)
        if 'diamond' in rewards_info:
            diamond = int(rewards_info['diamond'], 0) * cls.PRICE_DICT['diamond']
            result += diamond
        if 'coupon' in rewards_info:
            coupon = int(rewards_info['coupon'], 0) * cls.PRICE_DICT['coupon']
            result += coupon
        if 'target' in rewards_info:
            target = int(rewards_info['target'], 0) * cls.PRICE_DICT['target']
            result += target
        if 'props' in rewards_info:
            for one in rewards_info['props']:
                props = (int(one['count'], 0) * cls.PRICE_DICT[one['id']])
                result += props
        return result

props = BirdProps()