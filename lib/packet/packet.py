#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib import general

def make(data_type, *args):
	if args and hasattr(args[0], "lock"):
		with args[0].lock:
			data_value = eval("make_%s"%data_type)(*args)
	else:
		data_value = eval("make_%s"%data_type)(*args)
	if data_value == None:
		print "packet make error:", data_type, args
		return ""
	packet = general.pack_short(len(data_value)+2)
	packet += data_type.decode("hex")
	packet += data_value
	#print "make", packet.encode("hex")
	return general.encode(packet)

def pack_user_data(user, attr, i):
	result = "\x04"
	for player in user.player:
		result += player and general.pack(getattr(player, attr), i) or "\x00"*i
	return result

def make_0002(ver):
	"""認証接続確認(s0001)の応答"""
	return ver

def make_001e(word):
	"""PASS鍵"""
	return word

def make_000b(data):
	"""接続・接続確認(s000a)の応答"""
	return data

def make_0020(user, _type):
	"""アカウント認証結果/ログアウト開始/ログアウトキャンセル"""
	if _type == "loginsucess":
		return "\x00\x00\x00\x00"+general.pack(user.userid, 4)+"\x00\x00\x00\x00"*2
	elif _type == "loginfaild":
		return "\xFF\xFF\xFF\xFE"+general.pack(user.userid, 4)+"\x00\x00\x00\x00"*2
	elif _type == "isonline":
		return "\xFF\xFF\xFF\xFB"+general.pack(user.userid, 4)+"\x00\x00\x00\x00"*2
	elif _type == "logoutstart":
		return "\x00"
	elif _type == "logoutcancel":
		return "\xF9"
	else:
		print "make_0020: type not exist", _type

def make_00a1(_type):
	"""キャラクター作成結果"""
	if _type == "sucess":
		return "\x00\x00\x00\x00"
	elif _type == "nametoolong":
		return "\xff\xff\xff\x9c"
	elif _type == "slotexist":
		return "\xff\xff\xff\x9d"
	elif _type == "nameexist":
		return "\xff\xff\xff\x9e"
	elif _type == "nametooshort":
		return "\xff\xff\xff\x9f"
	elif _type == "namebadchar":
		return "\xff\xff\xff\xa0"
	elif _type == "other":
		return "\xff\xff\xff\xff"
	else:
		print "make_00a1: type not exist", _type

def make_00a6(sucess):
	"""キャラクター削除結果"""
	return sucess and "\x00" or "\x9c"

def make_0028(user):
	"""4キャラクターの基本属性"""
	result = general.pack(len(user.player), 1)#キャラ数
	for player in user.player:
		result += player and general.pack_str(player.name) or "\x00"#名前
	result += pack_user_data(user, "race", 1) #種族
	result += pack_user_data(user, "form", 1) #フォーム（DEMの）
	result += pack_user_data(user, "gender", 1) #性別
	result += pack_user_data(user, "hair", 2) #髪型
	result += pack_user_data(user, "haircolor", 1) #髪色
	#ウィング #ない時は\xFF\xFF
	result += pack_user_data(user, "wig", 2)
	result += general.pack(len(user.player), 1) #不明
	for player in user.player:
		result += player and "\xFF" or "\x00"
	result += pack_user_data(user, "face", 2) #顔
	#転生前のレベル #付ければ上位種族になる
	result += pack_user_data(user, "base_lv", 1)
	result += pack_user_data(user, "ex", 1) #転生特典？
	#if player.race = 1 than player.ex = 32 or 111+
	result += pack_user_data(user, "wing", 1) #転生翼？
	#if player.race = 1 than player.wing = 35 ~ 39
	result += pack_user_data(user, "wingcolor", 1) #転生翼色？
	#if player.race = 1 than player.wingcolor = 45 ~ 55
	result += pack_user_data(user, "job", 1) #職業
	result += pack_user_data(user, "map", 4) #マップ
	result += pack_user_data(user, "lv_base", 1) #レベル
	result += pack_user_data(user, "lv_job1", 1) #1次職レベル
	result += general.pack(len(user.player), 1) #残りクエスト数
	for player in user.player:
		result += player and "\x00\x03" or "\x00\x00"
	result += pack_user_data(user, "lv_job2x", 1) #2次職レベル
	result += pack_user_data(user, "lv_job2t", 1) #2.5次職レベル
	result += pack_user_data(user, "lv_job3", 1) #3次職レベル
	return result

def make_09e9(player):
	"""装備情報#IDのキャラの見た目を変更"""
	result = general.pack(player.charid, 4)#キャラID
	result += "\x0d" #装備の数(常に0x0d) #13
	item_head = player.item.get(player.equip.head)
	item_face = player.item.get(player.equip.face)
	item_chestacce = player.item.get(player.equip.chestacce)
	item_tops = player.item.get(player.equip.tops)
	item_buttoms = player.item.get(player.equip.bottoms)
	item_backpack = player.item.get(player.equip.backpack)
	item_right = player.item.get(player.equip.right)
	item_left = player.item.get(player.equip.left)
	item_shoes = player.item.get(player.equip.shoes)
	item_sock = player.item.get(player.equip.socks)
	item_pet = player.item.get(player.equip.pet)
	#頭
	result += ((item_head and item_head.type == "HELM") and
		general.pack(item_head.id, 4) or general.pack(0, 4))
	#頭アクセサリ
	result += ((item_head and item_head.type == "HELM") and
		general.pack(item_head.id, 4) or general.pack(0, 4))
	#顔
	result += ((item_face and item_face.type == general.pack(0, 4)) and
		general.pack(item_face.id, 4) or general.pack(0, 4))
	#顔アクセサリ
	result += ((item_face and item_face.type == general.pack(0, 4)) and
		general.pack(item_face.id, 4) or general.pack(0, 4))
	#胸アクセサリ
	result += ((item_chestacce and
		item_chestacce.type in general.ACCESORY_TYPE_LIST) and
		general.pack(item_chestacce.id, 4) or general.pack(0, 4))
	#上半身+下半身
	if item_tops and item_tops.type == "ONEPIECE":
		result += general.pack(item_tops.id, 4)
		result += general.pack(0, 4)
	else:
		result += ((item_tops and
			item_tops.type in general.UPPER_TYPE_LIST) and
			general.pack(item_tops.id, 4) or general.pack(0, 4))
		result += ((item_buttoms and
			item_buttoms.type in general.LOWER_TYPE_LIST) and
			general.pack(item_buttoms.id, 4) or general.pack(0, 4))
	#背中
	result += ((item_backpack and item_backpack.type == "BACKPACK") and
		general.pack(item_backpack.id, 4) or general.pack(0, 4))
	#右手装備
	result += ((item_right and
		item_right.type in general.RIGHT_TYPE_LIST) and
		general.pack(item_right.id, 4) or general.pack(0, 4))
	#左手装備
	result += ((item_left and
		item_left.type in general.LEFT_TYPE_LIST) and
		general.pack(item_left.id, 4) or general.pack(0, 4))
	#靴
	result += ((item_shoes and
		item_shoes.type in general.BOOTS_TYPE_LIST) and
		general.pack(item_shoes.id, 4) or general.pack(0, 4))
	#靴下
	result += ((item_sock and item_sock.type == "SOCKS") and
		general.pack(item_sock.id, 4) or general.pack(0, 4))
	#ペット
	result += ((item_pet and
		item_pet.type in general.PET_TYPE_LIST) and
		general.pack(item_pet.id, 4) or general.pack(0, 4))
	result += "\03"+"\00\00\00" #左手モーションタイプ size=3 { 片手, 両手, 攻撃}
	result += "\03"+"\00\00\00" #右手モーションタイプ size=3 #chr_act_tbl.csvを参照する
	result += "\03"+"\00\00\00" #乗り物モーションタイプ size=3
	result += general.pack(0, 4) #乗り物アイテムID
	result += general.pack(0, 1) #乗り物の染色値
	result += general.pack(0, 1) #戦闘状態の時1#0fa6で変更要請#0fa7で変更される
	return result

def make_0029(user):
	"""4キャラクターの装備"""
	result = ""
	for player in user.player:
		if player:
			result += "\x0d"+make_09e9(player)[5:5+13*4]
		else:
			result += "\x0d"+general.pack(0, 4)*13
	return result
