#!/usr/bin/env python
# -*- coding=utf-8 -*-
from util.Tips_show import Tips


class Player(object):

    @classmethod
    def deal_user_info(cls, player_info):
        relax_multiple, power_multiple = player_info.get("relax_multiple", 0), player_info.get("power_multiple", 0)
        channel_id, all_pay_total = player_info["channel"], int(player_info["pay_total"])
        cdkey, weixin, ali, sdk, gm = player_info["user_cdkey_pay"], player_info["user_weixin_pay"],player_info["user_ali_pay"],player_info["user_sdk_pay"], player_info.get("user_gm_pay",0)
        user_info = {"uid": player_info["uid"], "day_time": player_info["day_time"], "channel": channel_id, "pay_total":all_pay_total, "first_pay_time": player_info["first_pay_time"],
                       "total_play_time": player_info["total_play_time"],"relax_multiple": relax_multiple, "power_multiple": power_multiple}
        day_pay_total, surplus_diamond, day_exchange_in, day_exchange_out = 0, 0, 0, 0
        in_silver_coupon, out_silver_coupon, surplus_props_egg, in_props_701, in_props_702, in_props_703, in_props_704 = 0, 0, 0, 0, 0, 0, 0
        out_props_701, out_props_702, out_props_703, out_props_704, in_free_coin, in_pay_coin, in_free_diamond, in_pay_diamond = 0, 0, 0, 0, 0, 0, 0, 0
        out_diamond, in_props_219, out_props_219, in_props_301, out_props_301, in_props_215, out_props_215, in_props_216, out_props_216 = 0, 0, 0, 0, 0, 0, 0, 0, 0
        in_props_217, out_props_217, in_props_218, out_props_218, in_props_201, out_props_201, in_props_202, out_props_202 = 0, 0, 0, 0, 0, 0, 0, 0
        in_props_203, out_props_203, in_props_205, out_props_205, day_in_power = 0, 0, 0, 0, 0

        in_silver_coupon_pop, out_silver_coupon_pop, in_props_701_pop, in_props_702_pop, in_props_703_pop, in_props_704_pop = {}, {}, {}, {}, {}, {}
        out_props_701_pop, out_props_702_pop, out_props_703_pop, out_props_704_pop, in_free_coin_pop, in_pay_coin_pop, in_free_diamond_pop, in_pay_diamond_pop = {}, {}, {}, {}, {}, {}, {}, {}
        out_diamond_pop, in_props_219_pop, out_props_219_pop, in_props_301_pop, out_props_301_pop, in_props_215_pop, out_props_215_pop, in_props_216_pop, out_props_216_pop = {}, {}, {}, {}, {}, {}, {}, {}, {}
        in_props_217_pop, out_props_217_pop, in_props_218_pop, out_props_218_pop, in_props_201_pop, out_props_201_pop, in_props_202_pop, out_props_202_pop = {}, {}, {}, {}, {}, {}, {}, {}
        in_props_203_pop, out_props_203_pop, in_props_205_pop, out_props_205_pop, day_in_power_pop, all_pay_count = {}, {}, {}, {}, {}, {}
        all_pay_count.update({"cdkey_pay_total": cdkey, "weixin_pay_total": weixin, "ali_pay_total": ali, "gm_pay_total": gm, "sdk_pay_total": sdk})
        for key, value in player_info.items():
            # 当日充值
            if key.endswith('.pay.user.pay_total'):
                day_pay_total = int(value)
            # 话费券产出
            if key.startswith('in.silver_coupon.'):
                in_silver_coupon_pop[key] = int(in_silver_coupon_pop.get(key, 0)) + int(value)
                in_silver_coupon += int(value)

            # 话费券消耗
            if key.startswith('out.silver_coupon.'):
                out_silver_coupon_pop[key] = int(out_silver_coupon_pop.get(key, 0)) + int(value)
                out_silver_coupon += int(value)

            # 金币场产出金币
            if key.startswith('in.coin.') and not key.startswith('in.coin.catch.bird.'):
                if key.startswith('in.coin.new.login.reward') or key.startswith('in.coin.unlock.relax_barrel') or key.startswith('in.coin.new.sign.in') or key.startswith('in.coin.zero_yuan_gift.buy') \
                        or key.startswith('in.coin.new_player.task.get') or key.startswith('in.coin.use_props_arrow') or key.startswith('in.coin.day.task.get') or key.startswith(
                    'in.coin.week.task.get') or key.startswith('in.coin.exp.upgrade') or key.startswith(
                    'in.coin.benefit.reward') or key.startswith('in.coin.new_grow_active_recv') or key.startswith('in.coin.day.activity.value.receive') \
                        or key.startswith('in.coin.week.activity.value.receive') or key.startswith('in.coin.gm.mail.get'):

                    in_free_coin_pop[key] = int(in_free_coin_pop.get(key, 0)) + int(value)
                    # 免费金币产出
                    in_free_coin += int(value)
                else:
                    # 付费金币产出
                    in_pay_coin_pop[key] = int(in_pay_coin_pop.get(key, 0)) + int(value)
                    in_pay_coin += int(value)

            # 免费钻石产出
            if key.startswith('in.diamond.'):
                if key.startswith('in.diamond.new.login.reward') or key.startswith(
                        'in.diamond.exp.upgrade') or key.startswith('in.diamond.new.sign.in') or key.startswith(
                        'in.diamond.zero_yuan_gift.buy') \
                        or key.startswith('in.diamond.new_player.task.get') or key.startswith(
                    'in.diamond.day.task.get') or key.startswith('in.diamond.week.task.get') or key.startswith(
                    'in.diamond.unlock.relax_barrel') \
                        or key.startswith('in.diamond.new_grow_active_recv') or key.startswith(
                    'in.diamond.day.activity.value.receive') or key.startswith('in.diamond.week.activity.value.receive') \
                        or key.startswith('in.diamond.gm.mail.get'):

                    in_free_diamond_pop[key] = int(in_free_diamond_pop.get(key, 0)) + int(value)
                    in_free_diamond += int(value)
                else:
                    # 付费钻石产出
                    in_pay_diamond_pop[key] = int(in_pay_diamond_pop.get(key, 0)) + int(value)
                    in_pay_diamond += int(value)

            # 消耗钻石
            if key.startswith('out.diamond.'):
                out_diamond_pop[key] = int(out_diamond_pop.get(key, 0)) + int(value)
                out_diamond += int(value)

            # 金币场-龙蛋产出
            if key.startswith('in.props.701.') or key.startswith('in.props.1701.'):
                in_props_701_pop[key] = int(in_props_701_pop.get(key, 0)) + int(value)
                in_props_701 += int(value)
            if key.startswith('in.props.702.') or key.startswith('in.props.1702.'):
                in_props_702_pop[key] = int(in_props_702_pop.get(key, 0)) + int(value)
                in_props_702 += int(value)
            if key.startswith('in.props.703.') or key.startswith('in.props.1703.'):
                in_props_703_pop[key] = int(in_props_703_pop.get(key, 0)) + int(value)
                in_props_703 += int(value)
            if key.startswith('in.props.704.') or key.startswith('in.props.1704.'):
                in_props_704_pop[key] = int(in_props_704_pop.get(key, 0)) + int(value)
                in_props_704 += int(value)

            # 产出强化石
            if key.startswith('in.props.219.') or key.startswith('in.props.1219.'):
                in_props_219_pop[key] = int(in_props_219_pop.get(key, 0)) + int(value)
                in_props_219 += int(value)

            # 消耗强化石
            if key.startswith('in.props.219.') or key.startswith('in.props.1219.'):
                out_props_219_pop[key] = int(out_props_219_pop.get(key, 0)) + int(value)
                out_props_219 += int(value)

            # 兑入鸟蛋
            if key.startswith('in.power.power.shot.703.exchange') or key.startswith('in.power.power.shot.704.exchange') or \
                    key.startswith('in.power.power.shot.1703.exchange') or key.startswith('in.power.power.shot.1704.exchange'):
                day_exchange_in += int(value)

            # 兑出鸟蛋
            if key.startswith('out.power.power.shot.703.exchange') or key.startswith('out.power.power.shot.704.exchange') or \
                    key.startswith('out.power.power.shot.1703.exchange') or key.startswith('out.power.power.shot.1704.exchange'):
                day_exchange_out += int(value)

            # 金币场-龙蛋消耗
            if key.startswith('out.props.701.') or key.startswith('out.props.1701.'):
                out_props_701_pop[key] = int(out_props_701_pop.get(key, 0)) + -int(value)
                out_props_701 += -int(value)

            if key.startswith('out.props.702.') or key.startswith('out.props.1702.'):
                out_props_702_pop[key] = int(out_props_702_pop.get(key, 0)) + -int(value)
                out_props_702 += -int(value)

            if key.startswith('out.props.703.') or key.startswith('out.props.1703.'):
                out_props_703_pop[key] = int(out_props_703_pop.get(key, 0)) + -int(value)
                out_props_703 += -int(value)

            if key.startswith('out.props.704.') or key.startswith('out.props.1704.'):
                out_props_704_pop[key] = int(out_props_704_pop.get(key, 0)) + -int(value)
                out_props_704 += -int(value)

            # 消耗 锁/传/冰/狂
            if key.startswith('out.props.201.') or key.startswith('out.props.1201.'):
                out_props_201_pop[key] = int(out_props_201_pop.get(key, 0)) + -int(value)
                out_props_201 += -int(value)

            if key.startswith('out.props.202.') or key.startswith('out.props.1202.'):
                out_props_202_pop[key] = int(out_props_202_pop.get(key, 0)) + -int(value)
                out_props_202 += -int(value)

            if key.startswith('out.props.203.') or key.startswith('out.props.1203.'):
                out_props_203_pop[key] = int(out_props_203_pop.get(key, 0)) + -int(value)
                out_props_203 += -int(value)

            if key.startswith('out.props.205.') or key.startswith('out.props.1205.'):
                out_props_205_pop[key] = int(out_props_205_pop.get(key, 0)) + -int(value)
                out_props_205 += -int(value)

            if key.startswith('out.props.301.') or key.startswith('out.props.1301.'):
                out_props_301_pop[key] = int(out_props_301_pop.get(key, 0)) + -int(value)
                out_props_301 += -int(value)

            if key.startswith('out.props.215.') or key.startswith('out.props.1215.'):
                out_props_215_pop[key] = int(out_props_215_pop.get(key, 0)) + -int(value)
                out_props_215 += -int(value)

            if key.startswith('out.props.216.') or key.startswith('out.props.1216.'):
                out_props_216_pop[key] = int(out_props_216_pop.get(key, 0)) + -int(value)
                out_props_216 += -int(value)

            if key.startswith('out.props.217.') or key.startswith('out.props.1217.'):
                out_props_217_pop[key] = int(out_props_217_pop.get(key, 0)) + -int(value)
                out_props_217 += -int(value)

            if key.startswith('out.props.218.') or key.startswith('out.props.1218.'):
                out_props_218_pop[key] = int(out_props_218_pop.get(key, 0)) + -int(value)
                out_props_218 += -int(value)

            if key.startswith('out.props.219.') or key.startswith('out.props.1219.'):
                out_props_219_pop[key] = int(out_props_219_pop.get(key, 0)) + -int(value)
                out_props_219 += -int(value)

            # 产出 锁/传/冰/狂
            if key.startswith('in.props.201.') or key.startswith('in.props.1201.'):
                in_props_201_pop[key] = int(in_props_201_pop.get(key, 0)) + int(value)
                in_props_201 += int(value)

            if key.startswith('in.props.202.') or key.startswith('in.props.1202.'):
                in_props_202_pop[key] = int(in_props_202_pop.get(key, 0)) + int(value)
                in_props_202 += int(value)

            if key.startswith('in.props.203.') or key.startswith('in.props.1203.'):
                in_props_203_pop[key] = int(in_props_203_pop.get(key, 0)) + int(value)
                in_props_203 += int(value)

            if key.startswith('in.props.205.') or key.startswith('in.props.1205.'):
                in_props_205_pop[key] = int(in_props_205_pop.get(key, 0)) + int(value)
                in_props_205 += int(value)

            if key.startswith('in.props.301.') or key.startswith('in.props.1301.'):
                in_props_301_pop[key] = int(in_props_301_pop.get(key, 0)) + int(value)
                in_props_301 += int(value)

            if key.startswith('in.props.215.') or key.startswith('in.props.1215.'):
                in_props_215_pop[key] = int(in_props_215_pop.get(key, 0)) + int(value)
                in_props_215 += int(value)

            if key.startswith('in.props.216.') or key.startswith('in.props.1216.'):
                in_props_216_pop[key] = int(in_props_216_pop.get(key, 0)) + int(value)
                in_props_216 += int(value)

            if key.startswith('in.props.217.') or key.startswith('in.props.1217.'):
                in_props_217_pop[key] = int(in_props_217_pop.get(key, 0)) + int(value)
                in_props_217 += int(value)

            if key.startswith('in.props.218.') or key.startswith('in.props.1218.'):
                in_props_218_pop[key] = int(in_props_218_pop.get(key, 0)) + int(value)
                in_props_218 += int(value)

            if key.startswith('in.props.219.') or key.startswith('in.props.1219.'):
                in_props_219_pop[key] = int(in_props_219_pop.get(key, 0)) + int(value)
                in_props_219 += int(value)

            # 当日洗码量
            if key.startswith('out.power.') and not key.startswith(
                    "out.power.power.shot.703.exchange") and not key.startswith(
                    "out.power.power.shot.704.exchange"):
                day_in_power_pop[key] = int(day_in_power_pop.get(key, 0)) + int(value)
                day_in_power += int(value)

            # 当天剩余龙蛋
            if key.startswith('fix_own_props_701') or key.startswith('fix_own_props_702') or key.startswith('fix_own_props_703') or key.startswith('fix_own_props_704'):
                surplus_props_egg += int(value)

        pay_total_popup = Tips.get_pay_popup(all_pay_count, int(all_pay_total))
        user_info.update({"day_pay_total": day_pay_total, "pay_total_pop": pay_total_popup})

        # 当日洗码量
        day_in_power_popup = Tips.get_out_power_popup(day_in_power_pop, int(day_in_power))
        user_info.update({"day_in_power_pop": day_in_power_popup, "day_in_power": day_in_power})

        in_silver_coupon_popup = Tips.get_in_silver_coupon_popup(in_silver_coupon_pop, int(in_silver_coupon))
        out_silver_coupon_popup = Tips.get_out_silver_coupon_popup(out_silver_coupon_pop, int(out_silver_coupon))
        user_info.update({"in_silver_coupon": in_silver_coupon, "in_silver_coupon_pop": in_silver_coupon_popup, "out_silver_coupon": out_silver_coupon, "out_silver_coupon_pop": out_silver_coupon_popup})

        in_free_coin_popup = Tips.get_in_coin_popup(in_free_coin_pop, int(in_free_coin))
        in_pay_coin_popup = Tips.get_in_coin_popup(in_pay_coin_pop, int(in_pay_coin))
        user_info.update({"in_free_coin_pop": in_free_coin_popup, "in_pay_coin_pop": in_pay_coin_popup})

        in_free_diamond_popup = Tips.get_in_diamond_popup(in_free_diamond_pop, int(in_free_diamond))
        in_pay_diamond_popup = Tips.get_in_diamond_popup(in_pay_diamond_pop, int(in_pay_diamond))
        out_diamond_popup = Tips.get_out_diamond_popup(out_diamond_pop, int(out_diamond))
        user_info.update({"in_free_diamond_pop": in_free_diamond_popup, "in_pay_diamond_pop": in_pay_diamond_popup, "out_diamond_pop": out_diamond_popup})

        in_props_701_popup = Tips.get_in_props_701_popup(in_props_701_pop, int(in_props_701))
        in_props_702_popup = Tips.get_in_props_702_popup(in_props_702_pop, int(in_props_702))
        in_props_703_popup = Tips.get_in_props_703_popup(in_props_703_pop, int(in_props_703))
        in_props_704_popup = Tips.get_in_props_704_popup(in_props_704_pop, int(in_props_704))
        user_info.update({"in_props_701_pop": in_props_701_popup, "in_props_702_pop": in_props_702_popup, "in_props_703_pop": in_props_703_popup, "in_props_704_pop": in_props_704_popup,
                          "in_props_701": in_props_701, "in_props_702": in_props_702, "in_props_703": in_props_703, "in_props_704": in_props_704
                          })

        out_props_701_popup = Tips.get_out_props_701_popup(out_props_701_pop, int(out_props_701))
        out_props_702_popup = Tips.get_out_props_702_popup(out_props_702_pop, int(out_props_702))
        out_props_703_popup = Tips.get_out_props_703_popup(out_props_703_pop, int(out_props_703))
        out_props_704_popup = Tips.get_out_props_704_popup(out_props_704_pop, int(out_props_704))
        user_info.update({"out_props_701_pop": out_props_701_popup, "out_props_702_pop": out_props_702_popup, "out_props_703_pop": out_props_703_popup, "out_props_704_pop": out_props_704_popup,
                          "out_props_701": out_props_701, "out_props_702": out_props_702, "out_props_703": out_props_703, "out_props_704": out_props_704,
                          })

        in_props_201_popup = Tips.get_in_props_201_popup(in_props_201_pop, int(in_props_201))
        out_props_201_popup = Tips.get_out_props_201_popup(out_props_201_pop, int(out_props_201))
        user_info.update({"in_props_201": in_props_201, "out_props_201": out_props_201, "in_props_201_pop": in_props_201_popup, "out_props_201_pop": out_props_201_popup})

        in_props_202_popup = Tips.get_in_props_202_popup(in_props_202_pop, int(in_props_202))
        out_props_202_popup = Tips.get_out_props_202_popup(out_props_202_pop, int(out_props_202))
        user_info.update({"in_props_202": in_props_202, "out_props_202": out_props_202, "in_props_202_pop": in_props_202_popup, "out_props_202_pop": out_props_202_popup})

        in_props_203_popup = Tips.get_in_props_203_popup(in_props_203_pop, int(in_props_203))
        out_props_203_popup = Tips.get_out_props_203_popup(out_props_203_pop, int(out_props_203))
        user_info.update({"in_props_203": in_props_203, "out_props_203": out_props_203, "in_props_203_pop": in_props_203_popup, "out_props_203_pop": out_props_203_popup})

        in_props_205_popup = Tips.get_in_props_205_popup(in_props_205_pop, int(in_props_205))
        out_props_205_popup = Tips.get_out_props_205_popup(out_props_205_pop, int(out_props_205))
        user_info.update({"in_props_205": in_props_205, "out_props_205": out_props_205, "in_props_205_pop": in_props_205_popup, "out_props_205_pop": out_props_205_popup})

        in_props_215_popup = Tips.get_in_props_215_popup(in_props_215_pop, int(in_props_215))
        out_props_215_popup = Tips.get_out_props_215_popup(out_props_215_pop, int(out_props_215))
        user_info.update({"in_props_215": in_props_215, "out_props_215": out_props_215, "in_props_215_pop": in_props_215_popup, "out_props_215_pop": out_props_215_popup,"fix_own_props_215": player_info["fix_own_props_215"]})

        in_props_216_popup = Tips.get_in_props_216_popup(in_props_216_pop, int(in_props_216))
        out_props_216_popup = Tips.get_out_props_216_popup(out_props_216_pop, int(out_props_216))
        user_info.update({"in_props_216": in_props_216, "out_props_216": out_props_216, "in_props_216_pop": in_props_216_popup, "out_props_216_pop": out_props_216_popup,"fix_own_props_216": player_info["fix_own_props_216"]})

        in_props_217_popup = Tips.get_in_props_217_popup(in_props_217_pop, int(in_props_217))
        out_props_217_popup = Tips.get_out_props_217_popup(out_props_217_pop, int(out_props_217))
        user_info.update({"in_props_217": in_props_217, "out_props_217": out_props_217, "in_props_217_pop": in_props_217_popup, "out_props_217_pop": out_props_217_popup,"fix_own_props_217": player_info["fix_own_props_217"]})

        in_props_218_popup = Tips.get_in_props_218_popup(in_props_218_pop, int(in_props_218))
        out_props_218_popup = Tips.get_out_props_218_popup(out_props_218_pop, int(out_props_218))
        user_info.update({"in_props_218": in_props_218, "out_props_218": out_props_218, "in_props_218_pop": in_props_218_popup, "out_props_218_pop": out_props_218_popup,"fix_own_props_218": player_info["fix_own_props_218"]})

        in_props_219_popup = Tips.get_in_props_219_popup(in_props_219_pop, int(in_props_219))
        out_props_219_popup = Tips.get_out_props_219_popup(out_props_219_pop, int(out_props_219))
        user_info.update({"in_props_219": in_props_219, "in_props_219_pop": in_props_219_popup, "out_props_219": out_props_219, "out_props_219_pop": out_props_219_popup,"fix_own_props_219": player_info["fix_own_props_219"]})

        in_props_301_popup = Tips.get_in_props_301_popup(in_props_301_pop, int(in_props_301))
        out_props_301_popup = Tips.get_out_props_301_popup(out_props_301_pop, int(out_props_301))
        user_info.update({"in_props_301": in_props_301, "out_props_301": out_props_301, "in_props_301_pop": in_props_301_popup, "out_props_301_pop": out_props_301_popup,"fix_own_props_301": player_info["fix_own_props_301"]})

        in_props_egg = in_props_701 + in_props_702 + in_props_703 + in_props_704
        out_props_egg = out_props_701 + out_props_702 + out_props_703 + out_props_704
        in_jewel = in_props_215 + in_props_216 + in_props_217 + in_props_218 + in_props_301
        out_jewel = out_props_215 + out_props_216 + out_props_217 + out_props_218 + out_props_301
        fix_own_jewel = int(user_info["fix_own_props_215"]) + int(user_info["fix_own_props_216"]) + int(user_info["fix_own_props_217"]) + int(user_info["fix_own_props_218"]) + int(user_info["fix_own_props_301"])
        in_game_prop = in_props_201 + in_props_202 + in_props_203 + in_props_205
        out_game_prop = out_props_201 + out_props_202 + out_props_203 + out_props_205

        user_info.update({"fix_own_silver_coupon": player_info.get("fix_own_silver_coupon", 0), "surplus_props_egg":surplus_props_egg, "fix_own_props_701":player_info["fix_own_props_701"],
                          "fix_own_props_702": player_info["fix_own_props_702"],"fix_own_props_703":player_info["fix_own_props_703"],"fix_own_props_704":player_info["fix_own_props_704"],"in_free_coin":in_free_coin,
                          "in_pay_coin":in_pay_coin,"in_free_diamond":in_free_diamond,"in_pay_diamond":in_pay_diamond,"out_diamond":out_diamond,"fix_own_diamond":player_info["fix_own_diamond"],"day_exchange_in":day_exchange_in,
                          "day_exchange_out": day_exchange_out, "fix_own_power": player_info["fix_own_power"],"fix_last_own_power": player_info["fix_last_own_power"],"in_props_egg":in_props_egg, "out_props_egg":out_props_egg,
                          "in_jewel": in_jewel, "out_jewel": out_jewel, "fix_own_jewel": fix_own_jewel, "in_game_prop": in_game_prop, "out_game_prop": out_game_prop
                          })
        return user_info

Player = Player()