#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
import random
rand = random.randint

def warp_uptown_east(pc):
	result = script.select(pc, ("enter", "north", "south", "west", "cancel"), "warp")
	if result == 1:
		script.warp(pc, 10023000, rand(217, 218), rand(126, 129)) #アップタウン
	elif result == 2:
		script.warp(pc, 10023400, rand(126, 129), rand(29, 32)) #アップタウン北可動橋
	elif result == 3:
		script.warp(pc, 10023300, rand(126, 129), rand(224, 227)) #アップタウン南可動橋
	elif result == 4:
		script.warp(pc, 10023200, rand(29, 32), rand(126, 129)) #アップタウン西可動橋

def warp_uptown_west(pc):
	result = script.select(pc, ("enter", "north", "east", "south", "cancel"), "warp")
	if result == 1:
		script.warp(pc, 10023000, rand(37, 38), rand(126, 129)) #アップタウン
	elif result == 2:
		script.warp(pc, 10023400, rand(126, 129), rand(29, 32)) #アップタウン北可動橋
	elif result == 3:
		script.warp(pc, 10023100, rand(224, 227), rand(126, 129)) #アップタウン東可動橋
	elif result == 4:
		script.warp(pc, 10023300, rand(126, 129), rand(224, 227)) #アップタウン南可動橋

def warp_uptown_south(pc):
	result = script.select(pc, ("enter", "north", "east", "west", "cancel"), "warp")
	if result == 1:
		script.warp(pc, 10023000, rand(126, 129), rand(37, 38)) #アップタウン
	elif result == 2:
		script.warp(pc, 10023400, rand(126, 129), rand(29, 32)) #アップタウン北可動橋
	elif result == 3:
		script.warp(pc, 10023100, rand(224, 227), rand(126, 129)) #アップタウン東可動橋
	elif result == 4:
		script.warp(pc, 10023200, rand(29, 32), rand(126, 129)) #アップタウン西可動橋

def warp_uptown_north(pc):
	result = script.select(pc, ("enter", "east", "south", "west", "cancel"), "warp")
	if result == 1:
		script.warp(pc, 10023000, rand(126, 129), rand(37, 38)) #アップタウン
	elif result == 2:
		script.warp(pc, 10023100, rand(224, 227), rand(126, 129)) #アップタウン東可動橋
	elif result == 3:
		script.warp(pc, 10023300, rand(126, 129), rand(224, 227)) #アップタウン南可動橋
	elif result == 4:
		script.warp(pc, 10023200, rand(29, 32), rand(126, 129)) #アップタウン西可動橋

def warp_guild_lobby(pc):
	result = script.select(pc, ("1f", "2f", "3f", "4f", "5f", "cancel"), "warp")
	if result == 1:
		script.warp(pc, 30110000, rand(12, 14), rand(14, 16)) #ギルド元宮ロビー１Ｆ
	elif result == 2:
		script.warp(pc, 30111000, rand(12, 14), rand(14, 16)) #ギルド元宮ロビー２Ｆ
	elif result == 3:
		script.warp(pc, 30112000, rand(12, 14), rand(14, 16)) #ギルド元宮ロビー３Ｆ
	elif result == 4:
		script.warp(pc, 30113000, rand(12, 14), rand(14, 16)) #ギルド元宮ロビー４Ｆ
	elif result == 5:
		script.warp(pc, 30114000, rand(12, 14), rand(14, 16)) #ギルド元宮ロビー５Ｆ

def warp_10000700(pc):
	script.effect(pc, 4023)
	script.wait(pc, 1000)
	script.warp(pc, 20015000, 9, 36) #アイシー島への地下通路

def warp_10000817(pc):
	result = script.select(pc, ("中立の島", "海賊の島", "聖女の島", "やっぱやめた"), "どこにする？")
	if result == 1:
		script.warp(pc, 10054100, 224, 86) #フシギ団の砦（北部）
	elif result == 2:
		script.warp(pc, 10054100, 123, 77) #フシギ団の砦（北部）
	elif result == 3:
		script.warp(pc, 10054000, 72, 140) #フシギ団の砦

def warp_10001723(pc):
	script.say(pc, "".join(
		"上にあるクジラの口まで$R;",
		"ロープが伸びている…$R;",
		"$R伝って登れば、$R;",
		"クジラの口の中に入れそうだ。$R;"
	), "warp")
	result = script.select(pc, ("登らない", "登ってみる"), "登る？")
	if result == 2:
		script.warp(pc, 21190000, 32, 184) #口内淵

ID = {
	10000003: warp_uptown_east, #アップタウン東可動橋
	10000013: warp_uptown_west, #アップタウン西可動橋
	10000023: warp_uptown_south, #アップタウン南可動橋
	10000033: warp_uptown_north, #アップタウン北可動橋
	10000164: warp_guild_lobby, #ギルド元宮ロビー１Ｆ
	10000165: warp_guild_lobby, #ギルド元宮ロビー２Ｆ
	10000166: warp_guild_lobby, #ギルド元宮ロビー３Ｆ
	10000167: warp_guild_lobby, #ギルド元宮ロビー４Ｆ
	10000168: warp_guild_lobby, #ギルド元宮ロビー５Ｆ
	10000228: (30113000, 25, 13), #アルケミストギルド→ギルド元宮ロビー４Ｆ
	10000229: (30113000, 1, 13), #マリオネストギルド→ギルド元宮ロビー４Ｆ
	10000230: (30113000, 13, 25), #レンジャーギルド→ギルド元宮ロビー４Ｆ
	10000231: (30113000, 13, 1), #マーチャントギルド→ギルド元宮ロビー４Ｆ
	10000432: (30020001, 3, 5), #イストー岬→民家
	10000600: (30010001, 3, 5), #ノーザンプロムナード→ノーザン酒屋
	#10000624: None,
	#10000632: None,
	#10000634: None,
	10000638: (30170000, 3, 6), #永遠への北限→イグルー
	10000483: (10051000, 96, 123), #アイシー島→永遠への北限
	10000700: warp_10000700, #アイシー島への地下通路
	10000769: (30077000, 8, 12), #アイアンシティ下層階→動力制御室
	10000817: warp_10000817, #フシギ団本部
	10001317: (30091001, 6, 15), #東アクロニア平原→東平原初心者学校
	10001318: (10025000, 108, 123), #東平原初心者学校→東アクロニア平原
	10001319: (30091002, 6, 15), #西アクロニア平原→西平原初心者学校
	10001320: (10022000, 143, 133), #西平原初心者学校→西アクロニア平原
	10001321: (30091003, 6, 15), #南アクロニア平原→南平原初心者学校
	10001322: (10031000, 132, 121), #南平原初心者学校→南アクロニア平原
	10001323: (30091004, 6, 15), #北アクロニア平原→北平原初心者学校
	10001324: (30091004, 6, 15), #北平原初心者学校→北アクロニア平原
	10001723: warp_10001723,
	12001118: (30131001, 6, 1), #フシギ団の砦→フシギ団本部
}

def main(pc):
	warp_info = ID[pc.event_id]
	if callable(warp_info):
		warp_info(pc)
		return
	map_id = warp_info[0]
	if len(warp_info) == 3:
		x = warp_info[1]
		y = warp_info[2]
	else:
		x = random.randint(warp_info[1], warp_info[3])
		y = random.randint(warp_info[2], warp_info[4])
	script.warp(pc, map_id, x, y)

#Copyright (C) ゆとり鯖 All Rights Reserved.
