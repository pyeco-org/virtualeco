#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib import general
from lib import db

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
		result += general.pack((player and getattr(player, attr) or 0), i)
	return result

def make_0002(ver):
	"""認証接続確認(s0001)の応答"""
	return ver

def make_001e(word):
	"""PASS鍵"""
	return word

def make_000f(word):
	"""マップサーバーのPASS鍵送信"""
	return word

def make_000b(data):
	"""接続・接続確認(s000a)の応答"""
	return data

def make_0011():
	"""認証結果(マップサーバーに認証情報の送信(s0010)に対する応答)"""
	result = general.pack(0, 4)
	#result += general.pack_str(";")
	#result += general.pack(0, 4)
	result += "\x01\x00"
	result += "\x48\x6e\xb4\x20"
	return result

def make_0020(user, _type):
	"""アカウント認証結果/ログアウト開始/ログアウトキャンセル"""
	if _type == "loginsucess":
		return "\x00\x00\x00\x00"+general.pack(user.user_id, 4)+"\x00\x00\x00\x00"*2
	elif _type == "loginfaild":
		return "\xFF\xFF\xFF\xFE"+general.pack(user.user_id, 4)+"\x00\x00\x00\x00"*2
	elif _type == "isonline":
		return "\xFF\xFF\xFF\xFB"+general.pack(user.user_id, 4)+"\x00\x00\x00\x00"*2
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

def make_00a8(player):
	"""キャラクターマップ通知"""
	return general.pack(player.map, 4)

def make_0028(user):
	"""4キャラクターの基本属性"""
	result = general.pack(len(user.player), 1) #キャラ数
	for player in user.player:
		result += player and general.pack_str(player.name) or "\x00" #名前
	result += pack_user_data(user, "race", 1) #種族
	result += pack_user_data(user, "form", 1) #フォーム（DEMの）
	result += pack_user_data(user, "gender", 1) #性別
	result += pack_user_data(user, "hair", 2) #髪型
	result += pack_user_data(user, "haircolor", 1) #髪色
	#ウィング #ない時は\xFF\xFF
	result += pack_user_data(user, "wig", 2)
	result += general.pack(len(user.player), 1) #不明
	for player in user.player:
		result += general.pack((player and -1 or 0), 1)
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
		result += general.pack((player and 3 or 0), 2)
	result += pack_user_data(user, "lv_job2x", 1) #2次職レベル
	result += pack_user_data(user, "lv_job2t", 1) #2.5次職レベル
	result += pack_user_data(user, "lv_job3", 1) #3次職レベル
	return result

def make_0033(reply_ping=False):
	"""接続先通知要求(ログインサーバ/0032)の応答"""
	if reply_ping:
		result = ""
	else:
		from lib import server
		result = "\x01"
		result += general.pack_str(server.config.serveraddress)
		result += general.pack_int(server.config.mapserverport)
	return result

def make_09e9(player):
	"""装備情報#IDのキャラの見た目を変更"""
	result = general.pack(player.id, 4)
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
	result += general.pack((item_head and
			item_head.type == "HELM" and
			item_head.id or 0), 4)
	#頭アクセサリ
	result += general.pack((item_head and
			item_head.type == "ACCESORY_HEAD" and
			item_head.id or 0), 4)
	#顔
	result += general.pack((item_face and
			item_face.type == "FULLFACE" and
			item_face.id or 0), 4)
	#顔アクセサリ
	result += general.pack((item_face and
			item_face.type == "ACCESORY_FACE" and
			item_face.id or 0), 4)
	#胸アクセサリ
	result += general.pack((item_chestacce and
			item_chestacce.type in general.ACCESORY_TYPE_LIST and
			item_chestacce.id or 0), 4)
	#上半身+下半身
	if item_tops and item_tops.type == "ONEPIECE":
		result += general.pack(item_tops.id, 4)
		result += general.pack(0, 4)
	else:
		result += general.pack((item_tops and
				item_tops.type in general.UPPER_TYPE_LIST and
				item_tops.id or 0), 4)
		result += general.pack((item_buttoms and
				item_buttoms.type in general.LOWER_TYPE_LIST and
				item_buttoms.id or 0), 4)
	#背中
	result += general.pack((item_backpack and
			item_backpack.type == "BACKPACK" and
			item_backpack.id or 0), 4)
	#右手装備
	result += general.pack((item_right and
			item_right.type in general.RIGHT_TYPE_LIST and
			item_right.id or 0), 4)
	#左手装備
	result += general.pack((item_left and
			item_left.type in general.LEFT_TYPE_LIST and
			item_left.id or 0), 4)
	#靴
	result += general.pack((item_shoes and
			item_shoes.type in general.BOOTS_TYPE_LIST and
			item_shoes.id or 0), 4)
	#靴下
	result += general.pack((item_sock and
			item_sock.type == "SOCKS" and
			item_sock.id or 0), 4)
	#ペット
	result += general.pack((item_pet and
			item_pet.type in general.PET_TYPE_LIST and
			item_pet.id or 0), 4)
	result += "\x03"+"\x00\x00\x00" #左手モーションタイプ size=3 (片手, 両手, 攻撃)
	result += "\x03"+"\x00\x00\x00" #右手モーションタイプ size=3 #chr_act_tbl.csvを参照する
	result += "\x03"+"\x00\x00\x00" #乗り物モーションタイプ size=3
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

def make_1239(player, loading=False):
	"""キャラ速度通知・変更"""
	result = general.pack(player.id, 4)
	result += general.pack(loading and 10 or player.status.speed, 2)
	return result

def make_0fa7(player, mode=0x02):
	"""キャラのモード変更"""
	result = general.pack(player.id, 4)
	result += general.pack(mode, 4) #通常 00000002
	result += general.pack(0, 4)
	return result

def make_1a5f():
	"""右クリ設定"""
	return general.pack(0, 4)

def make_0203(item, iid, part):
	"""インベントリ情報"""
	result = general.pack(0, 1) #unknown #常に0
	result += "\xd6" #データサイズ
	result += general.pack(iid, 4) #インベントリID
	result += general.pack(item.id, 4) #アイテムID
	result += general.pack(0, 4) #見た目,フィギュア,スケッチ情報
	result += general.pack(part, 1) #アイテムの場所
	result += general.pack(0x01, 4) #鑑定済み:0x01 カードロック？:0x20
	result += general.pack(item.durability_max, 2) #耐久度
	result += general.pack(item.durability_max, 2) #最大耐久度or最大親密度
	result += general.pack(0, 2) #強化回数
	result += general.pack(0, 2) #カードスロット数
	result += general.pack(0, 4) #カードID1
	result += general.pack(0, 4) #カードID2
	result += general.pack(0, 4) #カードID3
	result += general.pack(0, 4) #カードID4
	result += general.pack(0, 4) #カードID5
	result += general.pack(0, 4) #カードID6
	result += general.pack(0, 4) #カードID7
	result += general.pack(0, 4) #カードID8
	result += general.pack(0, 4) #カードID9
	result += general.pack(0, 4) #カードID10
	result += general.pack(0, 1) #染色
	result += general.pack(item.count, 2) #個数
	result += general.pack(item.price, 4) #ゴーレム販売価格
	result += general.pack(0, 2) #ゴーレム販売個数
	result += general.pack(0, 2) #憑依重量
	result += general.pack(0, 2) #最大重量
	result += general.pack(0, 2) #最大容量
	result += general.pack(0, 2) #位置的に発動Skill？
	result += general.pack(0, 2) #使用可能Skill
	result += general.pack(0, 2) #位置的にパッシブスキル？
	result += general.pack(0, 2) #位置的に憑依時可能Skill？
	result += general.pack(0, 2) #位置的に憑依パッシブSkill？
	result += general.pack(item.str, 2) #str
	result += general.pack(item.mag, 2) #mag
	result += general.pack(item.vit, 2) #vit
	result += general.pack(item.dex, 2) #dex
	result += general.pack(item.agi, 2) #agi
	result += general.pack(item.int, 2) #int
	result += general.pack(item.luk, 2) #luk （ペットの場合現在HP
	result += general.pack(item.cha, 2) #cha（ペットの場合転生回数
	result += general.pack(item.hp, 2) #HP（使用出来るアイテムは回復
	result += general.pack(item.sp, 2) #SP（同上
	result += general.pack(item.mp, 2) #MP（同上
	result += general.pack(item.speed, 2) #移動速度
	result += general.pack(item.atk1, 2) #物理攻撃力(叩)
	result += general.pack(item.atk2, 2) #物理攻撃力(斬)
	result += general.pack(item.atk3, 2) #物理攻撃力(突)
	result += general.pack(item.matk, 2) #魔法攻撃力
	result += general.pack(item.DEF, 2) #物理防御
	result += general.pack(item.mdef, 2) #魔法防御
	result += general.pack(item.s_hit, 2) #近命中力
	result += general.pack(item.l_hit, 2) #遠命中力
	result += general.pack(item.magic_hit, 2) #魔命中力
	result += general.pack(item.s_avoid, 2) #近回避
	result += general.pack(item.l_avoid, 2) #遠回避
	result += general.pack(item.magic_avoid, 2) #魔回避
	result += general.pack(item.critical_hit, 2) #クリティカル
	result += general.pack(item.critical_avoid, 2) #クリティカル回避
	result += general.pack(item.heal_hp, 2) #回復力？
	result += general.pack(item.heal_mp, 2) #魔法回復力？
	result += general.pack(0, 2) #スタミナ回復力？
	result += general.pack(item.energy, 2) #無属性？
	result += general.pack(item.fire, 2) #火属性
	result += general.pack(item.water, 2) #水属性
	result += general.pack(item.wind, 2) #風属性
	result += general.pack(item.earth, 2) #地属性
	result += general.pack(item.light, 2) #光属性
	result += general.pack(item.dark, 2) #闇属性
	result += general.pack(item.poison, 2) #毒（+なら毒回復、−なら毒状態に
	result += general.pack(item.stone, 2) #石化
	result += general.pack(item.paralyze, 2) #麻痺
	result += general.pack(item.sleep, 2) #睡眠
	result += general.pack(item.silence, 2) #沈黙
	result += general.pack(item.slow, 2) #鈍足
	result += general.pack(item.confuse, 2) #混乱
	result += general.pack(item.freeze, 2) #凍結
	result += general.pack(item.stan, 2) #気絶
	result += general.pack(0, 2) #ペットステ（攻撃速度
	result += general.pack(0, 2) #ペットステ（詠唱速度
	result += general.pack(0, 2) #ペットステ？（スタミナ回復力？
	result += general.pack(item.price, 4) #ゴーレム露店の買取価格
	result += general.pack(0, 2) #ゴーレム露店の買取個数
	result += general.pack(item.price, 4) #商人露店の販売価格
	result += general.pack(0, 2) #商人露店の販売個数
	result += general.pack(0, 4) #何かの価格？ 商人露店の買取価格の予約？
	result += general.pack(0, 2) #何かの個数？
	result += general.pack(1, 2) #unknow
	result += general.pack(1, 1) #unknow
	result += general.pack(0, 2) #unknow
	result += general.pack(-1, 4) #unknow
	result += general.pack(0, 1) #unknow
	return result

def make_01ff(player):
	"""自分のキャラクター情報"""
	result = general.pack(player.id, 4)
	result += general.pack(player.id, 4) #固有ID
	result += general.pack_str(player.name) #名前
	result += general.pack(player.race, 1) #種族
	result += general.pack(player.form, 1) #フォーム
	result += general.pack(player.gender, 1) #性別
	result += general.pack(player.hair, 2) #髪型
	result += general.pack(player.haircolor, 1) #髪色
	result += general.pack(player.wig, 2) #ウィング
	result += "\xff" #不明
	result += general.pack(player.face, 2) #顔
	result += general.pack(player.base_lv, 1) #転生前のレベル
	result += general.pack(player.ex, 1) #転生特典
	result += general.pack(player.wing, 1) #転生翼
	result += general.pack(player.wingcolor, 1) #転生翼色
	result += general.pack(player.map, 4) #マップ
	result += general.pack(player.x, 1)
	result += general.pack(player.y, 1)
	result += general.pack(player.dir, 1)
	result += general.pack(player.status.hp, 4)
	result += general.pack(player.status.maxhp, 4)
	result += general.pack(player.status.mp, 4)
	result += general.pack(player.status.maxmp, 4)
	result += general.pack(player.status.sp, 4)
	result += general.pack(player.status.maxsp, 4)
	result += general.pack(player.status.ep, 4)
	result += general.pack(player.status.maxep, 4)
	result += general.pack(9, 2) #不明
	result += "\x08" #ステータス数#常に0x08
	result += general.pack(player.str, 2) #str
	result += general.pack(player.dex, 2) #dex
	result += general.pack(player.int, 2) #int
	result += general.pack(player.vit, 2) #vit
	result += general.pack(player.agi, 2) #agi
	result += general.pack(player.mag, 2) #mag
	result += general.pack(0, 2) #luk
	result += general.pack(0, 2) #cha
	result += "\x14" #equip_len?
	result += general.pack(0, 2) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(-1, 4) #憑依対象サーバーキャラID
	result += general.pack(0, 1) #憑依場所 ( r177b等も参照
	result += general.pack(player.gold, 4) #所持金
	result += make_09e9(player)[4:] #装備の\x0dから乗り物の染色値まで
	result += general.pack(1, 1) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(2, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #不明
	result += general.pack(0, 4) #unknow
	result += general.pack(0, 4) #unknow
	result += general.pack(1, 2) #不明
	return result

def make_03f2(msg_id):
	"""システムメッセージ""" #msg_id 0x04: 構えが「叩き」に変更されました
	return general.pack(msg_id, 2)

def make_09ec(player):
	"""ゴールドを更新する、値は更新後の値"""
	return general.pack(player.gold, 4)

def make_0221(player):
	"""最大HP/MP/SP"""
	result = general.pack(player.id, 4)
	result += "\x04"
	result += general.pack(player.status.maxhp, 4)
	result += general.pack(player.status.maxmp, 4)
	result += general.pack(player.status.maxsp, 4)
	result += general.pack(player.status.maxep, 4)
	return result

def make_021c(player):
	"""現在のHP/MP/SP/EP"""
	result = general.pack(player.id, 4)
	result += "\x04"
	result += general.pack(player.status.hp, 4)
	result += general.pack(player.status.mp, 4)
	result += general.pack(player.status.sp, 4)
	result += general.pack(player.status.ep, 4)
	return result

def make_0212(player):
	"""ステータス・補正・ボーナスポイント"""
	result = "\x08" #base
	result += general.pack(player.str, 2) #str
	result += general.pack(player.dex, 2) #dex
	result += general.pack(player.int, 2) #int
	result += general.pack(player.vit, 2) #vit
	result += general.pack(player.agi, 2) #agi
	result += general.pack(player.mag, 2) #mag
	result += general.pack(0, 2) #luk
	result += general.pack(0, 2) #cha
	result += "\x08" #revise
	result += general.pack(player.stradd, 2) #str
	result += general.pack(player.dexadd, 2) #dex
	result += general.pack(player.intadd, 2) #int
	result += general.pack(player.vitadd, 2) #vit
	result += general.pack(player.agiadd, 2) #agi
	result += general.pack(player.magadd, 2) #mag
	result += general.pack(0, 2) #luk
	result += general.pack(0, 2) #cha
	result += "\x08" #bounus
	result += general.pack(0, 2) #str
	result += general.pack(0, 2) #dex
	result += general.pack(0, 2) #int
	result += general.pack(0, 2) #vit
	result += general.pack(0, 2) #agi
	result += general.pack(0, 2) #mag
	result += general.pack(0, 2) #luk
	result += general.pack(0, 2) #cha
	return result

def make_0217(player):
	"""詳細ステータス"""
	result = "\x1e" #30
	result += general.pack(player.status.speed, 2) #歩く速度
	result += general.pack(player.status.minatk1, 2) #最小ATK1
	result += general.pack(player.status.minatk2, 2) #最小ATK2
	result += general.pack(player.status.minatk3, 2) #最小ATK3
	result += general.pack(player.status.maxatk1, 2) #最大ATK1
	result += general.pack(player.status.maxatk2, 2) #最大ATK2
	result += general.pack(player.status.maxatk3, 2) #最大ATK3
	result += general.pack(player.status.minmatk, 2) #最小MATK
	result += general.pack(player.status.maxmatk, 2) #最大MATK
	result += general.pack(player.status.leftdef, 2) #基本DEF
	result += general.pack(player.status.rightdef, 2) #追加DEF
	result += general.pack(player.status.leftmdef, 2) #基本MDEF
	result += general.pack(player.status.rightmdef, 2) #追加MDEF
	result += general.pack(player.status.shit, 2) #S.HIT(近距離命中率)
	result += general.pack(player.status.lhit, 2) #L.HIT(遠距離命中率)
	result += general.pack(player.status.mhit, 2) #魔法命中
	result += general.pack(player.status.chit, 2) #クリティカル命中
	result += general.pack(player.status.savoid, 2) #S.AVOID(近距離回避力)
	result += general.pack(player.status.lavoid, 2) #L.AVOID(遠距離回避力)
	result += general.pack(0, 2) #魔法回避力
	result += general.pack(player.status.hpheal,2) #HP回復率
	result += general.pack(player.status.mpheal,2) #MP回復率
	result += general.pack(player.status.spheal,2) #SP回復率
	result += general.pack(0, 2) #不明
	result += general.pack(player.status.aspd,2) #A.SPD(攻撃速度)
	result += general.pack(player.status.cspd,2) #C.SPD(詠唱速度)
	result += general.pack(0, 2) #不明
	result += general.pack(0, 2) #不明
	result += general.pack(0, 2) #不明
	result += general.pack(0, 2) #不明
	return result

def make_0230(player):
	"""現在CAPA/PAYL"""
	result = "\x04"
	result += general.pack(player.status.capa, 4) #CAPA(x0.1)
	result += general.pack(player.status.rightcapa, 4) #右手かばんCAPA(x0.1)
	result += general.pack(player.status.leftcapa, 4) #左手かばんCAPA(x0.1)
	result += general.pack(player.status.backcapa, 4) #背中CAPA(x0.1)
	result += "\x04"
	result += general.pack(player.status.payl, 4) #PAYL(x0.1)
	result += general.pack(player.status.rightpayl, 4) #右手かばんPAYL(x0.1)
	result += general.pack(player.status.leftpayl, 4) #左手かばんPAYL(x0.1)
	result += general.pack(player.status.backpayl, 4) #背中PAYL(x0.1)
	return result

def make_0231(player):
	"""最大CAPA/PAYL"""
	result = "\x04"
	result += general.pack(player.status.maxcapa, 4) #CAPA(x0.1)
	result += general.pack(player.status.maxrightcapa, 4) #右手かばんCAPA(x0.1)
	result += general.pack(player.status.maxleftcapa, 4) #左手かばんCAPA(x0.1)
	result += general.pack(player.status.maxbackcapa, 4) #背中CAPA(x0.1)
	result += "\x04"
	result += general.pack(player.status.maxpayl, 4) #PAYL(x0.1)
	result += general.pack(player.status.maxrightpayl, 4) #右手かばんPAYL(x0.1)
	result += general.pack(player.status.maxleftpayl, 4) #左手かばんPAYL(x0.1)
	result += general.pack(player.status.maxbackpayl, 4) #背中PAYL(x0.1)
	return result

def make_0244(player):
	"""職業"""
	result = general.pack(player.job, 4) #職業ID
	result += general.pack(0, 4) #ジョイントジョブID
	return result

def make_0226(player, job):
	"""スキル一覧"""
	result = ""
	if job == 0:
		skill_list_length = general.pack(len(player.skill_list), 1)
		result += skill_list_length #スキルID
		for skill_id in player.skill_list:
			result += general.pack(skill_id, 2)
		result += skill_list_length #習得Lv
		for skill_id in player.skill_list:
			result += general.pack(db.skill[skill_id].maxlv, 2)
		result += skill_list_length #不明
		for skill_id in player.skill_list:
			result += general.pack(0, 2)
		result += skill_list_length #習得可能Lv
		for skill_id in player.skill_list:
			result += general.pack(1, 2)
	else:
		skill_list_length = general.pack(0, 1)
		result += skill_list_length #スキルID
		result += skill_list_length #習得Lv
		result += skill_list_length #不明
		result += skill_list_length #習得可能Lv
	result += general.pack(job, 1) #一次職0 エキスパ1 etc...
	result += skill_list_length #習得スキル数 #TODO#レベル０のスキルを計算から外す
	return result

def make_022e(player):
	"""リザーブスキル"""
	return general.pack(0, 2)

def make_023a(player):
	"""Lv JobLv ボーナスポイント スキルポイント"""
	result = general.pack(player.lv_base, 1) #Lv
	result += general.pack(player.lv_job1, 1) #JobLv(1次職)
	result += general.pack(player.lv_job2x, 1) #JobLv(エキスパート)
	result += general.pack(player.lv_job2t, 1) #JobLv(テクニカル)
	result += general.pack(player.lv_job3, 1) #三次職のレベル？
	result += general.pack(1, 1) #JobLv(ジョイント？ブリーダー？)
	result += general.pack(1, 2) #ボーナスポイント
	result += general.pack(3, 2) #スキルポイント(1次職)
	result += general.pack(0, 2) #スキルポイント(エキスパート)
	result += general.pack(0, 2) #スキルポイント(テクニカル)
	result += general.pack(0, 2) #三次職のポイント？
	return result

def make_0235(player):
	"""EXP/JOBEXP"""
	result = general.pack(0, 4) #EXP(x0.1%)
	result += general.pack(0, 4) #JobEXP(x0.1%)
	result += general.pack(0, 4) #WarRecodePoint
	result += general.pack(0, 4) #ecoin
	result += "\x00\x00\x00\x00\x00\x00\x00\x00" #baseexp #signed long
	result += "\x00\x00\x00\x00\x00\x00\x00\x00" #jobexp #signed long
	return result

def make_1f72(show=False):
	"""もてなしタイニーアイコン""" #before login
	return general.pack((show and 1 or 0), 1)

def make_157c(player,
			state01=0, state02=0, state03=0,
			state04=0, state05=0, state06=0,
			state07=0, state08=0, state09=0):
	"""キャラの状態""" #send when loading map and after load
	#キャラの自然回復や状態異常等、様々な状態を更新する
	#状態に応じて画面上にアイコンが出る
	#毒などの場合エフェクトも出る
	result = general.pack(player.id, 4)
	result += general.pack(state01, 4)
	result += general.pack(state02, 4)
	result += general.pack(state03, 4)
	result += general.pack(state04, 4)
	result += general.pack(state05, 4)
	result += general.pack(state06, 4)
	result += general.pack(state07, 4)
	result += general.pack(state08, 4)
	result += general.pack(state09, 4)
	return result

def make_022d(player):
	"""HEARTスキル""" #send when loading map and after load
	result = "\x03" #スキルの数
	result += "\x27\x74"
	result += "\x27\x75"
	result += "\x27\x76"
	return result

def make_0223(player):
	"""属性値""" #send when loading map
	result = "\x07" #攻撃
	result += general.pack(0, 2) #新生属性？
	result += general.pack(0, 2) #火
	result += general.pack(0, 2) #水
	result += general.pack(0, 2) #風
	result += general.pack(0, 2) #土
	result += general.pack(0, 2) #光
	result += general.pack(0, 2) #闇
	result += "\x07" #防御
	result += general.pack(0, 2) #新生属性？
	result += general.pack(0, 2) #火
	result += general.pack(0, 2) #水
	result += general.pack(0, 2) #風
	result += general.pack(0, 2) #土
	result += general.pack(0, 2) #光
	result += general.pack(0, 2) #闇
	return result

def make_122a(mob_id_list=()):
	"""モンスターID通知""" #send when loading map and after load and make mob
	if not mob_id_list:
		return "\x00"
	else:
		result = general.pack(40, 1)
		for mob_id in mob_id_list:
			result += general.pack(mob_id, 4)
		result += general.pack(0, 4)*(40-len(mob_id_list))
	return result

def make_1bbc():
	"""スタンプ帳詳細""" #send when loading map
	result = "\x0b" #ジャンル数 常に0b
	result += general.pack(0, 2) #スペシャル
	result += general.pack(0, 2) #プルル
	result += general.pack(0, 2) #平原
	result += general.pack(0, 2) #海岸
	result += general.pack(0, 2) #荒野
	result += general.pack(0, 2) #大陸ダンジョン
	result += general.pack(0, 2) #雪国
	result += general.pack(0, 2) #廃炭鉱ダンジョン
	result += general.pack(0, 2) #ノーザンダンジョン
	result += general.pack(0, 2) #アイアンサウス
	result += general.pack(0, 2) #サウスダンジョン
	return result

def make_025d():
	"""不明""" #send when loading map
	return "\x00" #不明

def make_0695():
	"""不明""" #send when loading map
	return "\x00\x00\x00\x02\x00" #不明

def make_0236(player):
	"""wrp ranking""" #send when loading map
	result = general.pack(0, 4)
	result += general.pack(player.wrprank, 4) #wrpの順位
	return result

def make_1b67(player):
	"""マップ情報完了通知
	MAPログイン時に基本情報を全て受信した後に受信される"""
	result = general.pack(player.id, 4)
	result += general.pack(0, 1) #unknow
	return result
