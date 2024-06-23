#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: TF
# Create: 2019-01-28

class Tips(object):
    @staticmethod
    def get_desc_infos(keyArr, titleArr, channelValue, total_value):
        index = 0
        real_total_pay = 0
        infos = []
        field_list =["in.chip.catch.bird.200","in.chip.catch.bird.201","in.chip.catch.bird.202","in.chip.catch.bird.203", "in.chip.catch.bird.209"]
        exception = ""
        for key in keyArr:
            if key in channelValue:
                infos.append(titleArr[index] + ':' + str(channelValue[key]))
                real_total_pay += int(channelValue[key])
            elif key == 'add_line':
                infos.append('---------------------')
            else:
                exception += key + "\n"
            index += 1

        if total_value != real_total_pay:
            infos.append('数据存在异常，联系技术')
            if len(keyArr[0].split('.')) > 1:
                key_str = "{}.{}".format(keyArr[0].split('.')[0], keyArr[0].split('.')[1])
                retA = [i for i in channelValue if i not in keyArr]
                retB = [n for n in retA if n.startswith('{}'.format(key_str)) and n not in field_list]
                for field in retB:
                    infos.append(field)
                exception_info = exception
        return infos

    @classmethod
    def get_in_chip_info(self,add_line=None):
        keyArr = [
            'in.chip.buy.product',
            'in.chip.cdkey.reward',
            'in.chip.cdkey.reward.free',
            'in.chip.activity.buy.gift_box_1',
            'in.chip.activity.buy.gift_box_2',
            'add_line',
            'in.chip.day.activity.value.receive',
            'in.chip.week.activity.value.receive',
            'in.chip.game.startup',
            'in.chip.online.reward',
            'in.chip.signin.reward',
            'in.chip.unlock.barrel',
            'in.chip.bind.rewards',
            'in.chip.red_packet.reward',
            'in.chip.coupon.exchange',
            'in.chip.exp.upgrade',
            'in.chip.activity.pay.raffle',
            'in.chip.activity.task.reward.receive',
            'in.chip.activity.task.reward.total',
            'in.chip.activity.login.reward',
            'in.chip.vip.activity.reward',
            'in.chip.share.config.welfare',
            'in.chip.welfare.get',
            'in.chip.month.card.reward',
            'in.chip.vip_receive',
            'in.chip.high.rank.get',
            'in.chip.middle.rank.get',
            'in.chip.primary.rank.get',
            'in.chip.boss.rank.get',
            'in.chip.entity.use',
            'in.chip.props.recovery',
            'in.chip.task.get',
            'in.chip.super.weapon.fix.new',
            'in.chip.gm.mail.get',
            'in.chip.benefit.reward',
            'in.chip.match_table.mail.get',
            'in.chip.match_table.return',
            'in.chip.buy.product.recharge_double',
            'in.chip.save.money.activity.reward',
            'in.chip.year_monster_extra',
            'in.chip.pay.rank.get',
            'in.chip.buy.product.recharge_add',
            'in.chip.activity.shake.reward',
            'in.chip.activity.pay.rank.reward',
            'in.chip.game.fanfanle.get',  # 翻翻乐
            'in.chip.activity.smash_egg.reward',
            'in.chip.rich.man.reward',
            'in.chip.activity.rank.get',
            'in.chip.activity.point.exchange',
            'in.chip_pool_new_gift',
            'in.bright_give_info',
            'in.chip.weapon_bright_give',
            'in.chip.min_game_bright_give',
            'in.play_shot_gift_chip',
            'out.gift_chip.hit.bird',
            'in.give_chip.give.kill',
            'info.play_shot_gift_pool',
            'in.chip.activity.total_pay.recv',
            'in.chip.new.month.card102003',
            'in.chip.new.month.card102001',
            'in.chip.new.month.card102002',
            'in.chip.gift.buy.1000020',
            'in.chip.gift.buy.1000019',
            'in.chip.gift.buy.1000018',
            'in.chip.gift.buy.1000017',
            'in.chip.gift.buy.1000016',
            'in.chip.gift.buy.1000015',
            'in.chip.gift.buy.1000014',
            'in.chip.gift.buy.1000013',
            'in.chip.gift.buy.1000012',
            'in.chip.gift.buy.1000011',
            'in.chip.gift.buy.1000010',
            'in.chip.gift.buy.1000009',
            'in.chip.gift.buy.1000008',
            'in.chip.gift.buy.1000007',
            'in.chip.gift.buy.1000006',
            'in.chip.gift.buy.1000005',
            'in.chip.gift.buy.1000004',
            'in.chip.gift.buy.1000003',
            'in.chip.gift.buy.1000002',
            'in.chip.gift.buy.1000001',
            'in.chip.gift.buy.1000000',
        ]

        titleArr = [
            '支付购买',
            'CDKey',
            '免费CDKey',
            '活动礼包1产出',
            '活动礼包2产出',
            'add_line',
            '每日任务',
            '每周任务',
            '初次登录500',
            '在线转盘抽奖',
            '每日签到',
            '解锁炮倍',
            '绑定手机奖励',
            '红包奖励',
            '限时商城兑换',
            '升级礼包',
            '活动-充值转盘',
            '活动-击杀鸟',
            '活动-击杀鸟-总',
            '登录活动奖励',
            'vip登录有礼活动奖励',
            '分享福利',
            '被分享福利',
            '月卡',
            'VIP奖励',
            '高级场排行',
            '中级场排行',
            '初级场排行',
            'Boss排行',
            '宝箱',
            '炮台回收',
            '任务（旧）',
            '超级武器奖励',
            'gm邮件赠送',
            '救济金奖励',
            '竞技场奖励',
            '竞技场邮件退还',
            '首冲翻倍活动',
            '存钱窝',
            '金猪',
            '支付排行榜奖励',
            '充值加赠',
            '开心摇摇乐',
            '充值积分周期榜',
            '翻翻乐',
            '欢乐砸金蛋',
            '大富翁奖励',
            '炮王之王奖励',
            '积分商城兑换',
            '新手赠分',
            '明送鸟蛋',
            '超武明送',
            '小游戏明送',
            '千五赠分',
            '105赠分',
            '手工收送分合计',
            '水池填分',
            '累计充值奖励',
            '六元新手礼包',
            '黄金月卡',
            '至尊月卡',
            '88元礼包',
            '6元礼包',
            '超武礼包',
            '赏金礼包',
            '冰冻礼包',
            '狂暴礼包',
            '月度礼包',
            'VIP每周礼包',
            '每周礼包',
            '每日礼包',
            'VIP12专属礼包',
            'VIP11专属礼包',
            'VIP10专属礼包',
            'VIP9专属礼包',
            'VIP8专属礼包',
            'VIP7专属礼包',
            'VIP6专属礼包',
            'VIP5专属礼包',
            'VIP4专属礼包',
            'VIP3专属礼包',
            'VIP2专属礼包',
        ]

        if add_line:
            del keyArr[5]
            del titleArr[5]

        return keyArr,titleArr

    @classmethod
    def get_grail_in_chip(self, channelValue, total_chip):

        keyArr, titleArr = self.get_in_chip_info(True)
        chip_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_chip)
        return chip_infos


    @classmethod
    def get_in_chip_infos(self,channelValue, total_chip, gift_chip, recharge_gift_chip, chip_pool_new_gift,play_gift_chip):
        # in_chip_catch_bird_200 = channelValue.get('in.chip.catch.bird.200', 0)  # 初级房打鸟获得
        # in_chip_catch_bird_201 = channelValue.get('in.chip.catch.bird.201', 0)  # 新手房打鸟获得
        # in_chip_catch_bird_202 = channelValue.get('in.chip.catch.bird.202', 0)  # 中级房打鸟获得
        # in_chip_catch_bird_203 = channelValue.get('in.chip.catch.bird.203', 0)  # 高级房打鸟获得

        keyArr, titleArr = self.get_in_chip_info()
        chip_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_chip)
        chip_infos.append('---------------------')
        chip_infos.append('千N赠分:' + str(play_gift_chip))
        chip_infos.append('105赠分:' + str(gift_chip))
        chip_infos.append('充值赠分:' + str(recharge_gift_chip))
        chip_infos.append('新手阶段赠分:' + str(chip_pool_new_gift))

        pay_send_double = int(channelValue.get(keyArr[34], 0))

        return chip_infos, pay_send_double

    @classmethod
    def get_out_chip_infos(self, channelValue, total_chip):
        keyArr = [
            'out.chip.game.shot.bullet.200',
            'out.chip.game.shot.bullet.201',
            'out.chip.game.shot.bullet.202',
            'out.chip.game.shot.bullet.203',
            'out.chip.game.shot.bullet.209',
            'out.chip.create.vip.table',
            'out.chip.match.table.consume',
            'out.chip.chip.buy.weapon',
        ]

        titleArr = [
            '新手场打鸟',
            '初级场打鸟',
            '中级场打鸟',
            '高级场打鸟',
            'VIP场打鸟',
            '创建VIP房',
            '竞技场报名',
            '购买武器',
        ]
        out_chip_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_chip)
        return out_chip_infos

    @classmethod
    def get_in_coupon_infos(self,channelValue, total_coupon):
        keyArr = [
            'in.coupon.coupon_pool.hit.bird',
            'in.coupon.drop_coupon_np',
            'in.coupon.exp.upgrade',
            'in.coupon.target.room.get',
            'in.coupon.gm.reward',
            'in.coupon.limit.shop.buy',
            'in.coupon.goods.shop.buy',
            'in.coupon.coupon_pool.coupon.bird.fall',
            'in.coupon.online.reward',
            'in.coupon.game.fanfanle.get',
            'in.coupon.cdkey.reward',
            'in.coupon.rich.man.reward',
            'in.coupon.activity.smash_egg.reward',
        ]

        titleArr = [
            '打鸟掉落',
            '新玩家赠送',
            '玩家首次登陆赠送',
            '靶场产出',
            'GM赠送',
            '限时商城退款',
            '实物商城退款',
            '鸟券怪掉落',
            '在线奖励',
            '翻翻乐',
            '兑换码奖励',
            '大富翁奖励',
            '欢乐砸金蛋',
        ]

        in_coupon_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_coupon)
        real_hit_out = int(channelValue.get(keyArr[0], 0)) + int(channelValue.get(keyArr[7], 0))
        return in_coupon_infos, real_hit_out


    @classmethod
    def get_out_coupon_infos(self, channelValue, total_coupon):
        keyArr = [
            'out.coupon.limit.shop.buy',
            'out.coupon.goods.shop.buy',
        ]

        titleArr = [
            '限时商城购买',
            '实物商城购买',
        ]
        out_coupon_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_coupon)
        return out_coupon_infos

    @classmethod
    def get_o_coupon_x(self,in_chip_rmb, today_chip, out_coupon):
        infos = []

        # infos.append('出卷率：产出鸟券 /（充值钱数+商城兑换+免费送的-当天鸟蛋-亮亮')
        # infos.append(str(out_coupon) + ' / (' + str(pay_total) + '+' + str(exchange) + '+' + str(free) + '-' + str(today_chip) + ')')
        if out_coupon == 0:
            infos.append('出券率:0')
        else:
            all_in_chip = float(in_chip_rmb - today_chip)
            if all_in_chip <= 0:
                infos.append('出券率:0')
            else:
                infos.append('出券率:{}'.format(out_coupon / (all_in_chip)))

        return infos

    @classmethod
    def get_out_target_infos(self, channelValue, total_target):
        keyArr = [
            'out.target_coupon.target.room.consume',
        ]

        titleArr = [
            '靶场小游戏',
        ]

        out_target_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_target)
        return out_target_infos


    @classmethod
    def get_in_target_infos(self, channelValue, total_target):
        keyArr = [
            'in.target_coupon.target.bird.fall',
            'in.target_coupon.coupon.exchange',
            'in.target_coupon.bird.fall',
        ]

        titleArr = [
            '打靶场怪掉落',
            '限时商城',
            '打鸟掉落（旧）',
        ]

        in_target_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_target)
        hit_fall_count = int(channelValue.get('in.target_coupon.target.bird.fall', 0)) + int(channelValue.get('in.target_coupon.bird.fall', 0))
        return in_target_infos, hit_fall_count

    @classmethod
    def get_out_diamond_infos(self,channelValue, total_diamond):
        keyArr = [
            'out.diamond.game.fanfanle.change',
            'out.diamond.game.fanfanle.play',
            'out.diamond.table.buy.202',
            'out.diamond.table.buy.203',
            'out.diamond.table.buy.204',
            'out.diamond.table.buy.205',
            'out.diamond.inner.buy.202',
            'out.diamond.inner.buy.203',
            'out.diamond.inner.buy.204',
            'out.diamond.inner.buy.205',
            'out.diamond.unlock.barrel',
            'out.diamond.props.shop.buy30000',
            'out.diamond.props.shop.buy30001',
            'out.diamond.props.shop.buy30002',
            'out.diamond.props.shop.buy30003',
            'out.diamond.diamond.buy.weapon',
            'out.diamond.changenick.consume',
            'out.diamond.rich.man.consume',
            'out.diamond.smart_game_10000',
            'out.diamond.new.month.card.buy102001',
            'out.diamond.new.month.card.buy102002',
        ]

        titleArr = [
            '翻翻乐-换牌',
            '翻翻乐-门票',
            '冰冻-战斗中',
            '狂暴-战斗中',
            '超级武器-战斗中',
            '召唤金鸟-战斗中',
            '冰冻-商城',
            '狂暴-商城',
            '超级武器-商城',
            '召唤金鸟-商城',
            '升级炮台',
            '道具商城购买-冰冻',
            '道具商城购买-狂暴无双',
            '道具商城购买-超级武器',
            '道具商城购买-赏金传送',
            '购买炮台',
            '改昵称',
            '大富翁',
            '斗地主',
            '黄金月卡',
            '至尊月卡',
        ]

        out_diamond_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_diamond)
        return out_diamond_infos

    @classmethod
    def get_in_diamond_infos(self,channelValue, total_diamond):
        keyArr = [
            'in.diamond.buy.product',
            'in.diamond.cdkey.reward',
            'in.diamond.cdkey.reward.free',
            'in.diamond.activity.buy.gift_box_1',
            'in.diamond.activity.buy.gift_box_2',
            'in.diamond.bind.rewards',
            'in.diamond.buy.product.extra',
            'in.diamond.coupon.exchange',
            'in.diamond.exp.upgrade',
            'in.diamond.game.fanfanle.get',
            'in.diamond.month.card.reward',
            'in.diamond.online.reward',
            'in.diamond.signin.reward',
            'in.diamond.vip_receive',
            'in.diamond.day.activity.value.receive',
            'in.diamond.week.activity.value.receive',
            'in.diamond.unlock.barrel',
            'in.diamond.welfare.get',
            'in.diamond.share.config.welfare',
            'in.diamond.activity.pay.raffle',
            'in.diamond.bird.fall.200',
            'in.diamond.bird.fall.201',
            'in.diamond.bird.fall.202',
            'in.diamond.bird.fall.203',
            'in.diamond.boss.rank.get',
            'in.diamond.buy.product.recharge_add',
            'in.diamond.activity.pay.rank.reward',
            'in.diamond.activity.task.reward.receive',
            'in.diamond.activity.smash_egg.reward',
            'in.diamond.activity.rank.get',
            'in.diamond.activity.point.exchange',
            'in.diamond.primary.rank.get',
            'in.diamond.middle.rank.get',
            'in.diamond.high.rank.get',
            'in.diamond.pay.rank.get',
            'in.diamond.gift.buy.1000019',
            'in.diamond.gift.buy.1000010',
            'in.diamond.gift.buy.1000009',
            'in.diamond.gift.buy.1000008',
            'in.diamond.gift.buy.1000007',
            'in.diamond.gift.buy.1000006',
            'in.diamond.smart_game_10000',
        ]

        titleArr = [
            '支付购买',
            'CDKey',
            '免费cdkey',
            '活动礼包1产出',
            '活动礼包2产出',
            '绑定手机',
            '购买商品额外赠送',
            '限时商城兑换',
            '升级赠送',
            '翻翻乐',
            '月卡',
            '在线奖励',
            '签到',
            'VIP奖励',
            '每日任务获得',
            '每周任务获得',
            '解锁炮倍',
            '福利',
            '分享',
            '充值抽奖活动',
            '打鸟掉落-初级（旧）',
            '打鸟掉落-新手（旧）',
            '打鸟掉落-中级（旧）',
            '打鸟掉落-高级（旧）',
            'Boss排行（旧）',
            '充值加赠',
            '充值积分周期榜',
            '任务活动奖励(活动-击杀鸟)',
            '欢乐砸金蛋',
            '炮王之王奖励',
            '积分商城兑换',
            '初级排行榜奖励',
            '中级排行榜奖励',
            '高级排行榜奖励',
            '充值排行榜奖励',
            '6元礼包',
            'VIP12专属礼包',
            'VIP11专属礼包',
            'VIP10专属礼包',
            'VIP9专属礼包',
            'VIP8专属礼包',
            '斗地主',
        ]

        in_diamond_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_diamond)
        return in_diamond_infos

    @classmethod
    def get_in_weapon_infos(self, channelValue, total_weapon):
        keyArr = [
            'in.props.204.vip_receive',
            'in.props.204.online.reward',
            'in.props.204.activity.smash_egg.reward',
            'in.props.204.activity.pay.raffle',
            'in.props.204.activity.point.exchange',
            'in.props.204.diamond.exchange',
            'in.props.204.inner.buy',
            'in.props.204.rich.man.reward',
            'in.props.204.coupon.exchange',
        ]

        titleArr = [
            'vip升级奖励',
            '在线转盘奖励',
            '砸金蛋奖励',
            '充值抽奖活动',
            '积分商城兑换',
            '限时商城-道具兑换',
            '超级武器-商城',
            '大富翁奖励',
            '鸟券兑换-商城',
        ]

        in_weapon_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_weapon)
        return in_weapon_infos

    @classmethod
    def get_pay_infos(self,channelValue, total_pay):
        keyArr = [
            'weixin_pay_total',
            'ali_pay_total',
            'cdkey_pay_total',
            'sdk_pay_total',
            'gm_pay_total',
        ]

        titleArr = [
            '微信',
            '支付宝',
            'cdkey',
            'sdk支付',
            'gm支付',
        ]

        pay_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_pay)
        return pay_infos

    @classmethod
    def get_presented_infos(self, channelValue, total_coupon, ignore_warn=False):
        """洗码量"""
        keyArr = [
            'in.chip.catch.bird.200',
            'in.chip.catch.bird.201',
            'in.chip.catch.bird.202',
            'in.chip.catch.bird.203',
            'in.chip.catch.bird.209',
            'out.chip.game.shot.bullet.200',
            'out.chip.game.shot.bullet.201',
            'out.chip.game.shot.bullet.202',
            'out.chip.game.shot.bullet.203',
            'out.chip.game.shot.bullet.209',
        ]

        titleArr = [
            '新手场打鸟产出(包含超级武器)',
            '初级场打鸟产出(包含超级武器)',
            '中级场打鸟产出(包含超级武器)',
            '高级场打鸟产出(包含超级武器)',
            'vip房打鸟产出(包含超级武器)',
            '新手场打鸟消耗',
            '初级场打鸟消耗',
            '中级场打鸟消耗',
            '高级场打鸟消耗',
            'vip房打鸟消耗',
        ]

        presented_infos = self.get_desc_infos(keyArr, titleArr, channelValue, total_coupon)
        return presented_infos

    @classmethod
    def get_play_gift_chip_info(self, channelValue, total_gift_chip, ignore_warn=False):
        """千N赠分"""
        keyArr = [
            'in.play_shot_gift_chip.5',
            'in.play_shot_gift_chip.10',
            'in.play_shot_gift_chip.20',
            'in.play_shot_gift_chip.30',
            'in.play_shot_gift_chip.40',
            'in.play_shot_gift_chip.50',
            'in.play_shot_gift_chip.60',
            'in.play_shot_gift_chip.70',
            'in.play_shot_gift_chip.80',
            'in.play_shot_gift_chip.90',
            'in.play_shot_gift_chip.100',
            'in.play_shot_gift_chip.150',
            'in.play_shot_gift_chip.200',
            'in.play_shot_gift_chip.250',
            'in.play_shot_gift_chip.300',
            'in.play_shot_gift_chip.350',
            'in.play_shot_gift_chip.400',
            'in.play_shot_gift_chip.450',
            'in.play_shot_gift_chip.500',
            'in.play_shot_gift_chip.600',
            'in.play_shot_gift_chip.700',
            'in.play_shot_gift_chip.800',
            'in.play_shot_gift_chip.900',
            'in.play_shot_gift_chip.1000',
            'in.play_shot_gift_chip.1500',
            'in.play_shot_gift_chip.2000',
            'in.play_shot_gift_chip.2500',
            'in.play_shot_gift_chip.3000',
            'in.play_shot_gift_chip.3500',
            'in.play_shot_gift_chip.4000',
            'in.play_shot_gift_chip.4500',
            'in.play_shot_gift_chip.5000',
        ]

        titleArr = [
            '千N赠分5倍',
            '千N赠分10倍',
            '千N赠分20倍',
            '千N赠分30倍',
            '千N赠分40倍',
            '千N赠分50倍',
            '千N赠分60倍',
            '千N赠分70倍',
            '千N赠分80倍',
            '千N赠分90倍',
            '千N赠分100倍',
            '千N赠分150倍',
            '千N赠分200倍',
            '千N赠分250倍',
            '千N赠分300倍',
            '千N赠分350倍',
            '千N赠分400倍',
            '千N赠分450倍',
            '千N赠分500倍',
            '千N赠分600倍',
            '千N赠分700倍',
            '千N赠分800倍',
            '千N赠分900倍',
            '千N赠分1000倍',
            '千N赠分1500倍',
            '千N赠分2000倍',
            '千N赠分2500倍',
            '千N赠分3000倍',
            '千N赠分3500倍',
            '千N赠分4000倍',
            '千N赠分4500倍',
            '千N赠分5000倍',
        ]

        play_gift_chip = self.get_desc_infos(keyArr, titleArr, channelValue, total_gift_chip)
        return play_gift_chip


    @staticmethod
    def get_deal_popup(keyList, titleList, popup_info, total_info):
        show_list, index, show_info, exception = [], 0, 0, ""
        field_list = ["in.coin.catch.bird.301", "in.coin.catch.bird.302", "in.coin.catch.bird.303", "in.coin.catch.bird.304", "in.coin.catch.bird.305"
                      "in.coin.catch.bird.306", "in.power.catch.bird.401", "in.power.catch.bird.402", "in.power.catch.bird.403"]

        for key in keyList:
            if key in popup_info:
                show_list.append(titleList[index] + ':' + str(popup_info[key]))
                show_info += int(popup_info[key])
            elif key == "add_line":
                show_list.append('---------------------')
            else:
                exception += key + "\n"
            index += 1

        if show_info != total_info:
            show_list.append('数据存在异常，联系技术')
            if len(keyList[0].split('.')) > 1:
                key_str = "{}.{}".format(keyList[0].split('.')[0], keyList[0].split('.')[1])
                retA = [i for i in popup_info if i not in keyList]
                retB = [n for n in retA if n.startswith('{}'.format(key_str)) and n not in field_list]
                for field in retB:
                    show_list.append(field)
        return show_list

    @classmethod
    def get_in_coin_popup(cls, popup_info, total_info, add_line=None):
        keyList = [
            'in.coin.buy.product',
            'in.coin.cdkey.reward',
            'in.coin.cdkey.reward.free',
            'in.coin.new.login.reward',
            # 'add_line',
            'in.coin.unlock.relax_barrel',
            'in.coin.up.barrel.strange',
            'in.coin.use_props_arrow',
            'in.coin.new.month.card102001',
            'in.coin.new.month.card102002',
            'in.coin.day.task.get',
            'in.coin.week.task.get',
            'in.coin.room.task.get',
            'in.coin.new.sign.in',
            'in.coin.new_player_rechange_buy',
            'in.coin.new.player.rechange.return',
            'in.coin.vip.supply',
            'in.coin.benefit.reward',
            'in.coin.zero_yuan_gift.buy',
            'in.coin.day.activity.value.receive',
            'in.coin.week.activity.value.receive',
            'in.coin.new_player.task.get',
            'in.coin.exp.upgrade',
            'in.coin.gift.buy.1000009',
            'in.coin.gift.buy.1000002',
            'in.coin.gift.buy.1000001',
            'in.coin.first_gift_buy',
            'in.coin.vip_receive',
            'in.coin.activity.total_pay.recv',
            'in.coin.bind.rewards',
            'in.coin.new.month.card',
            'in.coin.props.use',
            'in.coin.coupon.exchange',
            'in.coin.gm.mail.get',
            'in.coin.gift.buy.1000027',
            'in.coin.gift.buy.1000026',
            'in.coin.gift.buy.1000025',
            'in.coin.gift.buy.1000014',
            'in.coin.gift.buy.1000013',
            'in.coin.gift.buy.1000012',
            'in.coin.gift.buy.1000011',
            'in.coin.gift.buy.1000010',
            'in.coin.gift.buy.1000009',
            'in.coin.gift.buy.1000008',
            'in.coin.gift.buy.1000007',
            'in.coin.gift.buy.1000004',
            'in.coin.gift.buy.1000003',

            'in.coin.bonus_pool_raffle.301',
            'in.coin.bonus_pool_raffle.302',
            'in.coin.bonus_pool_raffle.303',
            'in.coin.bonus_pool_raffle.304',
            'in.coin.bonus_pool_raffle.305',
            'in.coin.bonus_pool_raffle.306',
            'in.coin.rich.man.reward',
            'in.coin.super_boss_raffle.451',
        ]

        titleList = [
            '支付购买',
            'CDKey',
            '免费CDKey',
            '新手7日登陆',
            # 'add_line',
            '炮倍升级赠送',
            '炮倍强化',
            '消耗龙蛋',
            '购买月卡一周尝鲜',
            '购买尊贵月卡',
            '每日任务',
            '每周任务',
            '房间任务',
            '30日签到',
            '50元白送购买',
            '50元白送返还',
            'vip补给',
            '救济金',
            '0元礼包',
            '日常活跃',
            '周常活跃',
            '新手成长任务奖励',
            '升级赠送',
            '礼包商城:炮倍直升',
            '礼包商城:6元礼包',
            '礼包商城:3元礼包',
            '首充购买',
            'VIP奖励',
            '累计充值返奖',
            '绑定手机',
            '月卡邮件奖励',
            '开福袋',
            '兑换商城:兑换',
            '后台邮件赠送',
            '礼包商城:金鼠炮台',
            '礼包商城:每日超值',
            '礼包商城:春暖花开',
            '礼包商城:圣龙礼包',
            '礼包商城:土豪专属',
            '礼包商城:超级划算',
            '礼包商城:金币礼包(大)',
            '礼包商城:98元礼包',
            '礼包商城:68元礼包',
            '礼包商城:30元礼包',
            '礼包商城:6元礼包',
            '礼包商城:炮倍直升',
            '礼包商城:金币礼包(小)',

            '奖金鸟抽奖:新手海岛',
            '奖金鸟抽奖:林海雪原',
            '奖金鸟抽奖:极寒冰川',
            '奖金鸟抽奖:猎龙峡谷',
            '奖金鸟抽奖:绝境炼狱',
            '奖金鸟抽奖:极度魔界',
            '大富翁奖励',
            '风元素领主抽奖',
        ]

        if add_line:
            del keyList[5]
            del titleList[5]

        in_diamond_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_diamond_show

    @classmethod
    def get_in_diamond_popup(cls, popup_info, total_info):
        keyList = [
            'in.diamond.buy.product',
            'in.diamond.cdkey.reward',
            'in.diamond.cdkey.reward.free',
            'in.diamond.activity.buy.gift_box_1',
            'in.diamond.activity.buy.gift_box_2',
            'in.diamond.bind.rewards',
            'in.diamond.buy.product.extra',
            'in.diamond.coupon.exchange',
            'in.diamond.exp.upgrade',
            'in.diamond.game.fanfanle.get',
            'in.diamond.new.month.card102001',
            'in.diamond.new.month.card102002',
            'in.diamond.new.login.reward',
            'in.diamond.new.sign.in',
            'in.diamond.vip_receive',
            'in.diamond.day.task.get',
            'in.diamond.week.task.get',
            'in.diamond.unlock.barrel',
            'in.diamond.welfare.get',
            'in.diamond.share.config.welfare',
            'in.diamond.activity.pay.raffle',
            'in.diamond.boss.rank.get',
            'in.diamond.buy.product.recharge_add',
            'in.diamond.activity.pay.rank.reward',
            'in.diamond.activity.task.reward.receive',
            'in.diamond.activity.smash_egg.reward',
            'in.diamond.activity.rank.get',
            'in.diamond.activity.point.exchange',
            'in.diamond.zero_yuan_gift.buy',
            'in.diamond.new_player_rechange_buy',
            'in.diamond.catch.bird.304',
            'in.diamond.catch.bird.305',
            'in.diamond.catch.bird.306',
            'in.diamond.catch.bird.400',
            'in.diamond.catch.bird.401',
            'in.diamond.activity.total_pay.recv',
            'in.diamond.gift.buy.1000016',
            'in.diamond.gift.buy.1000014',
            'in.diamond.gift.buy.1000009',
            'in.diamond.gift.buy.1000008',
            'in.diamond.gift.buy.1000007',
            'in.diamond.gift.buy.1000003',
            'in.diamond.gift.buy.1000002',
            'in.diamond.gift.buy.1000001',
            'in.diamond.first_gift_buy',
            'in.diamond.new_player.task.get',
            'in.diamond.new_grow_active_recv',
            'in.diamond.gm.mail.get',
            'in.diamond.room.task.get',
            'in.diamond.activity.login.raffle1',
            'in.diamond.new.month.card',
        ]

        titleList = [
            '支付购买',
            'CDKey',
            '免费cdkey',
            '活动礼包1产出',
            '活动礼包2产出',
            '绑定手机',
            '购买商品额外赠送',
            '限时商城兑换',
            '等级升级赠送',
            '翻翻乐',
            '月卡一周尝鲜',
            '尊贵月卡',
            '7日签到奖励',
            '每日签到奖励',
            'VIP奖励',
            '每日任务获得',
            '每周任务获得',
            '解锁炮倍',
            '输入ID领取福利',
            '邀请好友奖励',
            '充值抽奖活动',
            'Boss排行（旧）',
            '充值加赠',
            '充值积分周期榜',
            '任务活动奖励(活动-击杀鸟)',
            '欢乐砸金蛋',
            '炮王之王奖励',
            '积分商城兑换',
            '0元礼包',
            '50元白送',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '刺激战场-初级:打鸟掉落',
            '刺激战场-中级:打鸟掉落',
            '累计充值返奖',
            '礼包商城:每日98元',
            '礼包商城:每日6元',
            '礼包商城:炮倍直升',
            '礼包商城:四色宝石(中)',
            '礼包商城:四色宝石(小)',
            '礼包商城:新手畅玩',
            '礼包商城:6元礼包',
            '礼包商城:3元礼包',
            '首充购买',
            '新手成长任务奖励',
            '新手成长任务积分奖励',
            '后台邮件赠送',
            '战斗中任务奖励',
            '登陆奖励活动',
            '购买月卡',
        ]

        in_diamond_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_diamond_show

    @classmethod
    def get_out_diamond_popup(cls, popup_info, total_info):
        keyList = [
            'out.diamond.table.301.buy.201',
            'out.diamond.table.301.buy.202',
            'out.diamond.table.301.buy.203',
            'out.diamond.table.301.buy.205',

            'out.diamond.table.302.buy.201',
            'out.diamond.table.302.buy.202',
            'out.diamond.table.302.buy.203',
            'out.diamond.table.302.buy.205',

            'out.diamond.table.303.buy.201',
            'out.diamond.table.303.buy.202',
            'out.diamond.table.303.buy.203',
            'out.diamond.table.303.buy.205',

            'out.diamond.table.304.buy.201',
            'out.diamond.table.304.buy.202',
            'out.diamond.table.304.buy.203',
            'out.diamond.table.304.buy.205',

            'out.diamond.table.305.buy.201',
            'out.diamond.table.305.buy.202',
            'out.diamond.table.305.buy.203',
            'out.diamond.table.305.buy.205',

            'out.diamond.table.306.buy.201',
            'out.diamond.table.306.buy.202',
            'out.diamond.table.306.buy.203',
            'out.diamond.table.306.buy.205',

            'out.diamond.table.401.buy.201',
            'out.diamond.table.401.buy.202',
            'out.diamond.table.401.buy.203',
            'out.diamond.table.401.buy.205',

            'out.diamond.table.402.buy.201',
            'out.diamond.table.402.buy.202',
            'out.diamond.table.402.buy.203',
            'out.diamond.table.402.buy.205',

            'out.diamond.table.403.buy.201',
            'out.diamond.table.403.buy.202',
            'out.diamond.table.403.buy.203',
            'out.diamond.table.403.buy.205',

            'out.diamond.props.shop.buy30000',
            'out.diamond.props.shop.buy30001',
            'out.diamond.props.shop.buy30002',
            'out.diamond.props.shop.buy30003',
            'out.diamond.props.shop.buy30004',
            'out.diamond.props.shop.buy30005',
            'out.diamond.props.shop.buy30006',
            'out.diamond.props.shop.buy30007',
            'out.diamond.props.shop.buy30008',
            'out.diamond.props.shop.buy30009',
            'out.diamond.props.shop.buy30010',
            'out.diamond.props.shop.buy30011',
            'out.diamond.props.shop.buy30012',
            'out.diamond.props.shop.buy30013',
            'out.diamond.props.shop.buy30014',
            'out.diamond.props.shop.buy30015',
            'out.diamond.props.shop.buy30016',
            'out.diamond.props.shop.buy30017',
            'out.diamond.unlock.relax_barrel',

            'out.diamond.changenick.consume',
            'out.diamond.trade_union.up_level',
            'out.diamond.up.relax_barrel',
            'out.diamond.rich.man.consume',
        ]

        titleList = [
            '新手海岛:购买锁定',
            '新手海岛:购买冰冻',
            '新手海岛:购买狂暴',
            '新手海岛:购买传送门',
            '林海雪原:购买锁定',
            '林海雪原:购买冰冻',
            '林海雪原:购买狂暴',
            '林海雪原:购买传送门',
            '极寒冰川:购买锁定',
            '极寒冰川:购买冰冻',
            '极寒冰川:购买狂暴',
            '极寒冰川:购买传送门',
            '猎龙峡谷:购买锁定',
            '猎龙峡谷:购买冰冻',
            '猎龙峡谷:购买狂暴',
            '猎龙峡谷:购买传送门',
            '绝境炼狱:购买锁定',
            '绝境炼狱:购买冰冻',
            '绝境炼狱:购买狂暴',
            '绝境炼狱:购买传送门',
            '极度魔界:购买锁定',
            '极度魔界:购买冰冻',
            '极度魔界:购买狂暴',
            '极度魔界:购买传送门',

            '初级场:购买锁定',
            '初级场:购买冰冻',
            '初级场:购买狂暴',
            '初级场:购买传送门',

            '中级场:购买锁定',
            '中级场:购买冰冻',
            '中级场:购买狂暴',
            '中级场:购买传送门',

            '高级场:购买锁定',
            '高级场:购买冰冻',
            '高级场:购买狂暴',
            '高级场:购买传送门',

            '道具商城购买x50锁定',
            '道具商城购买x20冰冻',
            '道具商城购买x10狂暴无双',
            '道具商城购买x50赏金传送',
            '道具商城购买x1毒龙蛋',
            '道具商城购买x1冰龙蛋',
            '道具商城购买x1火龙蛋',
            '道具商城购买x1圣磷蛋',
            '道具商城购买x10强化石',
            '道具商城购买x10绿宝石',
            '道具商城购买x10蓝宝石',
            '道具商城购买x10紫宝石',
            '道具商城购买x10橙宝石',
            '道具商城购买x10灵魂宝石',
            '道具商城购买x100锁定',
            '道具商城购买x100冰冻',
            '道具商城购买x100狂暴无双',
            '道具商城购买x100赏金传送',
            '炮倍升级赠送',

            '改名消耗',
            '工会升级',
            '解锁金币场炮倍',
            '大富翁活动',

        ]

        out_diamond_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_diamond_show

    @classmethod
    def get_in_silver_coupon_popup(cls, popup_info, total_info):
        keyList = [
            'in.silver_coupon.catch.bird.301',
            'in.silver_coupon.catch.bird.302',
            'in.silver_coupon.catch.bird.303',
            'in.silver_coupon.catch.bird.304',
            'in.silver_coupon.catch.bird.305',
            'in.silver_coupon.catch.bird.306',
            'in.silver_coupon.catch.bird.307',
            'in.silver_coupon.catch.bird.400',
            'in.silver_coupon.catch.bird.401',
            'in.silver_coupon.exp.upgrade',
            'in.silver_coupon.gm.reward',
            "in.silver_coupon.new.login.reward",
            "in.silver_coupon.room.task.get",
            "in.silver_coupon.new.sign.in",
            "in.silver_coupon.power.daily.rank.reward",
            "in.silver_coupon.power.week.rank.reward",
            "in.silver_coupon.open_box.601",
            "in.silver_coupon.open_box.602",
            "in.silver_coupon.open_box.603",
            "in.silver_coupon.bonus_pool_raffle.301",
            "in.silver_coupon.bonus_pool_raffle.302",
            "in.silver_coupon.bonus_pool_raffle.303",
            "in.silver_coupon.bonus_pool_raffle.304",
            "in.silver_coupon.bonus_pool_raffle.305",
            "in.silver_coupon.bonus_pool_raffle.306",
            "in.silver_coupon.bonus_pool_raffle.400",
            "in.silver_coupon.bonus_pool_raffle.401",
            "in.silver_coupon.bonus_pool_raffle.402",
            "in.silver_coupon.bonus_pool_raffle.403",
            "in.silver_coupon.rich.man.reward",
            "in.silver_coupon.props.use",
            "in.silver_coupon.super_boss_raffle.451",
            "in.silver_coupon.activity.pay.rank.reward",
            "in.silver_coupon.week.task.get",
            "in.silver_coupon.day.task.get",
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '上古战场:打鸟掉落',
            '刺激战场-体验场:靶场怪掉落',
            '刺激战场-初级场:靶场怪掉落',
            '等级升级赠送',
            'GM赠送',
            '签到奖励',
            '战斗中任务奖励',
            '30日签到',
            '捕鸟争霸赛日排行榜',
            '捕鸟争霸赛周排行榜',
            '开蓝色宝箱',
            '开紫色宝箱',
            '开钻石宝箱',
            '新手海岛:奖金鸟抽奖',
            '林海雪原:奖金鸟抽奖',
            '极寒冰川:奖金鸟抽奖',
            '猎龙峡谷:奖金鸟抽奖',
            '绝境炼狱:奖金鸟抽奖',
            '极度魔界:奖金鸟抽奖',
            '刺激战场-体验场:奖金鸟抽奖',
            '刺激战场-初级:奖金鸟抽奖',
            '刺激战场-中级:奖金鸟抽奖',
            '刺激战场-高级:奖金鸟抽奖',

            '大富翁奖励',
            '活动礼盒',
            '风元素领主抽奖',
            '活动积分排行榜奖励',
            '每日任务奖励',
            '每周任务奖励',
        ]

        in_silver_coupon_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_silver_coupon_show

    @classmethod
    def get_out_silver_coupon_popup(cls, popup_info, total_info):
        keyList = [
            'out.silver_coupon.limit.shop.buy',
        ]

        titleList = [
            '限时商城兑换',
        ]

        in_silver_coupon_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_silver_coupon_show

    @classmethod
    def get_in_props_201_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.201.catch.bird.301',
            'in.props.201.catch.bird.302',
            'in.props.201.catch.bird.303',
            'in.props.201.catch.bird.304',
            'in.props.201.catch.bird.305',
            'in.props.201.catch.bird.306',
            'in.props.201.day.task.get',
            'in.props.201.exp.upgrade',
            'in.props.201.new.month.card102001',
            'in.props.201.new.month.card102002',
            'in.props.201.new_player_rechange_buy',
            'in.props.201.unlock.relax_barrel',
            'in.props.201.zero_yuan_gift.buy',
            'in.props.201.new.login.reward',
            'in.props.201.room.task.get',
            'in.props.201.first_gift_buy',
            'in.props.201.week.task.get',
            'in.props.201.vip_receive',

            'in.props.1201.catch.bird.301',
            'in.props.1201.catch.bird.302',
            'in.props.1201.catch.bird.303',
            'in.props.1201.catch.bird.304',
            'in.props.1201.catch.bird.305',
            'in.props.1201.catch.bird.306',
            'in.props.1201.day.task.get',
            'in.props.1201.exp.upgrade',
            'in.props.1201.new.month.card102001',
            'in.props.1201.new.month.card102002',
            'in.props.1201.new_player_rechange_buy',
            'in.props.1201.unlock.relax_barrel',
            'in.props.1201.zero_yuan_gift.buy',
            'in.props.1201.new.login.reward',
            'in.props.1201.room.task.get',
            'in.props.1201.first_gift_buy',
            'in.props.1201.week.task.get',
            'in.props.1201.vip_receive',

            'in.props.1201.new.sign.in',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务赠送',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            '白送50元奖励',
            '解锁炮倍奖励',
            '0元礼包奖励',
            '7天签到赠送',
            '战斗中任务',
            '首充购买',
            'vip奖励',
            '周常任务',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务赠送',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            '白送50元奖励',
            '解锁炮倍奖励',
            '0元礼包奖励',
            '7天签到赠送',
            '战斗中任务',
            '首充购买',
            'vip奖励',
            '周常任务',
            '30日签到',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_201_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.201.game.use.301',
            'out.props.201.game.use.302',
            'out.props.201.game.use.303',
            'out.props.201.game.use.304',
            'out.props.201.game.use.305',
            'out.props.201.game.use.306',
            'out.props.201.game.use.307',

            'out.props.201.game.use.401',
            'out.props.201.game.use.402',
            'out.props.201.game.use.403',

            'out.props.1201.game.use.301',
            'out.props.1201.game.use.302',
            'out.props.1201.game.use.303',
            'out.props.1201.game.use.304',
            'out.props.1201.game.use.305',
            'out.props.1201.game.use.306',
            'out.props.1201.game.use.307',

            'out.props.1201.game.use.401',
            'out.props.1201.game.use.402',
            'out.props.1201.game.use.403',
        ]

        titleList = [
            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '上古战场:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',

            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '上古战场:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_202_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.202.catch.bird.301',
            'in.props.202.catch.bird.302',
            'in.props.202.catch.bird.303',
            'in.props.202.catch.bird.304',
            'in.props.202.catch.bird.305',
            'in.props.202.catch.bird.306',
            'in.props.202.day.task.get',
            'in.props.202.exp.upgrade',
            'in.props.202.new.month.card102001',
            'in.props.202.new.month.card102002',
            'in.props.202.vip_receive',
            'in.props.202.unlock.relax_barrel',
            'in.props.202.new.login.reward',
            'in.props.202.room.task.get',
            'in.props.202.week.task.get',
            'in.props.202.zero_yuan_gift.buy',
            'in.props.202.first_gift_buy',
            'in.props.202.gift.buy.1000009',
            'in.props.202.gift.buy.1000002',

            'in.props.1202.catch.bird.301',
            'in.props.1202.catch.bird.302',
            'in.props.1202.catch.bird.303',
            'in.props.1202.catch.bird.304',
            'in.props.1202.catch.bird.305',
            'in.props.1202.catch.bird.306',
            'in.props.1202.day.task.get',
            'in.props.1202.exp.upgrade',
            'in.props.1202.new.month.card102001',
            'in.props.1202.new.month.card102002',
            'in.props.1202.vip_receive',
            'in.props.1202.unlock.relax_barrel',
            'in.props.1202.new.login.reward',
            'in.props.1202.room.task.get',
            'in.props.1202.week.task.get',
            'in.props.1202.zero_yuan_gift.buy',
            'in.props.1202.first_gift_buy',
            'in.props.1202.gift.buy.1000009',
            'in.props.1202.gift.buy.1000002',

            'in.props.1202.rich.man.reward',
            'in.props.1202.super_boss_raffle.451',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            'vip奖励',
            '解锁炮倍',
            '7天签到赠送',
            '战斗中任务',
            '周任务',
            '0元礼包',
            '首充购买',
            '礼包商城:炮倍直升',
            '礼包商城:6元礼包',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            'vip奖励',
            '解锁炮倍',
            '7天签到赠送',
            '战斗中任务',
            '周任务',
            '0元礼包',
            '首充购买',
            '礼包商城:炮倍直升',
            '礼包商城:6元礼包',

            '大富翁奖励',
            '风元素领主抽奖',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_202_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.202.game.use.301',
            'out.props.202.game.use.302',
            'out.props.202.game.use.303',
            'out.props.202.game.use.304',
            'out.props.202.game.use.305',
            'out.props.202.game.use.306',
            'out.props.202.game.use.401',
            'out.props.202.game.use.402',
            'out.props.202.game.use.403',

            'out.props.1202.game.use.301',
            'out.props.1202.game.use.302',
            'out.props.1202.game.use.303',
            'out.props.1202.game.use.304',
            'out.props.1202.game.use.305',
            'out.props.1202.game.use.306',
            'out.props.1202.game.use.401',
            'out.props.1202.game.use.402',
            'out.props.1202.game.use.403',
        ]

        titleList = [
            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',

            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_203_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.203.catch.bird.301',
            'in.props.203.catch.bird.302',
            'in.props.203.catch.bird.303',
            'in.props.203.catch.bird.304',
            'in.props.203.catch.bird.305',
            'in.props.203.catch.bird.306',
            'in.props.203.day.task.get',
            'in.props.203.exp.upgrade',
            'in.props.203.new.month.card102001',
            'in.props.203.new.month.card102002',
            'in.props.203.vip_receive',
            'in.props.203.unlock.relax_barrel',
            'in.props.203.new.login.reward',
            'in.props.203.room.task.get',
            'in.props.203.week.task.get',
            'in.props.203.zero_yuan_gift.buy',

            'in.props.1203.catch.bird.301',
            'in.props.1203.catch.bird.302',
            'in.props.1203.catch.bird.303',
            'in.props.1203.catch.bird.304',
            'in.props.1203.catch.bird.305',
            'in.props.1203.catch.bird.306',
            'in.props.1203.day.task.get',
            'in.props.1203.exp.upgrade',
            'in.props.1203.new.month.card102001',
            'in.props.1203.new.month.card102002',
            'in.props.1203.vip_receive',
            'in.props.1203.unlock.relax_barrel',
            'in.props.1203.new.login.reward',
            'in.props.1203.room.task.get',
            'in.props.1203.week.task.get',
            'in.props.1203.zero_yuan_gift.buy',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            'vip奖励',
            '解锁炮倍',
            '7天签到赠送',
            '战斗中任务',
            '周任务',
            '0元礼包',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            'vip奖励',
            '解锁炮倍',
            '7天签到赠送',
            '战斗中任务',
            '周任务',
            '0元礼包',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_203_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.203.game.use.301',
            'out.props.203.game.use.302',
            'out.props.203.game.use.303',
            'out.props.203.game.use.304',
            'out.props.203.game.use.305',
            'out.props.203.game.use.306',
            'out.props.203.game.use.401',
            'out.props.203.game.use.402',
            'out.props.203.game.use.403',

            'out.props.1203.game.use.301',
            'out.props.1203.game.use.302',
            'out.props.1203.game.use.303',
            'out.props.1203.game.use.304',
            'out.props.1203.game.use.305',
            'out.props.1203.game.use.306',
            'out.props.1203.game.use.401',
            'out.props.1203.game.use.402',
            'out.props.1203.game.use.403',
        ]

        titleList = [
            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',

            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_205_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.205.catch.bird.301',
            'in.props.205.catch.bird.302',
            'in.props.205.catch.bird.303',
            'in.props.205.catch.bird.304',
            'in.props.205.catch.bird.305',
            'in.props.205.catch.bird.306',
            'in.props.205.day.task.get',
            'in.props.205.exp.upgrade',
            'in.props.205.new.month.card102001',
            'in.props.205.new.month.card102002',
            'in.props.205.vip_receive',
            'in.props.205.unlock.relax_barrel',
            'in.props.205.new.login.reward',
            'in.props.205.room.task.get',
            'in.props.205.week.task.get',
            'in.props.205.zero_yuan_gift.buy',
            'in.props.205.new.sign.in',
            'in.props.205.first_gift_buy',
            'in.props.205.activity.total_pay.recv',

            'in.props.1205.catch.bird.301',
            'in.props.1205.catch.bird.302',
            'in.props.1205.catch.bird.303',
            'in.props.1205.catch.bird.304',
            'in.props.1205.catch.bird.305',
            'in.props.1205.catch.bird.306',
            'in.props.1205.day.task.get',
            'in.props.1205.exp.upgrade',
            'in.props.1205.new.month.card102001',
            'in.props.1205.new.month.card102002',
            'in.props.1205.vip_receive',
            'in.props.1205.unlock.relax_barrel',
            'in.props.1205.new.login.reward',
            'in.props.1205.room.task.get',
            'in.props.1205.week.task.get',
            'in.props.1205.zero_yuan_gift.buy',
            'in.props.1205.new.sign.in',
            'in.props.1205.first_gift_buy',
            'in.props.1205.activity.total_pay.recv',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            'vip奖励',
            '解锁炮倍',
            '7天签到赠送',
            '战斗中任务',
            '周任务',
            '0元礼包',
            '30日签到',
            '首充购买',
            '累计充值返奖',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '每日任务',
            '等级升级赠送',
            '周卡赠送',
            '月卡赠送',
            'vip奖励',
            '解锁炮倍',
            '7天签到赠送',
            '战斗中任务',
            '周任务',
            '0元礼包',
            '30日签到',
            '首充购买',
            '累计充值返奖',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_205_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.205.game.use.301',
            'out.props.205.game.use.302',
            'out.props.205.game.use.303',
            'out.props.205.game.use.304',
            'out.props.205.game.use.305',
            'out.props.205.game.use.306',
            'out.props.205.game.use.401',
            'out.props.205.game.use.402',
            'out.props.205.game.use.403',

            'out.props.1205.game.use.301',
            'out.props.1205.game.use.302',
            'out.props.1205.game.use.303',
            'out.props.1205.game.use.304',
            'out.props.1205.game.use.305',
            'out.props.1205.game.use.306',
            'out.props.1205.game.use.401',
            'out.props.1205.game.use.402',
            'out.props.1205.game.use.403',
        ]

        titleList = [
            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',

            '新手海岛:战斗消耗',
            '林海雪原:战斗消耗',
            '极寒冰川:战斗消耗',
            '猎龙峡谷:战斗消耗',
            '绝境炼狱:战斗消耗',
            '极度魔界:战斗消耗',
            '初级场:战斗消耗',
            '中级场:战斗消耗',
            '高级场:战斗消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_215_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.215.catch.bird.301',
            'in.props.215.catch.bird.302',
            'in.props.215.catch.bird.303',
            'in.props.215.catch.bird.304',
            'in.props.215.catch.bird.305',
            'in.props.215.catch.bird.306',
            'in.props.215.new.month.card102001',
            'in.props.215.new.month.card102002',
            'in.props.215.new.sign.in',

            'in.props.1215.catch.bird.301',
            'in.props.1215.catch.bird.302',
            'in.props.1215.catch.bird.303',
            'in.props.1215.catch.bird.304',
            'in.props.1215.catch.bird.305',
            'in.props.1215.catch.bird.306',
            'in.props.1215.new.month.card102001',
            'in.props.1215.new.month.card102002',
            'in.props.1215.new.sign.in',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '30日签到',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '30日签到',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_215_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.215.game.use.301',
            'out.props.1215.on_up_barrel',
        ]

        titleList = [
            '新手海岛:战斗中使用',
            '强化炮倍:消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_216_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.216.catch.bird.301',
            'in.props.216.catch.bird.302',
            'in.props.216.catch.bird.303',
            'in.props.216.catch.bird.304',
            'in.props.216.catch.bird.305',
            'in.props.216.catch.bird.306',
            'in.props.216.new.month.card102001',
            'in.props.216.new.month.card102002',
            'in.props.216.day.task.get',
            'in.props.216.week.task.get',
            'in.props.216.new.sign.in',

            'in.props.1216.catch.bird.301',
            'in.props.1216.catch.bird.302',
            'in.props.1216.catch.bird.303',
            'in.props.1216.catch.bird.304',
            'in.props.1216.catch.bird.305',
            'in.props.1216.catch.bird.306',
            'in.props.1216.new.month.card102001',
            'in.props.1216.new.month.card102002',
            'in.props.1216.day.task.get',
            'in.props.1216.week.task.get',
            'in.props.1216.new.sign.in',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '日任务奖励',
            '周任务奖励',
            '30日签到',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '日任务奖励',
            '周任务奖励',
            '30日签到',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_216_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.216.game.use.301',
            'out.props.1216.on_up_barrel',
        ]

        titleList = [
            '新手海岛:战斗中使用',
            '强化炮倍:消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_217_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.217.catch.bird.301',
            'in.props.217.catch.bird.302',
            'in.props.217.catch.bird.303',
            'in.props.217.catch.bird.304',
            'in.props.217.catch.bird.305',
            'in.props.217.catch.bird.306',
            'in.props.217.new.month.card102001',
            'in.props.217.new.month.card102002',
            'in.props.217.day.task.get',
            'in.props.217.week.task.get',
            'in.props.217.zero_yuan_gift.buy',

            'in.props.1217.catch.bird.301',
            'in.props.1217.catch.bird.302',
            'in.props.1217.catch.bird.303',
            'in.props.1217.catch.bird.304',
            'in.props.1217.catch.bird.305',
            'in.props.1217.catch.bird.306',
            'in.props.1217.new.month.card102001',
            'in.props.1217.new.month.card102002',
            'in.props.1217.day.task.get',
            'in.props.1217.week.task.get',
            'in.props.1217.zero_yuan_gift.buy',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '日任务奖励',
            '周任务奖励',
            '0元礼包',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '日任务奖励',
            '周任务奖励',
            '0元礼包',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_217_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.217.game.use.301',
            'out.props.1217.on_up_barrel',
        ]

        titleList = [
            '新手海岛:战斗中使用',
            '强化炮倍:消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_218_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.218.catch.bird.301',
            'in.props.218.catch.bird.302',
            'in.props.218.catch.bird.303',
            'in.props.218.catch.bird.304',
            'in.props.218.catch.bird.305',
            'in.props.218.catch.bird.306',
            'in.props.218.new.month.card102001',
            'in.props.218.new.month.card102002',
            'in.props.218.day.task.get',
            'in.props.218.week.task.get',
            'in.props.218.zero_yuan_gift.buy',

            'in.props.1218.catch.bird.301',
            'in.props.1218.catch.bird.302',
            'in.props.1218.catch.bird.303',
            'in.props.1218.catch.bird.304',
            'in.props.1218.catch.bird.305',
            'in.props.1218.catch.bird.306',
            'in.props.1218.new.month.card102001',
            'in.props.1218.new.month.card102002',
            'in.props.1218.day.task.get',
            'in.props.1218.week.task.get',
            'in.props.1218.zero_yuan_gift.buy',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '日任务奖励',
            '周任务奖励',
            '0元礼包',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '月卡一周尝鲜',
            '尊贵月卡',
            '日任务奖励',
            '周任务奖励',
            '0元礼包',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_218_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.218.game.use.301',
            'out.props.1218.on_up_barrel',
        ]

        titleList = [
            '新手海岛:战斗中使用',
            '强化炮倍:消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_219_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.219.catch.bird.301',

        ]

        titleList = [
            '新手海岛:打鸟掉落',

        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_219_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.219.game.use.301',
            'out.props.1219.on_up_barrel',
        ]

        titleList = [
            '新手海岛:战斗中使用',
            '强化炮倍:消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_301_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.301.catch.bird.301',

        ]

        titleList = [
            '新手海岛:打鸟掉落',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_301_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.301.game.use.301',
            'out.props.1301.on_up_barrel',
        ]

        titleList = [
            '新手海岛:战斗中使用',
            '强化炮倍:消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_1327_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1327.activity.total_pay.recv',
            'in.props.1327.gift.buy.1000030',
            'in.props.1327.gm.mail.get',
        ]

        titleList = [
            '累计充值赠送捕鸟宝箱',
            '礼包商城购买捕鸟宝箱',
            'gm赠送捕鸟宝箱',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_1321_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1321.gm.mail.get',
            'in.props.1321.buy.product',
            'in.props.1322.buy.product',
            'in.props.1323.buy.product',
            'in.props.1323.zongzi_present',
            'in.props.1323.lucky_bag_present',
        ]

        titleList = [
            'gm赠送',
            '购买商品',
            '购买商品',
            '购买商品',
            '龙舟赛排名奖励',
            '活动登录赠送',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_1305_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1305.gm.mail.get',
            'in.props.1305.buy.product',
            'in.props.1305.activity.total_pay.recv',
        ]

        titleList = [
            'gm赠送',
            '购买商品',
            '累计充值赠送',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_1302_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1302.gm.mail.get',
            'in.props.1302.buy.product',
        ]

        titleList = [
            'gm赠送',
            '购买商品',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_601_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.601.limit_shop.exchange',
        ]

        titleList = [
            '限时商城兑换:蓝色宝箱',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_602_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.602.limit_shop.exchange',
        ]

        titleList = [
            '限时商城兑换:紫色色宝箱',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_603_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.603.limit_shop.exchange',
        ]

        titleList = [
            '限时商城兑换:钻石宝箱',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_1612_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1612.buy.product',
            'in.props.1612.gm.mail.get',
        ]

        titleList = [
            '购买商品',
            'gm赠送',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_1705_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1612.buy.product',
        ]

        titleList = [
            'boss掉落',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_1311_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.1311.buy.product',
            'in.props.1311.gm.mail.get',
        ]

        titleList = [
            '购买商品',
            'gm赠送',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_in_props_701_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.701.catch.bird.301',
            'in.props.701.catch.bird.302',
            'in.props.701.catch.bird.303',
            'in.props.701.catch.bird.304',
            'in.props.701.catch.bird.305',
            'in.props.701.catch.bird.306',
            'in.props.701.catch.bird.307',
            'in.props.701.new.login.reward',
            'in.props.701.room.task.get',
            'in.props.701.new_grow_active_recv',
            'in.props.701.new_player.task.get',
            'in.props.701.activity.login.raffle',
            'in.props.701.out.pwd.box',

            'in.props.701.bonus_pool_raffle.301',
            'in.props.701.bonus_pool_raffle.302',
            'in.props.701.bonus_pool_raffle.303',
            'in.props.701.bonus_pool_raffle.304',
            'in.props.701.bonus_pool_raffle.305',
            'in.props.701.bonus_pool_raffle.306',
            'in.props.701.bonus_pool_raffle.307',

            'in.props.1701.catch.bird.301',
            'in.props.1701.catch.bird.302',
            'in.props.1701.catch.bird.303',
            'in.props.1701.catch.bird.304',
            'in.props.1701.catch.bird.305',
            'in.props.1701.catch.bird.306',
            'in.props.1701.catch.bird.307',
            'in.props.1701.new.login.reward',
            'in.props.1701.room.task.get',
            'in.props.1701.new_grow_active_recv',
            'in.props.1701.new_player.task.get',
            'in.props.701.egg_appraise_success',
            'in.props.1701.day.activity.value.receive',
            'in.props.1701.week.activity.value.receive',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            "上古战场:打鸟掉落",
            '7日签到奖励',
            '战斗中任务',
            '新手成长任务积分奖励',
            '新手成长任务奖励',
            '活动登录奖励',
            '保险箱取出',

            '新手海岛:奖金鸟抽奖',
            '林海雪原:奖金鸟抽奖',
            '极寒冰川:奖金鸟抽奖',
            '猎龙峡谷:奖金鸟抽奖',
            '绝境炼狱:奖金鸟抽奖',
            '极度魔界:奖金鸟抽奖',
            '上古战场:奖金鸟抽奖',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            "上古战场:打鸟掉落",
            '新手7日登陆',
            '战斗中任务',
            '新手成长任务积分奖励',
            '新手成长任务奖励',
            '龙蛋孵化',
            '每日任务活跃度奖励',
            '每周任务活跃度奖励',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_701_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.701.game.use.301',
            'out.props.701.game.use.302',
            'out.props.701.game.use.303',
            'out.props.701.game.use.304',
            'out.props.701.game.use.305',
            'out.props.701.game.use.306',
            'out.props.701.game.use.307',
            'out.props.701.in.pwd.box',

            'out.props.1701.game.use.301',
            'out.props.1701.game.use.302',
            'out.props.1701.game.use.303',
            'out.props.1701.game.use.304',
            'out.props.1701.game.use.305',
            'out.props.1701.game.use.306',
            'out.props.1701.game.use.307',
        ]

        titleList = [
            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
            '保险箱存入',

            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_702_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.702.catch.bird.301',
            'in.props.702.catch.bird.302',
            'in.props.702.catch.bird.303',
            'in.props.702.catch.bird.304',
            'in.props.702.catch.bird.305',
            'in.props.702.catch.bird.306',

            'in.props.702.bonus_pool_raffle.301',
            'in.props.702.bonus_pool_raffle.302',
            'in.props.702.bonus_pool_raffle.303',
            'in.props.702.bonus_pool_raffle.304',
            'in.props.702.bonus_pool_raffle.305',
            'in.props.702.bonus_pool_raffle.306',
            'in.props.702.bonus_pool_raffle.307',

            'in.props.702.new_grow_active_recv',
            'in.props.702.new_player.task.get',
            'in.props.702.new.sign.in',
            'in.props.702.new.login.reward',
            'in.props.702.rich.man.reward',
            'in.props.702.props.use',
            'in.props.702.out.pwd.box',
            'in.props.702.limit_shop.exchange',
            'in.props.702.props.use.321',
            'in.props.702.props.use.305',
            'in.props.702.gm.mail.get',
            'in.props.702.props.use.327',

            'in.props.1702.catch.bird.301',
            'in.props.1702.catch.bird.302',
            'in.props.1702.catch.bird.303',
            'in.props.1702.catch.bird.304',
            'in.props.1702.catch.bird.305',
            'in.props.1702.catch.bird.306',
            'in.props.1702.new_grow_active_recv',
            'in.props.1702.new_player.task.get',
            'in.props.1702.new.sign.in',
            'in.props.1702.new.login.reward',

            'in.props.702.props.use.311',
            'in.props.702.props.use.612',
            'in.props.702.props.use.705',
            'in.props.702.egg_appraise_success',
            'in.props.1702.day.activity.value.receive',
            'in.props.1702.week.activity.value.receive',
            'in.props.702.activity.box.use',
            'in.props.702.activity.box.use.331',
            'in.props.702.activity.box.use.332',
            'in.props.702.activity.box.use.333',
            'in.props.702.present.get',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',

            '新手海岛:奖金鸟抽奖',
            '林海雪原:奖金鸟抽奖',
            '极寒冰川:奖金鸟抽奖',
            '猎龙峡谷:奖金鸟抽奖',
            '绝境炼狱:奖金鸟抽奖',
            '极度魔界:奖金鸟抽奖',
            '上古战场:奖金鸟抽奖',

            '新手成长任务积分奖励',
            '新手成长任务奖励',
            '30日签到',
            '7日签到奖励',
            '大富翁奖励',
            '活动礼盒',
            '保险箱取出',
            '限时商城兑换',
            '开粽子',
            '开礼盒',
            'gm赠送',
            '捕鸟宝箱',

            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '新手成长任务积分奖励',
            '新手成长任务奖励',
            '30日签到',
            '7日签到奖励',

            '开神秘礼盒',
            '开超级福袋',
            '领主礼盒',
            '龙蛋孵化',
            '每日任务活跃度奖励',
            '每周任务活跃度奖励',
            '七夕活动宝箱',
            '白银宝箱',
            '黄金宝箱',
            '白金宝箱',
            '赠送道具',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_702_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.702.game.use.301',
            'out.props.702.game.use.302',
            'out.props.702.game.use.303',
            'out.props.702.game.use.304',
            'out.props.702.game.use.305',
            'out.props.702.game.use.306',
            'out.props.702.game.use.307',
            'out.props.702.limit.shop.buy',
            'out.props.702.in.pwd.box',

            'out.props.1702.game.use.301',
            'out.props.1702.game.use.302',
            'out.props.1702.game.use.303',
            'out.props.1702.game.use.304',
            'out.props.1702.game.use.305',
            'out.props.1702.game.use.306',
            'out.props.1702.game.use.307',
            'out.props.1702.limit.shop.buy',
            'out.props.702.present.props.1036376',
            'out.props.702.present.props.1119031',
            'out.props.702.present.props.1090755',
            'out.props.702.present.props.1119032',
            'out.props.702.present.props.1100934',
            'out.props.702.present.props.1104144',
            'out.props.702.present.props.1039636',
            'out.props.702.present.props.1089876',
            'out.props.702.present.props.1119030',
            'out.props.702.present.props.1023209',
            'out.props.702.present.props.1119033',
            'out.props.702.present.props.1119029',
            'out.props.702.present.props.1090603',
            'out.props.702.present.props.1039007',
            'out.props.702.present.props.1119028',
            'out.props.702.present.props.1107595',
            'out.props.702.present.props.1036882',
            'out.props.702.present.props.1003170',

            'out.props.702.present.props.1101392',
            'out.props.702.present.props.1125982',
        ]

        titleList = [
            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
            '限时商城兑换',
            '保险箱存储',

            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
            '限时商城兑换',
            '赠送道具给:1036376',
            '赠送道具给:1119031',
            '赠送道具给:1090755',
            '赠送道具给:1119032',
            '赠送道具给:1100934',
            '赠送道具给:1104144',
            '赠送道具给:1039636',
            '赠送道具给:1089876',
            '赠送道具给:1119030',
            '赠送道具给:1023209',
            '赠送道具给:1119033',
            '赠送道具给:1119029',
            '赠送道具给:1090603',
            '赠送道具给:1039007',
            '赠送道具给:1119028',
            '赠送道具给:1107595',
            '赠送道具给:1036882',
            '赠送道具给:1003170',

            '赠送道具给:1101392',
            '赠送道具给:1125982',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_703_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.703.catch.bird.301',
            'in.props.703.catch.bird.302',
            'in.props.703.catch.bird.303',
            'in.props.703.catch.bird.304',
            'in.props.703.catch.bird.305',
            'in.props.703.catch.bird.306',
            'in.props.703.catch.bird.307',
            'in.props.703.catch.bird.401',
            'in.props.703.out.pwd.box',
            'in.props.703.power.shot.703.exchange',
            'in.props.703.gift.buy.1000014',

            'in.props.703.bonus_pool_raffle.301',
            'in.props.703.bonus_pool_raffle.302',
            'in.props.703.bonus_pool_raffle.303',
            'in.props.703.bonus_pool_raffle.304',
            'in.props.703.bonus_pool_raffle.305',
            'in.props.703.bonus_pool_raffle.306',
            'in.props.703.bonus_pool_raffle.307',

            'in.props.703.bonus_pool_raffle.400',
            'in.props.703.bonus_pool_raffle.401',
            'in.props.703.bonus_pool_raffle.402',
            'in.props.703.bonus_pool_raffle.403',
            'in.props.703.props.use',
            'in.props.703.coupon.exchange',
            'in.props.703.gm.mail.get',
            'in.props.703.open_box.601',
            'in.props.703.open_box.602',
            'in.props.703.open_box.603',
            'in.props.703.limit_shop.exchange',
            'in.props.703.props.use.302',
            'in.props.703.props.use.321',
            'in.props.703.props.use.305',
            'in.props.703.new_grow_active_recv',
            'in.props.703.gift.buy.1000010',

            'in.props.703.super_boss_raffle.451',
            'in.props.703.activity.total_pay.recv',
            'in.props.703.props.use.327',

            'in.props.703.props.use.311',
            'in.props.703.props.use.612',
            'in.props.703.props.use.705',
            'in.props.703.egg_appraise_success',
            'in.props.1703.day.activity.value.receive',
            'in.props.1703.week.activity.value.receive',
            'in.props.703.activity.box.use',
            'in.props.703.activity.box.use.331',
            'in.props.703.activity.box.use.332',
            'in.props.703.activity.box.use.333',
            'in.props.703.present.get',
            'in.props.703.limit.shop.buy.return',
            'in.props.703.catch.bird.231.305',
            'in.props.703.catch.bird.231.306',
            'in.props.703.catch.bird.231.307',
            'in.props.703.catch.bird.232.305',
            'in.props.703.catch.bird.232.306',
            'in.props.703.catch.bird.232.307',

            'in.props.703.catch.bird.231.401',
            'in.props.703.catch.bird.231.402',
            'in.props.703.catch.bird.231.403',
            'in.props.703.catch.bird.232.401',
            'in.props.703.catch.bird.232.402',
            'in.props.703.catch.bird.232.403',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '上古战场:打鸟掉落',
            '刺激战场-初级:风暴狮角召唤',
            '保险箱取出',
            '消耗鸟蛋兑出龙蛋',
            '购买圣龙礼包',
            '新手海岛:奖金鸟抽奖',
            '林海雪原:奖金鸟抽奖',
            '极寒冰川:奖金鸟抽奖',
            '猎龙峡谷:奖金鸟抽奖',
            '绝境炼狱:奖金鸟抽奖',
            '极度魔界:奖金鸟抽奖',
            '上古战场:奖金鸟抽奖',
            '刺激战场-体验场:奖金鸟抽奖',
            '刺激战场-初级:奖金鸟抽奖',
            '刺激战场-中级:奖金鸟抽奖',
            '刺激战场-高级:奖金鸟抽奖',
            '活动礼盒',
            '商城话费券兑换',
            'gm邮件赠送',
            '开蓝色宝箱',
            '开紫色宝箱',
            '开钻石宝箱',
            '限时商城兑换',
            '开福袋',
            '开粽子',
            '开礼盒',
            '新手成长任务积分奖励',
            "礼包商城:98元礼包",
            '风元素领主抽奖',
            '累计充值奖励',
            '捕鸟宝箱',
            '开神秘礼盒',
            '开超级福袋',
            '领主礼盒',
            '龙蛋孵化',
            '每日任务活跃度奖励',
            '每周任务活跃度奖励',
            '七夕活动宝箱',
            '白银宝箱',
            '黄金宝箱',
            '白金宝箱',
            '赠送道具',
            '限时商城兑换失败返还',
            '猎龙峡谷:风暴狮角召唤英勇狮鹫',
            '绝境炼狱:风暴狮角召唤英勇狮鹫',
            '极度魔界:风暴狮角召唤英勇狮鹫',
            '猎龙峡谷:风暴狮角召唤双足飞龙',
            '绝境炼狱:风暴狮角召唤双足飞龙',
            '极度魔界:风暴狮角召唤双足飞龙',
            '刺激战场-初级:风暴狮角召唤英勇狮鹫',
            '刺激战场-中级:风暴狮角召唤英勇狮鹫',
            '刺激战场-高级:风暴狮角召唤英勇狮鹫',
            '刺激战场-初级:风暴狮角召唤双足飞龙',
            '刺激战场-中级:风暴狮角召唤双足飞龙',
            '刺激战场-高级:风暴狮角召唤双足飞龙',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_703_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.703.game.use.301',
            'out.props.703.game.use.302',
            'out.props.703.game.use.303',
            'out.props.703.game.use.304',
            'out.props.703.game.use.305',
            'out.props.703.game.use.306',
            'out.props.703.game.use.307',
            'out.props.703.power.shot.703.exchange',
            'out.props.703.limit.shop.buy',
            'out.props.703.in.pwd.box',

            'out.props.1703.game.use.301',
            'out.props.1703.game.use.302',
            'out.props.1703.game.use.303',
            'out.props.1703.game.use.304',
            'out.props.1703.game.use.305',
            'out.props.1703.game.use.306',
            'out.props.1703.game.use.307',
            'out.props.1703.limit.shop.buy',

            'out.props.703.present.props.1119031',
            'out.props.703.present.props.1090755',
            'out.props.703.present.props.1119032',
            'out.props.703.present.props.1100934',
            'out.props.703.present.props.1104144',
            'out.props.703.present.props.1039636',
            'out.props.703.present.props.1089876',
            'out.props.703.present.props.1119030',
            'out.props.703.present.props.1023209',
            'out.props.703.present.props.1119033',
            'out.props.703.present.props.1119029',
            'out.props.703.present.props.1090603',
            'out.props.703.present.props.1039007',
            'out.props.703.present.props.1119028',
            'out.props.703.present.props.1107595',
            'out.props.703.present.props.1036079',
            'out.props.703.present.props.1036376',
            'out.props.703.present.props.1095042',
            'out.props.703.present.props.1036882',
            'out.props.703.present.props.1077513',
            'out.props.703.present.props.1010246',
            'out.props.703.present.props.1046700',
            'out.props.703.present.props.1117015',
            'out.props.703.present.props.1066551',
            'out.props.703.present.props.1041935',
            'out.props.703.present.props.1130195',
            'out.props.703.present.props.1071610',
            'out.props.703.present.props.1084967',
            'out.props.703.present.props.1036134',
            'out.props.703.present.props.1021893',
        ]

        titleList = [
            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
            '消耗龙蛋兑入鸟蛋',
            '兑换商城购买',
            '保险箱存储',

            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
            '兑换商城购买',
            '赠送道具给:1119031',
            '赠送道具给:1090755',
            '赠送道具给:1119032',
            '赠送道具给:1100934',
            '赠送道具给:1104144',
            '赠送道具给:1039636',
            '赠送道具给:1089876',
            '赠送道具给:1119030',
            '赠送道具给:1023209',
            '赠送道具给:1119033',
            '赠送道具给:1119029',
            '赠送道具给:1090603',
            '赠送道具给:1039007',
            '赠送道具给:1119028',
            '赠送道具给:1107595',
            '赠送道具给:1036079',
            '赠送道具给:1036376',
            '赠送道具给:1095042',
            '赠送道具给:1036882',
            '赠送道具给:1077513',
            '赠送道具给:1010246',
            '赠送道具给:1046700',
            '赠送道具给:1117015',
            '赠送道具给:1066551',
            '赠送道具给:1041935',
            '赠送道具给:1130195',
            '赠送道具给:1071610',
            '赠送道具给:1084967',
            '赠送道具给:1036134',
            '赠送道具给:1021893',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_in_props_704_popup(cls, popup_info, total_info):
        keyList = [
            'in.props.704.catch.bird.301',
            'in.props.704.catch.bird.302',
            'in.props.704.catch.bird.303',
            'in.props.704.catch.bird.304',
            'in.props.704.catch.bird.305',
            'in.props.704.catch.bird.306',
            'in.props.704.power.shot.704.exchange',
            'in.props.704.catch.bird.307',
            'in.props.704.out.pwd.box',
            'in.props.704.gift.buy.1000014',
            'in.props.704.gift.buy.1000006',
            'in.props.704.gm.mail.get',
            'in.props.704.coupon.exchange',
            'in.props.704.open_box.601',
            'in.props.704.open_box.602',
            'in.props.704.open_box.603',
            'in.props.704.limit_shop.exchange',

            'in.props.704.bonus_pool_raffle.400',
            'in.props.704.bonus_pool_raffle.401',
            'in.props.704.bonus_pool_raffle.402',
            'in.props.704.bonus_pool_raffle.403',
            'in.props.704.props.use',
            'in.props.704.activity.total_pay.recv',
            'in.props.704.props.use.302',
            'in.props.704.props.use.321',
            'in.props.704.props.use.305',
            'in.props.704.props.use.327',
            'in.props.704.props.use.311',
            'in.props.704.props.use.612',
            'in.props.704.props.use.705',
            'in.props.704.egg_appraise_success',
            'in.props.1704.day.activity.value.receive',
            'in.props.1704.week.activity.value.receive',
            'in.props.704.activity.box.use',
            'in.props.704.activity.box.use.331',
            'in.props.704.activity.box.use.332',
            'in.props.704.activity.box.use.333',
            'in.props.704.present.get',
            'in.props.704.limit.shop.buy.return',

            'in.props.704.catch.bird.231.305',
            'in.props.704.catch.bird.231.306',
            'in.props.704.catch.bird.231.307',
            'in.props.704.catch.bird.232.305',
            'in.props.704.catch.bird.232.306',
            'in.props.704.catch.bird.232.307',
            'in.props.704.catch.bird.231.401',
            'in.props.704.catch.bird.231.402',
            'in.props.704.catch.bird.231.403',
            'in.props.704.catch.bird.232.401',
            'in.props.704.catch.bird.232.402',
            'in.props.704.catch.bird.232.403',
        ]

        titleList = [
            '新手海岛:打鸟掉落',
            '林海雪原:打鸟掉落',
            '极寒冰川:打鸟掉落',
            '猎龙峡谷:打鸟掉落',
            '绝境炼狱:打鸟掉落',
            '极度魔界:打鸟掉落',
            '消耗鸟蛋兑出龙蛋',
            '上古战场:打鸟掉落',
            '保险箱取出',
            '购买圣龙礼包',
            '购买直升战场',
            'gm邮件赠送',
            '商城话费券兑换',
            '开蓝色宝箱',
            '开紫色宝箱',
            '开钻石宝箱',
            '限时商城兑换',
            '刺激战场-体验场:奖金鸟抽奖',
            '刺激战场-初级:奖金鸟抽奖',
            '刺激战场-中级:奖金鸟抽奖',
            '刺激战场-高级:奖金鸟抽奖',
            '活动礼盒',
            '累计充值活动',
            '开福袋',
            '开粽子',
            '开礼盒',
            '捕鸟宝箱',
            '开神秘礼盒',
            '开超级福袋',
            '领主礼盒',
            '龙蛋孵化',
            '每日任务活跃度奖励',
            '每周任务活跃度奖励',
            '七夕活动宝箱',
            '白银宝箱',
            '黄金宝箱',
            '白金宝箱',
            '赠送道具',
            '限时商城兑换失败返还',
            '猎龙峡谷:风暴狮角召唤英勇狮鹫',
            '绝境炼狱:风暴狮角召唤英勇狮鹫',
            '极度魔界:风暴狮角召唤英勇狮鹫',
            '猎龙峡谷:风暴狮角召唤双足飞龙',
            '绝境炼狱:风暴狮角召唤双足飞龙',
            '极度魔界:风暴狮角召唤双足飞龙',
            '刺激战场-初级:风暴狮角召唤英勇狮鹫',
            '刺激战场-中级:风暴狮角召唤英勇狮鹫',
            '刺激战场-高级:风暴狮角召唤英勇狮鹫',
            '刺激战场-初级:风暴狮角召唤双足飞龙',
            '刺激战场-中级:风暴狮角召唤双足飞龙',
            '刺激战场-高级:风暴狮角召唤双足飞龙',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_props_704_popup(cls, popup_info, total_info):
        keyList = [
            'out.props.704.game.use.301',
            'out.props.704.game.use.302',
            'out.props.704.game.use.303',
            'out.props.704.game.use.304',
            'out.props.704.game.use.305',
            'out.props.704.game.use.306',
            'out.props.704.game.use.307',
            'out.props.704.in.pwd.box',
            'out.props.704.power.shot.704.exchange',
            'out.props.704.limit.shop.buy',

            'out.props.1704.game.use.301',
            'out.props.1704.game.use.302',
            'out.props.1704.game.use.303',
            'out.props.1704.game.use.304',
            'out.props.1704.game.use.305',
            'out.props.1704.game.use.306',
            'out.props.1704.game.use.307',

            'out.props.704.present.props.1119031',
            'out.props.704.present.props.1090755',
            'out.props.704.present.props.1119032',
            'out.props.704.present.props.1100934',
            'out.props.704.present.props.1104144',
            'out.props.704.present.props.1039636',
            'out.props.704.present.props.1089876',
            'out.props.704.present.props.1119030',
            'out.props.704.present.props.1023209',
            'out.props.704.present.props.1119033',
            'out.props.704.present.props.1119029',
            'out.props.704.present.props.1090603',
            'out.props.704.present.props.1039007',
            'out.props.704.present.props.1119028',
            'out.props.704.present.props.1107595',
            'out.props.704.present.props.1036079',
            'out.props.704.present.props.1095042',
            'out.props.704.present.props.1093179',
            'out.props.704.present.props.1077840',
            'out.props.704.present.props.1066551',
            'out.props.704.present.props.1077513',
            'out.props.704.present.props.1104822',
            'out.props.704.present.props.1041935',
            'out.props.704.present.props.1036077',
            'out.props.704.present.props.1021893',
            'out.props.704.present.props.1046700',
            'out.props.704.present.props.1118071',
            'out.props.704.present.props.1128015',
            'out.props.704.present.props.1125982',
            'out.props.704.present.props.1100931',
            'out.props.704.present.props.1041938',

            'out.props.704.present.props.1036134',
            'out.props.704.present.props.1130195',
            'out.props.704.present.props.1036882',
            'out.props.704.present.props.1044215',
            'out.props.704.present.props.1109742',
            'out.props.704.present.props.1036376',
            'out.props.704.present.props.1128663',
            'out.props.704.present.props.1130407',
        ]

        titleList = [
            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',
            '保险箱存储',
            '消耗龙蛋兑换鸟蛋',
            '兑换商城购买',

            '新手海岛:战斗中消耗',
            '林海雪原:战斗中消耗',
            '极寒冰川:战斗中消耗',
            '猎龙峡谷:战斗中消耗',
            '绝境炼狱:战斗中消耗',
            '极度魔界:战斗中消耗',
            '上古战场:战斗中消耗',

            '赠送道具给:1119031',
            '赠送道具给:1090755',
            '赠送道具给:1119032',
            '赠送道具给:1100934',
            '赠送道具给:1104144',
            '赠送道具给:1039636',
            '赠送道具给:1089876',
            '赠送道具给:1119030',
            '赠送道具给:1023209',
            '赠送道具给:1119033',
            '赠送道具给:1119029',
            '赠送道具给:1090603',
            '赠送道具给:1039007',
            '赠送道具给:1119028',
            '赠送道具给:1107595',
            '赠送道具给:1036079',
            '赠送道具给:1095042',
            '赠送道具给:1093179',
            '赠送道具给:1077840',
            '赠送道具给:1066551',
            '赠送道具给:1077513',
            '赠送道具给:1104822',
            '赠送道具给:1041935',
            '赠送道具给:1036077',
            '赠送道具给:1021893',
            '赠送道具给:1046700',
            '赠送道具给:1118071',
            '赠送道具给:1128015',
            '赠送道具给:1125982',
            '赠送道具给:1100931',
            '赠送道具给:1041938',

            '赠送道具给:1036134',
            '赠送道具给:1130195',
            '赠送道具给:1036882',
            '赠送道具给:1044215',
            '赠送道具给:1109742',
            '赠送道具给:1036376',
            '赠送道具给:1128663',
            '赠送道具给:1130407',
        ]

        out_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return out_props_show

    @classmethod
    def get_surplus_props_popup(cls, popup_info, total_info):
        keyList = [
            'fix_own_props_215',
            'fix_own_props_216',
            'fix_own_props_217',
            'fix_own_props_218',
            'fix_own_props_219',
            'fix_own_props_301',
            'fix_own_props_701',
            'fix_own_props_702',
            'fix_own_props_703',
            'fix_own_props_704',
        ]

        titleList = [
            '剩余绿宝石',
            '剩余蓝宝石',
            '剩余紫宝石',
            '剩余橙宝石',
            '剩余强化石',
            '剩余灵魂宝石',
            '剩余毒龙蛋',
            '剩余冰龙蛋',
            '剩余火龙蛋',
            '剩余圣龙蛋',
        ]

        surplus_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return surplus_props_show

    @classmethod
    def get_pay_popup(cls, popup_info, total_info):
        keyList = [
            'weixin_pay_total',
            'ali_pay_total',
            'cdkey_pay_total',
            'sdk_pay_total',
            'gm_pay_total',
        ]

        titleList = [
            '微信',
            '支付宝',
            'cdkey',
            'sdk支付',
            'gm支付',
        ]

        in_pay_show = cls.get_desc_infos(keyList, titleList, popup_info, total_info)
        return in_pay_show

    @classmethod
    def get_in_power_popup(cls, popup_info, total_info):
        keyList = [
            'in.power.first_enter_room_400',
            'in.power.first_enter_room_401',
            'in.power.first_enter_room_402',
            'in.power.first_enter_room_403',
            'in.power.bonus_pool_raffle.400',
            'in.power.bonus_pool_raffle.401',
            'in.power.bonus_pool_raffle.402',
            'in.power.bonus_pool_raffle.403',
            'in.power.activity.total_pay.recv',
            'in.power.up.barrel.strange',
        ]

        titleList = [
            '刺激战场-体验场:初次进入房间赠送',
            '刺激战场-初级:初次进入房间赠送',
            '刺激战场-中级:初次进入房间赠送',
            '刺激战场-高级:初次进入房间赠送',
            '刺激战场-体验场:奖金鸟抽奖',
            '刺激战场-初级:奖金鸟抽奖',
            '刺激战场-中级:奖金鸟抽奖',
            '刺激战场-高级:奖金鸟抽奖',
            '累计充值返奖',
            '炮倍强化',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show

    @classmethod
    def get_out_power_popup(cls, popup_info, total_info):
        keyList = [
            'out.power.game.shot.bullet.400',
            'out.power.game.shot.bullet.401',
            'out.power.game.shot.bullet.402',
            'out.power.game.shot.bullet.403',
        ]

        titleList = [
            '刺激战场-体验场:打鸟消耗',
            '刺激战场-初级:打鸟消耗',
            '刺激战场-中级:打鸟消耗',
            '刺激战场-高级:打鸟消耗',
        ]

        in_props_show = cls.get_deal_popup(keyList, titleList, popup_info, total_info)
        return in_props_show