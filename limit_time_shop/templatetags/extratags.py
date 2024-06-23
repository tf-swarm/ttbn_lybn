# -*- coding: utf-8 -*-
from django import template
import json
import time
from login_manage.models import ChannelList
from util.context import Context
import sys
from util.tool import Time
register = template.Library()
reload(sys)
sys.setdefaultencoding("utf8")


@register.filter(name='channel_name')
def channel_name(channel):
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    if isinstance(channel,list):
        info = ""
        for chl in channel:
            if not isinstance(chl,str):
                chl = str(chl)
                name = channel_deal_with(chl,chanel_info)
            else:
                name = channel_deal_with(chl,chanel_info)
            info = info + name
            info = info + " "
    else:
        info = channel_deal_with(channel,chanel_info)
    return info


def channel_deal_with(channelid, chanel_info):
    channelid = str(channelid)
    if chanel_info.has_key(channelid):
        return chanel_info[channelid]
    else:
        if channelid == "1":
            return '硬核渠道汇总'
        elif channelid == "2":
            return 'CPL渠道汇总'
        elif channelid == "3":
            return 'CPS渠道汇总'
        elif channelid == "1004_10":
            return 'OPPO游客'
        elif channelid == "1004_11":
            return 'OPPO广告包游客'
        else:
            return channelid


@register.filter(name='currency_type')
def currency_type(money):
    money = int(money)
    if money == 1:
        return '鸟蛋'
    elif money == 2:
        return '钻石'
    elif money == 3:
        return 'RMB'
    elif money == 5:
        return '鸟券'
    elif money == 6:
        return '积分'
    elif money == 7:
        return '话费券'
    elif money == 8:
        return '火龙蛋'
    elif money == 9:
        return '圣龙蛋'
    elif money == 10:
        return '冰龙蛋'
    elif money == 11:
        return '龙舟券'
    else:
        return '积分卡'


@register.filter(name='shop_name')
def shop_name(good_name):
    good_name = str(good_name)
    if good_name == "-1":
        return '白送50元'
    elif good_name == "1":
        return '生活实物'
    elif good_name == "2":
        return '卡类专区'
    elif good_name == "3":
        return '游戏道具'
    elif good_name == "5":
        return '活动专区'
    else:
        return good_name


@register.filter(name='shop_money')
def shop_money(money):
    money = int(money)
    if money == 7:
        return "话费券"
    elif money == 8:
        return "火龙蛋"
    elif money == 9:
        return "圣龙蛋"
    elif money == 10:
        return "冰龙蛋"
    elif money == 11:
        return "龙舟券"
    else:
        return money


@register.filter(name='exchange_power')
def exchange_power(money):
    chip = int(money)
    if chip == 0:
        power = 0
    else:
        power = round((float(chip) / 10000000), 2)
    return power


@register.filter(name='game_name')
def game_name(gid):
    if gid == 1:
        return '靶场'
    elif gid == 2:
        return '翻翻乐'
    elif gid == 3:
        return '大富翁'


@register.filter(name='convert_reward')
def convert_reward(rewards_info):

    if isinstance(rewards_info, unicode):
        rewards_info = eval(rewards_info)
    return props.get_reward_str(rewards_info)


@register.filter(name='pool_name')
def pool_name(pool_info):
    if pool_info != 0:
        result = "元兑换码"
        value = pool_info
        reward = "{}{}".format(value,result)
        return reward
    else:
        result = "免费码"
        return result


@register.filter(name='count_down')
def count_down(days):
    day_time = int(time.time())
    time_difference = (days - day_time)
    if time_difference % 86400 == 0:
        days = time_difference / 86400
    else:
        days = (time_difference / 86400) + 1
    return days


@register.filter(name='stop_deal')
def stop_deal(Timestamp):
    """红包终止处理"""
    Timestamp = Time.str_to_timestamp(Timestamp.encode('utf-8'))
    day_time = int(time.time())
    if day_time >Timestamp :
        return False
    else:
        return True


@register.filter(name='hideCard')
def hideCard(cardNo):
    length = len(cardNo)
    beforeLength = 0
    afterLength = 0
    replaceSymbol = "*"
    data = []
    for i, x in enumerate(cardNo):
        if i < beforeLength or i >= (length - afterLength):
            data.append(x)
        else:
            data.append(replaceSymbol)
    info_str = ''.join(data)
    return info_str[:18]


@register.filter(name='transition')
def transition(number):
    if not isinstance(number,int):
        new_data = int(number)
        info = new_data - new_data
    else:
        info = number - number
    return info


@register.filter(name='recharge_info')
def recharge_info(reward):
    if reward.has_key("name"):
        return reward["name"]
    elif reward.has_key("c"):
        return "{}鸟蛋".format(reward["c"])
    elif reward.has_key("d"):
        return "{}钻石".format(reward["d"])


@register.filter(name='burying_time')
def burying_time(b_time):
    if isinstance(b_time,int):
        return Time.timestamp_to_str(b_time)
    else:
        return b_time


class BirdProps():
    # 未绑定
    PROP_COUPON = 3  # 奖券
    PROP_LOCK_BIRD = 201  # 锁定
    PROP_FREEZE = 202  # 冰冻
    PROP_VIOLENT = 203  # 狂暴
    PROP_SUPER_WEAPON = 204  # 超级武器
    PROP_PORTAL = 205  # 召唤
    PROP_QUICK = 206  # 加速

    PROP_EGG_BRONZE = 211  # 青铜宝箱
    PROP_EGG_SILVER = 212  # 白银宝箱
    PROP_EGG_GOLD = 213  # 黄金宝箱
    PROP_EGG_COLOR = 214  # 至尊宝箱
    GREEN_STONE = 215  # 绿灵石
    ORANGE_STONE = 216  # 蓝魔石
    VIOLET_STONE = 217  # 紫晶石
    RED_STONE = 218  # 血精石
    GEM = 219  # 强化石
    CREATE_TABLE_CARD = 220  # 创房卡
    ROOM_CARD = 225  # 房卡
    LUCKY_BAG = 302  # 福袋

    # 绑定
    LOOK_PROP_LOCK_BIRD = 1201  # 锁定
    LOOK_PROP_FREEZE = 1202  # 冰冻
    LOOK_PROP_VIOLENT = 1203  # 狂暴
    LOOK_PROP_SUPER_WEAPON = 1204  # 超级武器
    LOOK_PROP_PORTAL = 1205  # 召唤
    LOOK_PROP_QUICK = 1206  # 加速
    LOOK_PROP_EGG_BRONZE = 1211  # 青铜宝箱
    LOOK_PROP_EGG_SILVER = 1212  # 白银宝箱
    LOOK_PROP_EGG_GOLD = 1213  # 黄金宝箱
    LOOK_PROP_EGG_COLOR = 1214  # 至尊宝箱
    LOOK_GREEN_STONE = 1215  # 绿灵石
    LOOK_ORANGE_STONE = 1216  # 蓝魔石
    LOOK_VIOLET_STONE = 1217  # 紫晶石
    LOOK_RED_STONE = 1218  # 血精石
    LOOK_GEM = 1219  # 强化石
    LOOK_CREATE_TABLE_CARD = 1220  # 创房卡
    LOOK_ROOM_CARD = 1225  # 房卡

    # 二期新增物品
    PROP_SOUL_STONE = 301  # 灵魂宝石
    PROP_WIND_RAFFLE = 303  # 风暴结晶
    PROP_WEAPON_DEBRIS = 304  # 逐风者的碎片
    PROP_LUCKY_BAG = 1302  # 福袋
    PROP_SUMMER_BAG = 1305  # 礼盒
    PROP_MYSTICAL_BAG = 1311  # 神秘礼盒
    PROP_Dragon_Boat = 1351  # 龙舟券
    PROP_Traditional = 1321  # 八宝粽子
    PROP_Bird_Box = 1327  # 捕鸟宝箱
    PROP_Wish_Card = 1611  # 许愿卡
    PROP_Silver_Key = 1328  # 白银钥匙
    PROP_Gold_Key = 1329  # 黄金钥匙
    PROP_Platinum_Key = 1330  # 白金钥匙
    PROP_Silver_Box = 1331  # 白银宝箱
    PROP_Gold_Box = 1332  # 黄金宝箱
    PROP_Platinum_Box = 1333  # 白金宝箱
    PROP_Storm_Unicorn = 1207  # 风暴狮角
    PROP_BOX_BRONZE = 601
    PROP_BOX_SILVER = 602
    PROP_BOX_GOLD = 603
    PROP_BOX_SMALL = 604
    PROP_BOX_BIG = 605
    PROP_BOX_S_COUPON = 606

    PROP_ARROW_1 = 701
    PROP_ARROW_2 = 702
    PROP_ARROW_3 = 703
    PROP_ARROW_4 = 704

    LOOK_PROP_SOUL_STONE = 1301  # 灵魂宝石
    LOOK_PROP_WIND_RAFFLE = 1303  # 风暴结晶
    LOOK_PROP_WEAPON_DEBRIS = 1304  # 逐风者的碎片
    LOOK_PROP_BOX_BRONZE = 1601
    LOOK_PROP_BOX_SILVER = 1602
    LOOK_PROP_BOX_GOLD = 1603
    LOOK_PROP_BOX_SMALL = 1604
    LOOK_PROP_BOX_BIG = 1605
    LOOK_PROP_BOX_S_COUPON = 1606

    LOOK_PROP_ARROW_1 = 1701
    LOOK_PROP_ARROW_2 = 1702
    LOOK_PROP_ARROW_3 = 1703
    LOOK_PROP_ARROW_4 = 1704

    def get_props_desc(self, pid):
        if pid == self.PROP_LOCK_BIRD:
            return u'锁定'
        elif pid == self.PROP_FREEZE:
            return u'冰冻'
        elif pid == self.PROP_VIOLENT:
            return u'狂暴'
        elif pid == self.PROP_SUPER_WEAPON:
            return u'超级武器'
        elif pid == self.PROP_PORTAL:
            return u'召唤'
        elif pid == self.PROP_QUICK:
            return u'加速'
        elif pid == self.PROP_EGG_BRONZE:
            return u'青铜宝箱'
        elif pid == self.PROP_EGG_SILVER:
            return u'白银宝箱'
        elif pid == self.PROP_EGG_GOLD:
            return u'黄金宝箱'
        elif pid == self.PROP_EGG_COLOR:
            return u'至尊宝箱'
        elif pid == self.GREEN_STONE:
            return u'绿灵石'
        elif pid == self.RED_STONE:
            return u'血精石'
        elif pid == self.ORANGE_STONE:
            return u'蓝魔石'
        elif pid == self.VIOLET_STONE:
            return u'紫晶石'
        elif pid == self.GEM:
            return u'强化石'
        elif pid == self.PROP_SOUL_STONE:
            return u'灵魂宝石'
        elif pid == self.LOOK_PROP_WIND_RAFFLE:
            return u'风暴结晶'
        elif pid == self.LOOK_PROP_WEAPON_DEBRIS:
            return u'逐风者的碎片'
        elif pid == self.PROP_WEAPON_DEBRIS:
            return u'逐风者的碎片'
        elif pid == self.LUCKY_BAG:
            return u'福袋'
        elif pid == self.PROP_LUCKY_BAG:
            return u'福袋'
        elif pid == self.PROP_SUMMER_BAG:
            return u'礼盒'
        elif pid == self.PROP_MYSTICAL_BAG:
            return u'神秘礼盒'
        elif pid == self.PROP_Dragon_Boat:
            return u'龙舟券'
        elif pid == self.PROP_Traditional:
            return u'八宝粽子'
        elif pid == self.PROP_Bird_Box:
            return u'捕鸟宝箱'
        elif pid == self.PROP_Wish_Card:
            return u'许愿卡'
        elif pid == self.PROP_Silver_Key:
            return u'白银钥匙'
        elif pid == self.PROP_Gold_Key:
            return u'黄金钥匙'
        elif pid == self.PROP_Platinum_Key:
            return u'白金钥匙'
        elif pid == self.PROP_Silver_Box:
            return u'白银宝箱'
        elif pid == self.PROP_Gold_Box:
            return u'黄金宝箱'
        elif pid == self.PROP_Platinum_Box:
            return u'白金宝箱'
        elif pid == self.PROP_Storm_Unicorn:
            return u'风暴狮角'
        elif pid == self.CREATE_TABLE_CARD:
            return u'创房卡'
        elif pid == self.ROOM_CARD:
            return u'房卡道具'
        elif pid == self.PROP_BOX_BRONZE:
            return u'青铜宝箱'
        elif pid == self.PROP_BOX_SILVER:
            return u'白银宝箱'
        elif pid == self.PROP_BOX_GOLD:
            return u'黄金宝箱'
        elif pid == self.LOOK_PROP_LOCK_BIRD:
            return u'绑定锁定'
        elif pid == self.LOOK_PROP_FREEZE:
            return u'绑定冰冻'
        elif pid == self.LOOK_PROP_VIOLENT:
            return u'绑定狂暴'
        elif pid == self.LOOK_PROP_SUPER_WEAPON:
            return u'绑定超级武器'
        elif pid == self.LOOK_PROP_PORTAL:
            return u'绑定召唤'
        elif pid == self.LOOK_PROP_QUICK:
            return u'绑定加速'

        elif pid == self.LOOK_PROP_EGG_BRONZE:
            return u'绑定青铜宝箱'
        elif pid == self.LOOK_PROP_EGG_SILVER:
            return u'绑定白银宝箱'
        elif pid == self.LOOK_PROP_EGG_GOLD:
            return u'绑定黄金宝箱'
        elif pid == self.LOOK_PROP_EGG_COLOR:
            return u'绑定至尊宝箱'
        elif pid == self.LOOK_GREEN_STONE:
            return u'绑定绿灵石'
        elif pid == self.LOOK_RED_STONE:
            return u'绑定血精石'
        elif pid == self.LOOK_ORANGE_STONE:
            return u'绑定蓝魔石'
        elif pid == self.LOOK_VIOLET_STONE:
            return u'绑定紫晶石'
        elif pid == self.LOOK_GEM:
            return u'绑定强化石'
        elif pid == self.LOOK_PROP_SOUL_STONE:
            return u'绑定灵魂宝石'
        elif pid == self.LOOK_CREATE_TABLE_CARD:
            return u'绑定创房卡'
        elif pid == self.LOOK_ROOM_CARD:
            return u'绑定房卡道具'
        elif pid == self.LOOK_PROP_BOX_BRONZE:
            return u'绑定青铜宝箱'
        elif pid == self.LOOK_PROP_BOX_SILVER:
            return u'绑定白银宝箱'
        elif pid == self.LOOK_PROP_BOX_GOLD:
            return u'绑定黄金宝箱'

        # 新增掉落测试
        elif pid == self.PROP_COUPON:
            return u'鸟券'
        elif pid == 220:
            return u'创房卡'
        elif pid == 604:
            return u'青铜宝箱'
        elif pid == 701:
            return u'毒龙蛋'
        elif pid == 702:
            return u'冰龙蛋'
        elif pid == 703:
            return u'火龙蛋'
        elif pid == 704:
            return u'圣龙蛋'

        elif pid == 1220:
            return u'创房卡'
        elif pid == 1604:
            return u'青铜宝箱'
        elif pid == self.LOOK_PROP_ARROW_1:
            return u'绑定毒龙蛋'
        elif pid == self.LOOK_PROP_ARROW_2:
            return u'绑定冰龙蛋'
        elif pid == self.LOOK_PROP_ARROW_3:
            return u'绑定火龙蛋'
        elif pid == self.LOOK_PROP_ARROW_4:
            return u'绑定圣龙蛋'

        # 永久炮台
        elif pid < 20000 * 1000:
            if pid == 20000:
                return u'零式火炮'
            if pid == 20001:
                return u'流沙之鳞'
            if pid == 20002:
                return u'冰翼猎手'
            if pid == 20003:
                return u'翡翠荆棘'
            if pid == 20004:
                return u'狂怒炎龙'
            if pid == 20005:
                return u'死亡之翼'
            if pid == 20006:
                return u'雷鸣宙斯'
            if pid == 20007:
                return u'暗夜魅影'
            if pid == 20008:
                return u'九五至尊'
            if pid == 20010:
                return u'恭贺新春'
            if pid == 20011:
                return u'工地之光'
            if pid == 20012:
                return u'翡翠梦境'
            if pid == 20013:
                return u'逐风者'
            if pid == 20014:
                return u'天炎之怒'
            if pid == 20015:
                return u'蓝魔冰晶'
            if pid == 20016:
                return u'夏日清檬'

        # 限时炮道具
        elif pid >= 20000 * 1000 and pid <= 30000 * 1000:
            props_id = int(pid / 1000)
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
            if props_id == 20011:
                name += u'工地之光'
            if props_id == 20012:
                name += u'翡翠梦境'
            if props_id == 20013:
                name += u'逐风者'
            if props_id == 20014:
                name += u'天炎之怒'
            if props_id == 20015:
                name += u'蓝魔冰晶'
            if props_id == 20016:
                name += u'夏日清檬'
            name = name + u'%d天' % (props_day)
            return name
        elif pid >= 20000 * 10000 and pid <= 30000 * 10000:
            props_id = int(pid / 10000)
            props_day = int(pid % 10000)
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
            if props_id == 20011:
                name += u'工地之光'
            if props_id == 20012:
                name += u'翡翠梦境'
            if props_id == 20013:
                name += u'逐风者'
            if props_id == 20014:
                name += u'天炎之怒'
            if props_id == 20015:
                name += u'蓝魔冰晶'
            if props_id == 20016:
                name += u'夏日清檬'
            name = name + u'%d分钟' % (props_day)
            return name

    def get_reward_str(self, reward):
        if isinstance(reward, list):
            reward = reward[0]
        else:
            reward = reward
        desc = []
        keys = ['diamond', 'power','target','coin','silver_coupon']
        names = [u'钻石', u'鸟蛋', u'靶券', u'金币', u'话费券']
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

    def get_zongzi_name(self,field):
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


props = BirdProps()


@register.filter(name='deal_zongzi_name')
def deal_zongzi_name(result):
    zongzi_list = []
    for field,value in result.items():
        name = props.get_zongzi_name(field)
        zongzi_list.append("{}*{}".format(name,value))
    return u', '.join(zongzi_list)


@register.filter(name='hide_phone')
def hide_phone(phone):
    phone = str(phone)
    if len(phone) == 11:
        show_phone = phone[0:3] + '****' + phone[7:11]
        return show_phone
    else:
        return '0'


@register.filter(name='game_name')
def game_name(g_name):
    games = int(g_name)
    if games == 1:
        return "翻翻乐"
    elif games == 2:
        return "靶场"
    elif games == 3:
        return "大富翁"
    else:
        return "斗地主"


@register.filter(name='vip_name')
def vip_name(vip_list):
    if not isinstance(vip_list,list):
        vip_info = ["vip{}".format(vip) for vip in eval(vip_list)]
    else:
        vip_info = ["vip{}".format(vip) for vip in vip_list]

    vip_str = ','.join(vip_info)
    return vip_str


@register.filter(name='room_name')
def room_name(r_name):
    room = str(r_name)
    if room == "301":
        return "新手海岛"
    elif room == "302":
        return "林海雪原"
    elif room == "303":
        return "极寒冰川"
    elif room == "304":
        return "猎龙峡谷"
    elif room == "305":
        return "绝境炼狱"
    elif room == "306":
        return "极度魔界"
    elif room == "307":
        return "上古战场"
    elif room == "400":
        return "刺激战场-体验"
    elif room == "401":
        return "刺激战场-初"
    elif room == "402":
        return "刺激战场-中"
    elif room == "403":
        return "刺激战场-高"
    else:
        return room



