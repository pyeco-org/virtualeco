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

def pack_user_data(pack, user, attr):
	result = "\x04"
	for player in user.player:
		result += pack((player and getattr(player, attr) or 0))
	return result
def pack_user_byte(*args):
	return pack_user_data(general.pack_byte, *args)
def pack_user_short(*args):
	return pack_user_data(general.pack_short, *args)
def pack_user_int(*args):
	return pack_user_data(general.pack_int, *args)

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
	result = general.pack_int(0)
	#result += general.pack_str(";")
	#result += general.pack(0, 4)
	result += "\x01\x00"
	result += "\x48\x6e\xb4\x20"
	return result

def make_0020(user, _type):
	"""アカウント認証結果/ログアウト開始/ログアウトキャンセル"""
	if _type == "loginsucess":
		return "\x00\x00\x00\x00"+general.pack_int(user.user_id)+"\x00\x00\x00\x00"*2
	elif _type == "loginfaild":
		return "\xFF\xFF\xFF\xFE"+general.pack_int(user.user_id)+"\x00\x00\x00\x00"*2
	elif _type == "isonline":
		return "\xFF\xFF\xFF\xFB"+general.pack_int(user.user_id)+"\x00\x00\x00\x00"*2
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
	return general.pack_int(player.map_id)

def make_0028(user):
	"""4キャラクターの基本属性"""
	result = general.pack_byte(len(user.player)) #キャラ数
	for player in user.player:
		result += player and general.pack_str(player.name) or "\x00" #名前
	result += pack_user_byte(user, "race") #種族
	result += pack_user_byte(user, "form") #フォーム（DEMの）
	result += pack_user_byte(user, "gender") #性別
	result += pack_user_short(user, "hair") #髪型
	result += pack_user_byte(user, "haircolor") #髪色
	#ウィング #ない時は\xFF\xFF
	result += pack_user_short(user, "wig")
	result += general.pack_byte(len(user.player)) #不明
	for player in user.player:
		result += general.pack_byte((player and -1 or 0))
	result += pack_user_short(user, "face") #顔
	#転生前のレベル #付ければ上位種族になる
	result += pack_user_byte(user, "base_lv")
	result += pack_user_byte(user, "ex") #転生特典？
	#if player.race = 1 than player.ex = 32 or 111+
	result += pack_user_byte(user, "wing") #転生翼？
	#if player.race = 1 than player.wing = 35 ~ 39
	result += pack_user_byte(user, "wingcolor") #転生翼色？
	#if player.race = 1 than player.wingcolor = 45 ~ 55
	result += pack_user_byte(user, "job") #職業
	result += pack_user_int(user, "map_id") #マップ
	result += pack_user_byte(user, "lv_base") #レベル
	result += pack_user_byte(user, "lv_job1") #1次職レベル
	result += general.pack_byte(len(user.player)) #残りクエスト数
	for player in user.player:
		result += general.pack_short((player and 3 or 0))
	result += pack_user_byte(user, "lv_job2x") #2次職レベル
	result += pack_user_byte(user, "lv_job2t") #2.5次職レベル
	result += pack_user_byte(user, "lv_job3") #3次職レベル
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
	"""装備情報 IDのキャラの見た目を変更"""
	result = general.pack_int(player.id)
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
	result += general.pack_int((item_head and
			item_head.type == "HELM" and
			item_head.item_id or 0))
	#頭アクセサリ
	result += general.pack_int((item_head and
			item_head.type == "ACCESORY_HEAD" and
			item_head.item_id or 0))
	#顔
	result += general.pack_int((item_face and
			item_face.type == "FULLFACE" and
			item_face.item_id or 0))
	#顔アクセサリ
	result += general.pack_int((item_face and
			item_face.type == "ACCESORY_FACE" and
			item_face.item_id or 0))
	#胸アクセサリ
	result += general.pack_int((item_chestacce and
			item_chestacce.type in general.ACCESORY_TYPE_LIST and
			item_chestacce.item_id or 0))
	#上半身+下半身
	if item_tops and item_tops.type == "ONEPIECE":
		result += general.pack_int(item_tops.item_id)
		result += general.pack_int(0)
	else:
		result += general.pack_int((item_tops and
				item_tops.type in general.UPPER_TYPE_LIST and
				item_tops.item_id or 0))
		result += general.pack_int((item_buttoms and
				item_buttoms.type in general.LOWER_TYPE_LIST and
				item_buttoms.item_id or 0))
	#背中
	result += general.pack_int((item_backpack and
			item_backpack.type == "BACKPACK" and
			item_backpack.item_id or 0))
	#右手装備
	result += general.pack_int((item_right and
			item_right.type in general.RIGHT_TYPE_LIST and
			item_right.item_id or 0))
	#左手装備
	result += general.pack_int((item_left and
			item_left.type in general.LEFT_TYPE_LIST and
			item_left.item_id or 0))
	#靴
	result += general.pack_int((item_shoes and
			item_shoes.type in general.BOOTS_TYPE_LIST and
			item_shoes.item_id or 0))
	#靴下
	result += general.pack_int((item_sock and
			item_sock.type == "SOCKS" and
			item_sock.item_id or 0))
	#ペット
	result += general.pack_int((item_pet and
			item_pet.type in general.PET_TYPE_LIST and
			item_pet.item_id or 0))
	result += "\x03"+"\x00\x00\x00" #左手モーションタイプ size=3 (片手, 両手, 攻撃)
	result += "\x03"+"\x00\x00\x00" #右手モーションタイプ size=3 #chr_act_tbl.csvを参照する
	result += "\x03"+"\x00\x00\x00" #乗り物モーションタイプ size=3
	result += general.pack_int(0) #乗り物アイテムID
	result += general.pack_byte(0) #乗り物の染色値
	result += general.pack_byte(0) #戦闘状態の時1#0fa6で変更要請#0fa7で変更される
	return result

def make_0029(user):
	"""4キャラクターの装備"""
	result = ""
	for player in user.player:
		if player:
			result += "\x0d"+make_09e9(player)[5:5+13*4]
		else:
			result += "\x0d"+general.pack_int(0)*13
	return result

def make_1239(player, speed=None):
	"""キャラ速度通知・変更"""
	result = general.pack_int(player.id)
	if speed != None:
		general.pack_short(speed)
	else:
		general.pack_short(player.status.speed)
	return result

def make_0fa7(player, mode=0x02):
	"""キャラのモード変更"""
	result = general.pack_int(player.id)
	result += general.pack_int(mode) #通常 00000002
	result += general.pack_int(0)
	return result

def make_1a5f():
	"""右クリ設定"""
	return general.pack_int(0)

def make_0203(item, iid, part):
	"""インベントリ情報"""
	result = general.pack_byte(0) #unknown #常に0
	result += "\xd6" #データサイズ
	result += general.pack_int(iid) #インベントリID
	result += general.pack_int(item.item_id) #アイテムID
	result += general.pack_int(0) #見た目,フィギュア,スケッチ情報
	result += general.pack_byte(part) #アイテムの場所
	result += general.pack_int(0x01) #鑑定済み:0x01 カードロック？:0x20
	result += general.pack_short(item.durability_max) #耐久度
	result += general.pack_short(item.durability_max) #最大耐久度or最大親密度
	result += general.pack_short(0) #強化回数
	result += general.pack_short(0) #カードスロット数
	result += general.pack_int(0) #カードID1
	result += general.pack_int(0) #カードID2
	result += general.pack_int(0) #カードID3
	result += general.pack_int(0) #カードID4
	result += general.pack_int(0) #カードID5
	result += general.pack_int(0) #カードID6
	result += general.pack_int(0) #カードID7
	result += general.pack_int(0) #カードID8
	result += general.pack_int(0) #カードID9
	result += general.pack_int(0) #カードID10
	result += general.pack_byte(0) #染色
	result += general.pack_short(item.count) #個数
	result += general.pack_int(item.price) #ゴーレム販売価格
	result += general.pack_short(0) #ゴーレム販売個数
	result += general.pack_short(0) #憑依重量
	result += general.pack_short(0) #最大重量
	result += general.pack_short(0) #最大容量
	result += general.pack_short(0) #位置的に発動Skill？
	result += general.pack_short(0) #使用可能Skill
	result += general.pack_short(0) #位置的にパッシブスキル？
	result += general.pack_short(0) #位置的に憑依時可能Skill？
	result += general.pack_short(0) #位置的に憑依パッシブSkill？
	result += general.pack_short(item.str) #str
	result += general.pack_short(item.mag) #mag
	result += general.pack_short(item.vit) #vit
	result += general.pack_short(item.dex) #dex
	result += general.pack_short(item.agi) #agi
	result += general.pack_short(item.int) #int
	result += general.pack_short(item.luk) #luk （ペットの場合現在HP
	result += general.pack_short(item.cha) #cha（ペットの場合転生回数
	result += general.pack_short(item.hp) #HP（使用出来るアイテムは回復
	result += general.pack_short(item.sp) #SP（同上
	result += general.pack_short(item.mp) #MP（同上
	result += general.pack_short(item.speed) #移動速度
	result += general.pack_short(item.atk1) #物理攻撃力(叩)
	result += general.pack_short(item.atk2) #物理攻撃力(斬)
	result += general.pack_short(item.atk3) #物理攻撃力(突)
	result += general.pack_short(item.matk) #魔法攻撃力
	result += general.pack_short(item.DEF) #物理防御
	result += general.pack_short(item.mdef) #魔法防御
	result += general.pack_short(item.s_hit) #近命中力
	result += general.pack_short(item.l_hit) #遠命中力
	result += general.pack_short(item.magic_hit) #魔命中力
	result += general.pack_short(item.s_avoid) #近回避
	result += general.pack_short(item.l_avoid) #遠回避
	result += general.pack_short(item.magic_avoid) #魔回避
	result += general.pack_short(item.critical_hit) #クリティカル
	result += general.pack_short(item.critical_avoid) #クリティカル回避
	result += general.pack_short(item.heal_hp) #回復力？
	result += general.pack_short(item.heal_mp) #魔法回復力？
	result += general.pack_short(0) #スタミナ回復力？
	result += general.pack_short(item.energy) #無属性？
	result += general.pack_short(item.fire) #火属性
	result += general.pack_short(item.water) #水属性
	result += general.pack_short(item.wind) #風属性
	result += general.pack_short(item.earth) #地属性
	result += general.pack_short(item.light) #光属性
	result += general.pack_short(item.dark) #闇属性
	result += general.pack_short(item.poison) #毒（+なら毒回復、−なら毒状態に
	result += general.pack_short(item.stone) #石化
	result += general.pack_short(item.paralyze) #麻痺
	result += general.pack_short(item.sleep) #睡眠
	result += general.pack_short(item.silence) #沈黙
	result += general.pack_short(item.slow) #鈍足
	result += general.pack_short(item.confuse) #混乱
	result += general.pack_short(item.freeze) #凍結
	result += general.pack_short(item.stan) #気絶
	result += general.pack_short(0) #ペットステ（攻撃速度
	result += general.pack_short(0) #ペットステ（詠唱速度
	result += general.pack_short(0) #ペットステ？（スタミナ回復力？
	result += general.pack_int(item.price) #ゴーレム露店の買取価格
	result += general.pack_short(0) #ゴーレム露店の買取個数
	result += general.pack_int(item.price) #商人露店の販売価格
	result += general.pack_short(0) #商人露店の販売個数
	result += general.pack_int(0) #何かの価格？ 商人露店の買取価格の予約？
	result += general.pack_short(0) #何かの個数？
	result += general.pack_short(1) #unknow
	result += general.pack_byte(1) #unknow
	result += general.pack_short(0) #unknow
	result += general.pack_int(-1) #unknow
	result += general.pack_byte(0) #unknow
	return result

def make_01ff(player):
	"""自分のキャラクター情報"""
	result = general.pack_int(player.id)
	result += general.pack_int(player.id) #固有ID
	result += general.pack_str(player.name) #名前
	result += general.pack_byte(player.race) #種族
	result += general.pack_byte(player.form) #フォーム
	result += general.pack_byte(player.gender) #性別
	result += general.pack_short(player.hair) #髪型
	result += general.pack_byte(player.haircolor) #髪色
	result += general.pack_short(player.wig) #ウィング
	result += "\xff" #不明
	result += general.pack_short(player.face) #顔
	result += general.pack_byte(player.base_lv) #転生前のレベル
	result += general.pack_byte(player.ex) #転生特典
	result += general.pack_byte(player.wing) #転生翼
	result += general.pack_byte(player.wingcolor) #転生翼色
	result += general.pack_int(player.map_id) #マップ
	result += general.pack_byte(player.x)
	result += general.pack_byte(player.y)
	result += general.pack_byte(player.dir)
	result += general.pack_int(player.status.hp)
	result += general.pack_int(player.status.maxhp)
	result += general.pack_int(player.status.mp)
	result += general.pack_int(player.status.maxmp)
	result += general.pack_int(player.status.sp)
	result += general.pack_int(player.status.maxsp)
	result += general.pack_int(player.status.ep)
	result += general.pack_int(player.status.maxep)
	result += general.pack_short(9) #不明
	result += "\x08" #ステータス数#常に0x08
	result += general.pack_short(player.str) #str
	result += general.pack_short(player.dex) #dex
	result += general.pack_short(player.int) #int
	result += general.pack_short(player.vit) #vit
	result += general.pack_short(player.agi) #agi
	result += general.pack_short(player.mag) #mag
	result += general.pack_short(0) #luk
	result += general.pack_short(0) #cha
	result += "\x14" #equip_len?
	result += general.pack_short(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(-1) #憑依対象サーバーキャラID
	result += general.pack_byte(0) #憑依場所 ( r177b等も参照
	result += general.pack_int(player.gold) #所持金
	result += make_09e9(player)[4:] #装備の\x0dから乗り物の染色値まで
	result += general.pack_byte(1) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(2) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #不明
	result += general.pack_int(0) #unknow
	result += general.pack_int(0) #unknow
	result += general.pack_short(1) #不明
	return result

def make_03f2(msg_id):
	"""システムメッセージ""" #msg_id 0x04: 構えが「叩き」に変更されました
	return general.pack_short(msg_id)

def make_09ec(player):
	"""ゴールドを更新する、値は更新後の値"""
	return general.pack_int(player.gold)

def make_0221(player):
	"""最大HP/MP/SP"""
	result = general.pack_int(player.id)
	result += "\x04"
	result += general.pack_int(player.status.maxhp)
	result += general.pack_int(player.status.maxmp)
	result += general.pack_int(player.status.maxsp)
	result += general.pack_int(player.status.maxep)
	return result

def make_021c(player):
	"""現在のHP/MP/SP/EP"""
	result = general.pack_int(player.id)
	result += "\x04"
	result += general.pack_int(player.status.hp)
	result += general.pack_int(player.status.mp)
	result += general.pack_int(player.status.sp)
	result += general.pack_int(player.status.ep)
	return result

def make_0212(player):
	"""ステータス・補正・ボーナスポイント"""
	result = "\x08" #base
	result += general.pack_short(player.str) #str
	result += general.pack_short(player.dex) #dex
	result += general.pack_short(player.int) #int
	result += general.pack_short(player.vit) #vit
	result += general.pack_short(player.agi) #agi
	result += general.pack_short(player.mag) #mag
	result += general.pack_short(0) #luk
	result += general.pack_short(0) #cha
	result += "\x08" #revise
	result += general.pack_short(player.stradd) #str
	result += general.pack_short(player.dexadd) #dex
	result += general.pack_short(player.intadd) #int
	result += general.pack_short(player.vitadd) #vit
	result += general.pack_short(player.agiadd) #agi
	result += general.pack_short(player.magadd) #mag
	result += general.pack_short(0) #luk
	result += general.pack_short(0) #cha
	result += "\x08" #bounus
	result += general.pack_short(0) #str
	result += general.pack_short(0) #dex
	result += general.pack_short(0) #int
	result += general.pack_short(0) #vit
	result += general.pack_short(0) #agi
	result += general.pack_short(0) #mag
	result += general.pack_short(0) #luk
	result += general.pack_short(0) #cha
	return result

def make_0217(player):
	"""詳細ステータス"""
	result = "\x1e" #30
	result += general.pack_short(player.status.speed) #歩く速度
	result += general.pack_short(player.status.minatk1) #最小ATK1
	result += general.pack_short(player.status.minatk2) #最小ATK2
	result += general.pack_short(player.status.minatk3) #最小ATK3
	result += general.pack_short(player.status.maxatk1) #最大ATK1
	result += general.pack_short(player.status.maxatk2) #最大ATK2
	result += general.pack_short(player.status.maxatk3) #最大ATK3
	result += general.pack_short(player.status.minmatk) #最小MATK
	result += general.pack_short(player.status.maxmatk) #最大MATK
	result += general.pack_short(player.status.leftdef) #基本DEF
	result += general.pack_short(player.status.rightdef) #追加DEF
	result += general.pack_short(player.status.leftmdef) #基本MDEF
	result += general.pack_short(player.status.rightmdef) #追加MDEF
	result += general.pack_short(player.status.shit) #S.HIT(近距離命中率)
	result += general.pack_short(player.status.lhit) #L.HIT(遠距離命中率)
	result += general.pack_short(player.status.mhit) #魔法命中
	result += general.pack_short(player.status.chit) #クリティカル命中
	result += general.pack_short(player.status.savoid) #S.AVOID(近距離回避力)
	result += general.pack_short(player.status.lavoid) #L.AVOID(遠距離回避力)
	result += general.pack_short(0) #魔法回避力
	result += general.pack_short(player.status.hpheal) #HP回復率
	result += general.pack_short(player.status.mpheal) #MP回復率
	result += general.pack_short(player.status.spheal) #SP回復率
	result += general.pack_short(0) #不明
	result += general.pack_short(player.status.aspd) #A.SPD(攻撃速度)
	result += general.pack_short(player.status.cspd) #C.SPD(詠唱速度)
	result += general.pack_short(0) #不明
	result += general.pack_short(0) #不明
	result += general.pack_short(0) #不明
	result += general.pack_short(0) #不明
	return result

def make_0230(player):
	"""現在CAPA/PAYL"""
	result = "\x04"
	result += general.pack_int(player.status.capa) #CAPA(x0.1)
	result += general.pack_int(player.status.rightcapa) #右手かばんCAPA(x0.1)
	result += general.pack_int(player.status.leftcapa) #左手かばんCAPA(x0.1)
	result += general.pack_int(player.status.backcapa) #背中CAPA(x0.1)
	result += "\x04"
	result += general.pack_int(player.status.payl) #PAYL(x0.1)
	result += general.pack_int(player.status.rightpayl) #右手かばんPAYL(x0.1)
	result += general.pack_int(player.status.leftpayl) #左手かばんPAYL(x0.1)
	result += general.pack_int(player.status.backpayl) #背中PAYL(x0.1)
	return result

def make_0231(player):
	"""最大CAPA/PAYL"""
	result = "\x04"
	result += general.pack_int(player.status.maxcapa) #CAPA(x0.1)
	result += general.pack_int(player.status.maxrightcapa) #右手かばんCAPA(x0.1)
	result += general.pack_int(player.status.maxleftcapa) #左手かばんCAPA(x0.1)
	result += general.pack_int(player.status.maxbackcapa) #背中CAPA(x0.1)
	result += "\x04"
	result += general.pack_int(player.status.maxpayl) #PAYL(x0.1)
	result += general.pack_int(player.status.maxrightpayl) #右手かばんPAYL(x0.1)
	result += general.pack_int(player.status.maxleftpayl) #左手かばんPAYL(x0.1)
	result += general.pack_int(player.status.maxbackpayl) #背中PAYL(x0.1)
	return result

def make_0244(player):
	"""ステータスウィンドウの職業"""
	result = general.pack_int(player.job) #職業ID
	result += general.pack_int(0) #ジョイントジョブID
	return result

def make_0226(player, job):
	"""スキル一覧"""
	result = ""
	if job == 0:
		skill_list_length = general.pack_byte(len(player.skill_list))
		result += skill_list_length #スキルID
		for skill_id in player.skill_list:
			result += general.pack_short(skill_id)
		result += skill_list_length #習得Lv
		for skill_id in player.skill_list:
			result += general.pack_short(db.skill[skill_id].maxlv)
		result += skill_list_length #不明
		for skill_id in player.skill_list:
			result += general.pack_short(0)
		result += skill_list_length #習得可能Lv
		for skill_id in player.skill_list:
			result += general.pack_short(1)
	else:
		skill_list_length = general.pack_byte(0)
		result += skill_list_length #スキルID
		result += skill_list_length #習得Lv
		result += skill_list_length #不明
		result += skill_list_length #習得可能Lv
	result += general.pack_byte(job) #一次職0 エキスパ1 etc...
	result += skill_list_length #習得スキル数 #TODO#レベル０のスキルを計算から外す
	return result

def make_022e(player):
	"""リザーブスキル"""
	return general.pack_short(0)

def make_023a(player):
	"""Lv JobLv ボーナスポイント スキルポイント"""
	result = general.pack_byte(player.lv_base) #Lv
	result += general.pack_byte(player.lv_job1) #JobLv(1次職)
	result += general.pack_byte(player.lv_job2x) #JobLv(エキスパート)
	result += general.pack_byte(player.lv_job2t) #JobLv(テクニカル)
	result += general.pack_byte(player.lv_job3) #三次職のレベル？
	result += general.pack_byte(1) #JobLv(ジョイント？ブリーダー？)
	result += general.pack_short(1) #ボーナスポイント
	result += general.pack_short(3) #スキルポイント(1次職)
	result += general.pack_short(0) #スキルポイント(エキスパート)
	result += general.pack_short(0) #スキルポイント(テクニカル)
	result += general.pack_short(0) #三次職のポイント？
	return result

def make_0235(player):
	"""EXP/JOBEXP"""
	result = general.pack_int(0) #EXP(x0.1%)
	result += general.pack_int(0) #JobEXP(x0.1%)
	result += general.pack_int(0) #WarRecodePoint
	result += general.pack_int(0) #ecoin
	result += "\x00\x00\x00\x00\x00\x00\x00\x00" #baseexp #signed long
	result += "\x00\x00\x00\x00\x00\x00\x00\x00" #jobexp #signed long
	return result

def make_1f72(show=False):
	"""もてなしタイニーアイコン""" #before login
	return general.pack_byte((show and 1 or 0))

def make_157c(player,
			state01=0, state02=0, state03=0,
			state04=0, state05=0, state06=0,
			state07=0, state08=0, state09=0):
	"""キャラの状態""" #send when loading map and after load
	#キャラの自然回復や状態異常等、様々な状態を更新する
	#状態に応じて画面上にアイコンが出る
	#毒などの場合エフェクトも出る
	result = general.pack_int(player.id)
	result += general.pack_int(state01)
	result += general.pack_int(state02)
	result += general.pack_int(state03)
	result += general.pack_int(state04)
	result += general.pack_int(state05)
	result += general.pack_int(state06)
	result += general.pack_int(state07)
	result += general.pack_int(state08)
	result += general.pack_int(state09)
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
	result += general.pack_short(0) #新生属性？
	result += general.pack_short(0) #火
	result += general.pack_short(0) #水
	result += general.pack_short(0) #風
	result += general.pack_short(0) #土
	result += general.pack_short(0) #光
	result += general.pack_short(0) #闇
	result += "\x07" #防御
	result += general.pack_short(0) #新生属性？
	result += general.pack_short(0) #火
	result += general.pack_short(0) #水
	result += general.pack_short(0) #風
	result += general.pack_short(0) #土
	result += general.pack_short(0) #光
	result += general.pack_short(0) #闇
	return result

def make_122a(mob_id_list=()):
	"""モンスターID通知""" #send when loading map and after load and make mob
	if not mob_id_list:
		return "\x00"
	else:
		result = general.pack_byte(40)
		for mob_id in mob_id_list:
			result += general.pack_int(mob_id)
		result += general.pack_int(0)*(40-len(mob_id_list))
	return result

def make_1bbc():
	"""スタンプ帳詳細""" #send when loading map
	result = "\x0b" #ジャンル数 常に0b
	result += general.pack_short(0) #スペシャル
	result += general.pack_short(0) #プルル
	result += general.pack_short(0) #平原
	result += general.pack_short(0) #海岸
	result += general.pack_short(0) #荒野
	result += general.pack_short(0) #大陸ダンジョン
	result += general.pack_short(0) #雪国
	result += general.pack_short(0) #廃炭鉱ダンジョン
	result += general.pack_short(0) #ノーザンダンジョン
	result += general.pack_short(0) #アイアンサウス
	result += general.pack_short(0) #サウスダンジョン
	return result

def make_025d():
	"""不明""" #send when loading map
	return "\x00" #不明

def make_0695():
	"""不明""" #send when loading map
	return "\x00\x00\x00\x02\x00" #不明

def make_0236(player):
	"""wrp ranking""" #send when loading map
	result = general.pack_int(0)
	result += general.pack_int(player.wrprank) #wrpの順位
	return result

def make_1b67(player):
	"""マップ情報完了通知
	MAPログイン時に基本情報を全て受信した後に受信される"""
	result = general.pack_int(player.id)
	result += general.pack_byte(0) #unknow
	return result

def make_196e(player):
	"""クエスト回数・時間"""
	result = general.pack_short(3) #残り数
	result += general.pack_int(1) #何時間後に3追加されるか
	result += general.pack_int(0) #不明#常に0？
	return result

def make_0259(player):
	"""ステータス試算結果"""
	result = make_0217(player) #詳細ステータス
	result += "\x03" #03固定 #次のdwordの数？
	result += general.pack_int(player.status.maxhp) #最大hp
	result += general.pack_int(player.status.maxmp) #最大mp
	result += general.pack_int(player.status.maxsp) #最大sp
	result += general.pack_short(player.status.maxcapa) #最大Capa
	result += general.pack_short(player.status.maxpayl) #最大payload
	return result

def make_120c(player):
	"""他キャラ情報/他キャラの憑依やHP等の情報"""
	result = general.pack_int(player.id) #サーバキャラID
	result += general.pack_byte(player.x) #x
	result += general.pack_byte(player.y) #y
	result += general.pack_short(player.status.speed) #キャラの足の早さ
	result += general.pack_byte(player.dir) #向き
	result += general.pack_int(-1) #憑依先のキャラID。（未憑依時:0xFFFFFFFF
	result += general.pack_byte(-1) #憑依箇所。(0:右手 1:左手 2:胸 3:鎧) (未憑依:FF)
	result += general.pack_int(player.status.hp) #現在HP
	result += general.pack_int(player.status.maxhp) #最大HP
	return result

def make_122f(pet):
	"""pet info"""
	result = general.pack_int(pet.id)
	result += "\x03" #unknow
	result += general.pack_int(pet.master.id)
	result += general.pack_int(pet.master.id)
	result += general.pack_byte(pet.master.lv_base)
	result += general.pack_int(pet.master.wrprank) #master wrprank
	result += "\x00" #unknow
	result += general.pack_byte(pet.x) #pet x
	result += general.pack_byte(pet.y) #pet y
	result += general.pack_short(pet.speed) #pet speed
	result += general.pack_byte(pet.dir) #pet dir
	result += general.pack_int(pet.hp) #pet hp
	result += general.pack_int(pet.maxhp) #pet maxhp
	return result

def make_1220(monster):
	"""モンスター情報"""
	result = general.pack_int(monster.id) #server id
	result += general.pack_int(monster.monster_id) #mobid
	result += general.pack_byte(monster.x) #x
	result += general.pack_byte(monster.y) #y
	result += general.pack_short(monster.speed) #speed
	result += general.pack_byte(monster.dir) #dir
	result += general.pack_int(monster.hp) #hp
	result += general.pack_int(monster.maxhp) #maxhp
	return result

def make_00dd(player):
	"""フレンドリスト(自キャラ)"""
	result = "\x01"#現在の状態
	#0-12:オフライン、オンライン、募集中、取り込み中、
	#お話し中、休憩中、退席中、戦闘中、商売中、憑依中、
	#クエスト中、お祭り中、連絡求む
	result += "\x01"+"\x00"#コメント
	return result

def make_0fa6(player):
	"""戦闘状態変更通知"""
	result = general.pack_int(player.id)
	result += general.pack_byte(player.battlestatus) #00: 通常状態 01: 戦闘状態
	return result

def make_121c(player):
	"""モーション通知"""
	result = general.pack_int(player.id) #サーバキャラID
	result += general.pack_short(player.motion_id) #モーションID
	result += general.pack_byte(player.motion_loop) #ループさせるかどうか
	result += general.pack_byte(0) #不明
	return result

def make_1211(player):
	"""PC消去"""
	return general.pack_int(player.id)

def make_11f9(player, move_type=7):
	"""キャラ移動アナウンス"""
	result = general.pack_int(player.id) #server id
	result += general.pack_short(player.rawx) #raw x
	result += general.pack_short(player.rawy) #raw y
	result += general.pack_short(player.rawdir) #raw dir
	result += general.pack_short(move_type) #type
	#move_type
	#0001: 向き変更のみ
	#0006: 歩き
	#0007: 走り
	#0008: 強制移動(ノックバック) (グローブ等)
	#0014: ワープ(ソーサラースキル・テレポート等)
	return result

def make_020e(player):
	"""キャラ情報"""
	result = general.pack_int(player.id)
	result += general.pack_int(player.id)
	result += general.pack_str(player.name)
	result += general.pack_byte(player.race) #種族
	result += general.pack_byte(player.form) #フォーム
	result += general.pack_byte(player.gender) #性別
	result += general.pack_short(player.hair) #髪型
	result += general.pack_byte(player.haircolor) #髪色
	result += general.pack_short(player.wig) #ウィング
	result += general.pack_byte(-1) #不明
	result += general.pack_short(player.face) #顔
	result += general.pack_byte(player.base_lv) #転生前のレベル
	result += general.pack_byte(player.ex) #転生特典
	result += general.pack_byte(player.wing) #転生翼
	result += general.pack_byte(player.wingcolor) #転生翼色
	result += make_09e9(player)[4:] #装備情報 IDのキャラの見た目を変更
	result += general.pack_str("") #パーティー名
	result += general.pack_byte(1) #パーティーリーダーor未所属なら1、それ以外は0
	result += general.pack_int(0) #リングID #変更時はr1ad1
	result += general.pack_str("") #リング名
	result += general.pack_byte(1) #1:リンマスorリングに入ってない 0:リングメンバ
	result += general.pack_str("") #看板
	result += general.pack_str("") #露店看板
	result += general.pack_byte(0) #プレイヤー露店かどうか
	result += general.pack_int(1000) #chara size (1000が標準
	result += general.pack_short(player.motion_id) #モーション#ただし座り(135)や移動や
										#武器・騎乗ペットによるモーションの場合0
	result += general.pack_int(0) #不明
	result += general.pack_int(2) #2 r0fa7参照
	result += general.pack_int(0) #0 r0fa7参照
	result += general.pack_byte(0) #演習時のエンブレムとか#1東2西4南8北Aヒーロー状態
	result += general.pack_byte(0) #メタモーバトルのチーム#1花2岩
	result += general.pack_byte(0) #1にすると/joyのモーションを取る
							#（マリオネット変身時。）2にすると〜
	result += general.pack_byte(0) #不明
	result += general.pack_byte(0) #ゲストIDかどうか
	result += general.pack_byte(player.lv_base) #レベル（ペットは1固定
	result += general.pack_int(player.wrprank) #WRP順位（ペットは -1固定。
									#別のパケで主人の値が送られてくる
	result += general.pack_int(0) #不明
	result += general.pack_byte(-1) #不明
	return result

def make_041b(player):
	"""kanban"""
	result = general.pack_int(player.id)
	result += general.pack_str(player.kanban)
	return result

def make_03e9(speaker_id, message):
	"""オープンチャット・システムメッセージ"""
	result = general.pack_int(speaker_id)
	result += general.pack_str(message)
	#発言者ID
	#-1: システムメッセージ(黄)
	#0: 管理者メッセージ(桃)
	#1-9999: PCユーザー
	#10000-30000: ペット
	#他: 飛空庭設置ペットなど
	return result

def make_05dc():
	"""イベント開始の通知"""
	return ""

def make_05e8(event_id):
	"""EventID通知 Event送信に対する応答"""
	result = general.pack_int(event_id)
	result += general.pack_int(0)
	return result

def make_05dd():
	"""イベント終了の通知"""
	return ""

def make_03f8():
	"""NPCメッセージのヘッダー"""
	return ""

def make_03f9():
	"""NPCメッセージのフッター"""
	return ""

def make_03f7(message, npc_name, npc_motion_id, npc_id, npc_visible=True):
	"""NPCメッセージ"""
	result = general.pack_int(npc_id)
	result += general.pack_byte(0) #unknow
	result += general.pack_byte((npc_visible and 1 or 0)) #npc visible
	result += general.pack_str(message)
	result += general.pack_short(npc_motion_id)
	result += general.pack_str(npc_name)
	return result




