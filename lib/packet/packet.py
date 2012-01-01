#!/usr/bin/env python
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
	for pc in user.pc_list:
		result += pack((pc and getattr(pc, attr) or 0))
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

def make_00a8(pc):
	"""キャラクターマップ通知"""
	return general.pack_int(pc.map_id)

def make_0028(user):
	"""4キャラクターの基本属性"""
	result = general.pack_byte(len(user.pc_list)) #キャラ数
	for pc in user.pc_list:
		result += pc and general.pack_str(pc.name) or "\x00" #名前
	result += pack_user_byte(user, "race") #種族
	result += pack_user_byte(user, "form") #フォーム（DEMの）
	result += pack_user_byte(user, "gender") #性別
	result += pack_user_short(user, "hair") #髪型
	result += pack_user_byte(user, "haircolor") #髪色
	#ウィング #ない時は\xFF\xFF
	result += pack_user_short(user, "wig")
	result += general.pack_byte(len(user.pc_list)) #不明
	for pc in user.pc_list:
		result += general.pack_byte((pc and -1 or 0))
	result += pack_user_short(user, "face") #顔
	#転生前のレベル #付ければ上位種族になる
	result += pack_user_byte(user, "base_lv")
	result += pack_user_byte(user, "ex") #転生特典？
	#if pc.race = 1 than pc.ex = 32 or 111+
	result += pack_user_byte(user, "wing") #転生翼？
	#if pc.race = 1 than pc.wing = 35 ~ 39
	result += pack_user_byte(user, "wingcolor") #転生翼色？
	#if pc.race = 1 than pc.wingcolor = 45 ~ 55
	result += pack_user_byte(user, "job") #職業
	result += pack_user_int(user, "map_id") #マップ
	result += pack_user_byte(user, "lv_base") #レベル
	result += pack_user_byte(user, "lv_job1") #1次職レベル
	result += general.pack_byte(len(user.pc_list)) #残りクエスト数
	for pc in user.pc_list:
		result += general.pack_short((pc and 3 or 0))
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

def make_09e9(pc):
	"""装備情報 IDのキャラの見た目を変更"""
	result = general.pack_int(pc.id)
	result += "\x0d" #装備の数(常に0x0d) #13
	item_head = pc.item.get(pc.equip.head)
	item_face = pc.item.get(pc.equip.face)
	item_chestacce = pc.item.get(pc.equip.chestacce)
	item_tops = pc.item.get(pc.equip.tops)
	item_buttoms = pc.item.get(pc.equip.bottoms)
	item_backpack = pc.item.get(pc.equip.backpack)
	item_right = pc.item.get(pc.equip.right)
	item_left = pc.item.get(pc.equip.left)
	item_shoes = pc.item.get(pc.equip.shoes)
	item_sock = pc.item.get(pc.equip.socks)
	item_pet = pc.item.get(pc.equip.pet)
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
	for pc in user.pc_list:
		if pc:
			result += "\x0d"+make_09e9(pc)[5:5+13*4]
		else:
			result += "\x0d"+general.pack_int(0)*13
	return result

def make_1239(pc, speed=None):
	"""キャラ速度通知・変更"""
	result = general.pack_int(pc.id)
	if speed != None:
		general.pack_short(speed)
	else:
		general.pack_short(pc.status.speed)
	return result

def make_0fa7(pc, mode=0x02):
	"""キャラのモード変更"""
	result = general.pack_int(pc.id)
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

def make_01ff(pc):
	"""自分のキャラクター情報"""
	result = general.pack_int(pc.id)
	result += general.pack_int(pc.id) #固有ID
	result += general.pack_str(pc.name) #名前
	result += general.pack_byte(pc.race) #種族
	result += general.pack_byte(pc.form) #フォーム
	result += general.pack_byte(pc.gender) #性別
	result += general.pack_short(pc.hair) #髪型
	result += general.pack_byte(pc.haircolor) #髪色
	result += general.pack_short(pc.wig) #ウィング
	result += "\xff" #不明
	result += general.pack_short(pc.face) #顔
	result += general.pack_byte(pc.base_lv) #転生前のレベル
	result += general.pack_byte(pc.ex) #転生特典
	result += general.pack_byte(pc.wing) #転生翼
	result += general.pack_byte(pc.wingcolor) #転生翼色
	result += general.pack_int(pc.map_id) #マップ
	result += general.pack_unsigned_byte(pc.x)
	result += general.pack_unsigned_byte(pc.y)
	result += general.pack_byte(pc.dir)
	result += general.pack_int(pc.status.hp)
	result += general.pack_int(pc.status.maxhp)
	result += general.pack_int(pc.status.mp)
	result += general.pack_int(pc.status.maxmp)
	result += general.pack_int(pc.status.sp)
	result += general.pack_int(pc.status.maxsp)
	result += general.pack_int(pc.status.ep)
	result += general.pack_int(pc.status.maxep)
	result += general.pack_short(9) #不明
	result += "\x08" #ステータス数#常に0x08
	result += general.pack_short(pc.str) #str
	result += general.pack_short(pc.dex) #dex
	result += general.pack_short(pc.int) #int
	result += general.pack_short(pc.vit) #vit
	result += general.pack_short(pc.agi) #agi
	result += general.pack_short(pc.mag) #mag
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
	result += general.pack_int(pc.gold) #所持金
	result += make_09e9(pc)[4:] #装備の\x0dから乗り物の染色値まで
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

def make_09ec(pc):
	"""ゴールドを更新する、値は更新後の値"""
	return general.pack_int(pc.gold)

def make_0221(pc):
	"""最大HP/MP/SP"""
	result = general.pack_int(pc.id)
	result += "\x04"
	result += general.pack_int(pc.status.maxhp)
	result += general.pack_int(pc.status.maxmp)
	result += general.pack_int(pc.status.maxsp)
	result += general.pack_int(pc.status.maxep)
	return result

def make_021c(pc):
	"""現在のHP/MP/SP/EP"""
	result = general.pack_int(pc.id)
	result += "\x04"
	result += general.pack_int(pc.status.hp)
	result += general.pack_int(pc.status.mp)
	result += general.pack_int(pc.status.sp)
	result += general.pack_int(pc.status.ep)
	return result

def make_0212(pc):
	"""ステータス・補正・ボーナスポイント"""
	result = "\x08" #base
	result += general.pack_short(pc.str) #str
	result += general.pack_short(pc.dex) #dex
	result += general.pack_short(pc.int) #int
	result += general.pack_short(pc.vit) #vit
	result += general.pack_short(pc.agi) #agi
	result += general.pack_short(pc.mag) #mag
	result += general.pack_short(0) #luk
	result += general.pack_short(0) #cha
	result += "\x08" #revise
	result += general.pack_short(pc.stradd) #str
	result += general.pack_short(pc.dexadd) #dex
	result += general.pack_short(pc.intadd) #int
	result += general.pack_short(pc.vitadd) #vit
	result += general.pack_short(pc.agiadd) #agi
	result += general.pack_short(pc.magadd) #mag
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

def make_0217(pc):
	"""詳細ステータス"""
	result = "\x1e" #30
	result += general.pack_short(pc.status.speed) #歩く速度
	result += general.pack_short(pc.status.minatk1) #最小ATK1
	result += general.pack_short(pc.status.minatk2) #最小ATK2
	result += general.pack_short(pc.status.minatk3) #最小ATK3
	result += general.pack_short(pc.status.maxatk1) #最大ATK1
	result += general.pack_short(pc.status.maxatk2) #最大ATK2
	result += general.pack_short(pc.status.maxatk3) #最大ATK3
	result += general.pack_short(pc.status.minmatk) #最小MATK
	result += general.pack_short(pc.status.maxmatk) #最大MATK
	result += general.pack_short(pc.status.leftdef) #基本DEF
	result += general.pack_short(pc.status.rightdef) #追加DEF
	result += general.pack_short(pc.status.leftmdef) #基本MDEF
	result += general.pack_short(pc.status.rightmdef) #追加MDEF
	result += general.pack_short(pc.status.shit) #S.HIT(近距離命中率)
	result += general.pack_short(pc.status.lhit) #L.HIT(遠距離命中率)
	result += general.pack_short(pc.status.mhit) #魔法命中
	result += general.pack_short(pc.status.chit) #クリティカル命中
	result += general.pack_short(pc.status.savoid) #S.AVOID(近距離回避力)
	result += general.pack_short(pc.status.lavoid) #L.AVOID(遠距離回避力)
	result += general.pack_short(0) #魔法回避力
	result += general.pack_short(pc.status.hpheal) #HP回復率
	result += general.pack_short(pc.status.mpheal) #MP回復率
	result += general.pack_short(pc.status.spheal) #SP回復率
	result += general.pack_short(0) #不明
	result += general.pack_short(pc.status.aspd) #A.SPD(攻撃速度)
	result += general.pack_short(pc.status.cspd) #C.SPD(詠唱速度)
	result += general.pack_short(0) #不明
	result += general.pack_short(0) #不明
	result += general.pack_short(0) #不明
	result += general.pack_short(0) #不明
	return result

def make_0230(pc):
	"""現在CAPA/PAYL"""
	result = "\x04"
	result += general.pack_int(pc.status.capa) #CAPA(x0.1)
	result += general.pack_int(pc.status.rightcapa) #右手かばんCAPA(x0.1)
	result += general.pack_int(pc.status.leftcapa) #左手かばんCAPA(x0.1)
	result += general.pack_int(pc.status.backcapa) #背中CAPA(x0.1)
	result += "\x04"
	result += general.pack_int(pc.status.payl) #PAYL(x0.1)
	result += general.pack_int(pc.status.rightpayl) #右手かばんPAYL(x0.1)
	result += general.pack_int(pc.status.leftpayl) #左手かばんPAYL(x0.1)
	result += general.pack_int(pc.status.backpayl) #背中PAYL(x0.1)
	return result

def make_0231(pc):
	"""最大CAPA/PAYL"""
	result = "\x04"
	result += general.pack_int(pc.status.maxcapa) #CAPA(x0.1)
	result += general.pack_int(pc.status.maxrightcapa) #右手かばんCAPA(x0.1)
	result += general.pack_int(pc.status.maxleftcapa) #左手かばんCAPA(x0.1)
	result += general.pack_int(pc.status.maxbackcapa) #背中CAPA(x0.1)
	result += "\x04"
	result += general.pack_int(pc.status.maxpayl) #PAYL(x0.1)
	result += general.pack_int(pc.status.maxrightpayl) #右手かばんPAYL(x0.1)
	result += general.pack_int(pc.status.maxleftpayl) #左手かばんPAYL(x0.1)
	result += general.pack_int(pc.status.maxbackpayl) #背中PAYL(x0.1)
	return result

def make_0244(pc):
	"""ステータスウィンドウの職業"""
	result = general.pack_int(pc.job) #職業ID
	result += general.pack_int(0) #ジョイントジョブID
	return result

def make_0226(pc, job):
	"""スキル一覧"""
	result = ""
	if job == 0:
		skill_list_length = general.pack_byte(len(pc.skill_list))
		result += skill_list_length #スキルID
		for skill_id in pc.skill_list:
			result += general.pack_short(skill_id)
		result += skill_list_length #習得Lv
		for skill_id in pc.skill_list:
			result += general.pack_short(db.skill[skill_id].maxlv)
		result += skill_list_length #不明
		for skill_id in pc.skill_list:
			result += general.pack_short(0)
		result += skill_list_length #習得可能Lv
		for skill_id in pc.skill_list:
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

def make_022e(pc):
	"""リザーブスキル"""
	return general.pack_short(0)

def make_023a(pc):
	"""Lv JobLv ボーナスポイント スキルポイント"""
	result = general.pack_byte(pc.lv_base) #Lv
	result += general.pack_byte(pc.lv_job1) #JobLv(1次職)
	result += general.pack_byte(pc.lv_job2x) #JobLv(エキスパート)
	result += general.pack_byte(pc.lv_job2t) #JobLv(テクニカル)
	result += general.pack_byte(pc.lv_job3) #三次職のレベル？
	result += general.pack_byte(1) #JobLv(ジョイント？ブリーダー？)
	result += general.pack_short(1) #ボーナスポイント
	result += general.pack_short(3) #スキルポイント(1次職)
	result += general.pack_short(0) #スキルポイント(エキスパート)
	result += general.pack_short(0) #スキルポイント(テクニカル)
	result += general.pack_short(0) #三次職のポイント？
	return result

def make_0235(pc):
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

def make_157c(pc,
			state01=0, state02=0, state03=0,
			state04=0, state05=0, state06=0,
			state07=0, state08=0, state09=0):
	"""キャラの状態""" #send when loading map and after load
	#キャラの自然回復や状態異常等、様々な状態を更新する
	#状態に応じて画面上にアイコンが出る
	#毒などの場合エフェクトも出る
	result = general.pack_int(pc.id)
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

def make_022d(pc):
	"""HEARTスキル""" #send when loading map and after load
	result = "\x03" #スキルの数
	result += "\x27\x74"
	result += "\x27\x75"
	result += "\x27\x76"
	return result

def make_0223(pc):
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

def make_0236(pc):
	"""wrp ranking""" #send when loading map
	result = general.pack_int(0)
	result += general.pack_int(pc.wrprank) #wrpの順位
	return result

def make_1b67(pc):
	"""マップ情報完了通知
	MAPログイン時に基本情報を全て受信した後に受信される"""
	result = general.pack_int(pc.id)
	result += general.pack_byte(0) #unknow
	return result

def make_196e(pc):
	"""クエスト回数・時間"""
	result = general.pack_short(3) #残り数
	result += general.pack_int(1) #何時間後に3追加されるか
	result += general.pack_int(0) #不明#常に0？
	return result

def make_0259(pc):
	"""ステータス試算結果"""
	result = make_0217(pc) #詳細ステータス
	result += "\x03" #03固定 #次のdwordの数？
	result += general.pack_int(pc.status.maxhp) #最大hp
	result += general.pack_int(pc.status.maxmp) #最大mp
	result += general.pack_int(pc.status.maxsp) #最大sp
	result += general.pack_short(pc.status.maxcapa) #最大Capa
	result += general.pack_short(pc.status.maxpayl) #最大payload
	return result

def make_120c(pc):
	"""他キャラ情報/他キャラの憑依やHP等の情報"""
	result = general.pack_int(pc.id) #サーバキャラID
	result += general.pack_unsigned_byte(pc.x) #x
	result += general.pack_unsigned_byte(pc.y) #y
	result += general.pack_short(pc.status.speed) #キャラの足の早さ
	result += general.pack_byte(pc.dir) #向き
	result += general.pack_int(-1) #憑依先のキャラID。（未憑依時:0xFFFFFFFF
	result += general.pack_byte(-1) #憑依箇所。(0:右手 1:左手 2:胸 3:鎧) (未憑依:FF)
	result += general.pack_int(pc.status.hp) #現在HP
	result += general.pack_int(pc.status.maxhp) #最大HP
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
	result += general.pack_unsigned_byte(pet.x) #pet x
	result += general.pack_unsigned_byte(pet.y) #pet y
	result += general.pack_short(pet.speed) #pet speed
	result += general.pack_byte(pet.dir) #pet dir
	result += general.pack_int(pet.hp) #pet hp
	result += general.pack_int(pet.maxhp) #pet maxhp
	return result

def make_1220(monster):
	"""モンスター情報"""
	result = general.pack_int(monster.id) #server id
	result += general.pack_int(monster.monster_id) #mobid
	result += general.pack_unsigned_byte(monster.x) #x
	result += general.pack_unsigned_byte(monster.y) #y
	result += general.pack_short(monster.speed) #speed
	result += general.pack_byte(monster.dir) #dir
	result += general.pack_int(monster.hp) #hp
	result += general.pack_int(monster.maxhp) #maxhp
	return result

def make_00dd(pc):
	"""フレンドリスト(自キャラ)"""
	result = "\x01"#現在の状態
	#0-12:オフライン、オンライン、募集中、取り込み中、
	#お話し中、休憩中、退席中、戦闘中、商売中、憑依中、
	#クエスト中、お祭り中、連絡求む
	result += "\x01"+"\x00"#コメント
	return result

def make_0fa6(pc):
	"""戦闘状態変更通知"""
	result = general.pack_int(pc.id)
	result += general.pack_byte(pc.battlestatus) #00: 通常状態 01: 戦闘状態
	return result

def make_121c(pc):
	"""モーション通知"""
	result = general.pack_int(pc.id) #サーバキャラID
	result += general.pack_short(pc.motion_id) #モーションID
	result += general.pack_byte(pc.motion_loop) #ループさせるかどうか #and 1 or 0
	result += general.pack_byte(0) #不明
	return result

def make_1211(pc):
	"""PC消去"""
	return general.pack_int(pc.id)

def make_11f9(pc, move_type=7):
	"""キャラ移動アナウンス"""
	result = general.pack_int(pc.id) #server id
	result += general.pack_short(pc.rawx) #raw x
	result += general.pack_short(pc.rawy) #raw y
	result += general.pack_short(pc.rawdir) #raw dir
	result += general.pack_short(move_type) #type
	#move_type
	#0001: 向き変更のみ
	#0006: 歩き
	#0007: 走り
	#0008: 強制移動(ノックバック) (グローブ等)
	#0014: ワープ(ソーサラースキル・テレポート等)
	return result

def make_020e(pc):
	"""キャラ情報"""
	result = general.pack_int(pc.id)
	result += general.pack_int(pc.id)
	result += general.pack_str(pc.name)
	result += general.pack_byte(pc.race) #種族
	result += general.pack_byte(pc.form) #フォーム
	result += general.pack_byte(pc.gender) #性別
	result += general.pack_short(pc.hair) #髪型
	result += general.pack_byte(pc.haircolor) #髪色
	result += general.pack_short(pc.wig) #ウィング
	result += general.pack_byte(-1) #不明
	result += general.pack_short(pc.face) #顔
	result += general.pack_byte(pc.base_lv) #転生前のレベル
	result += general.pack_byte(pc.ex) #転生特典
	result += general.pack_byte(pc.wing) #転生翼
	result += general.pack_byte(pc.wingcolor) #転生翼色
	result += make_09e9(pc)[4:] #装備情報 IDのキャラの見た目を変更
	result += general.pack_str("") #パーティー名
	result += general.pack_byte(1) #パーティーリーダーor未所属なら1、それ以外は0
	result += general.pack_int(0) #リングID #変更時はr1ad1
	result += general.pack_str("") #リング名
	result += general.pack_byte(1) #1:リンマスorリングに入ってない 0:リングメンバ
	result += general.pack_str("") #看板
	result += general.pack_str("") #露店看板
	result += general.pack_byte(0) #プレイヤー露店かどうか
	result += general.pack_int(1000) #chara size (1000が標準
	result += general.pack_short(pc.motion_id) #モーション#ただし座り(135)や移動や
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
	result += general.pack_byte(pc.lv_base) #レベル（ペットは1固定
	result += general.pack_int(pc.wrprank) #WRP順位（ペットは -1固定。
									#別のパケで主人の値が送られてくる
	result += general.pack_int(0) #不明
	result += general.pack_byte(-1) #不明
	return result

def make_041b(pc):
	"""kanban"""
	result = general.pack_int(pc.id)
	result += general.pack_str(pc.kanban)
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

def make_09e8(iid, part, _result, r):
	"""アイテム装備"""
	result = general.pack_int(iid) #インベントリID, 装備をはずしたときは-1
	result += general.pack_byte(part) #アイテムの装備先, 装備をはずしたときは-1
	result += general.pack_byte(_result) #通常0, noやpartが-1のとき1
	result += general.pack_int(r) #射程
	return result

def make_09e3(iid, part):
	"""アイテム保管場所変更"""
	result = general.pack_int(iid) #移動元インベントリID
	result += general.pack_byte(0) #成功時は0
	result += general.pack_byte(part) #移動先保管場所(エラー時は-1
	return result

def make_11fd(pc):
	"""マップ変更通知"""
	result = general.pack_int(pc.map_id) #mapid
	result += general.pack_unsigned_byte(pc.x) #x
	result += general.pack_unsigned_byte(pc.y) #y
	result += general.pack_byte(pc.dir) #dir
	result += "\x04" #常に0x04
	result += "\xff" #常に0xff #インスDにおける移動後の部屋の位置x
	result += "\xff" #常に0xff #インスDにおける移動後の部屋の位置y
	result += general.pack_byte(0) #motion
	result += general.pack_int(0) #大体0 #値が入ってるときはかなり大きめの値
	return result

def make_09d4(item, iid, part):
	"""アイテム取得"""
	result = make_0203(item, iid, part)[1:]
	result += general.pack_byte(0) #unknow
	return result

def make_09cf(item, iid):
	"""アイテム個数変化"""
	result = general.pack_int(iid) #インベントリID
	result += general.pack_short(item.count) #変化後の個数
	return result

def make_09ce(iid):
	"""インベントリからアイテム消去"""
	return general.pack_int(iid)

def make_0a0f(name, npc=False):
	"""トレードウィンドウ表示"""
	result = general.pack_str(name) #相手の名前
	result += general.pack_int(npc and 1 or 0) #00だと人間? 01だとNPC?
	return result

def make_0a19(pc):
	"""自分・相手がOKやキャンセルを押した際に双方に送信される"""
	result = general.pack_byte(pc.trade_state) #state1 #自分と相手分?
	result += general.pack_byte(0) #state2 #自分と相手分?
	#state1
	#00:OK押してない状態?
	#FF:OK押した状態?
	#01:トレード完了してる状態?
	#state2
	#00:OK押してない状態?
	#FF:OK押した状態?
	return result

def make_0a1c():
	"""トレード終了通知
	トレードが成立・キャンセルされた場合などに受信"""
	return ""

def make_09f6(warehouse_id, num_here, num_all, num_max):
	"""倉庫インベントリーヘッダ"""
	result = general.pack_int(warehouse_id) #倉庫の場所
	result += general.pack_int(num_here) #開いている倉庫にあるインベントリ数
	result += general.pack_int(num_all) #すべての倉庫にあるインベントリ数
	result += general.pack_int(num_max) #倉庫に入る最大インベントリ数
	#GAME_WARE_NAME_0,";アクロポリスシティ";
	#GAME_WARE_NAME_1,";ファーイースト国境駐在員";
	#GAME_WARE_NAME_2,";アイアンサウス国境駐在員";
	#GAME_WARE_NAME_3,";ノーザン国境駐在員";
	#GAME_WARE_NAME_4,";廃炭鉱キャンプ	";
	#GAME_WARE_NAME_5,";モーグシティ";
	#GAME_WARE_NAME_6,";アイアンサウス連邦";
	#GAME_WARE_NAME_7,";ノーザン王国";
	#GAME_WARE_NAME_8,";トンカシティ";
	#GAME_WARE_NAME_9,";";
	#GAME_WARE_NAME_10,";";
	#GAME_WARE_NAME_11,";";
	#GAME_WARE_NAME_12,";ファーイースト共和国";"""
	return result

def make_09f9(item, iid, part):
	"""倉庫インベントリーデータ"""
	result = make_0203(item, iid, part)[1:]
	#partが30(0x1e)の場合は開いた倉庫に、0の場合は別の倉庫にある。
	result += general.pack_byte(0)
	return result

def make_09fa():
	"""倉庫インベントリーフッタ"""
	return ""

def make_09fc(result_id):
	"""倉庫から取り出した時の結果"""
	#0
	#成功
	#-1〜-8
	#GAME_SMSG_WAREHOUSE_ERR1,";倉庫を開けていません";
	#GAME_SMSG_WAREHOUSE_ERR2,";指定されたアイテムは存在しません";
	#GAME_SMSG_WAREHOUSE_ERR3,";指定された数量が不正です";
	#GAME_SMSG_WAREHOUSE_ERR4,";倉庫のアイテム数が上限を超えてしまうためキャンセルされました";
	#GAME_SMSG_WAREHOUSE_ERR5,";キャラのアイテム数が100個を超えてしまうためキャンセルされました";
	#GAME_SMSG_WAREHOUSE_ERR6,";イベントアイテムは預けられません";
	#GAME_SMSG_WAREHOUSE_ERR7,";指定した格納場所は使用できません";
	#GAME_SMSG_WAREHOUSE_ERR8,";変身中のマリオネットは預ける事ができません";
	#それ以外
	#GAME_SMSG_WAREHOUSE_ERR99,";倉庫移動に失敗しました";
	return general.pack_int(result_id)

def make_09fe(result_id):
	"""倉庫に預けた時の結果"""
	#0
	#成功
	#-1〜-8
	#GAME_SMSG_WAREHOUSE_ERR1,";倉庫を開けていません";
	#GAME_SMSG_WAREHOUSE_ERR2,";指定されたアイテムは存在しません";
	#GAME_SMSG_WAREHOUSE_ERR3,";指定された数量が不正です";
	#GAME_SMSG_WAREHOUSE_ERR4,";倉庫のアイテム数が上限を超えてしまうためキャンセルされました";
	#GAME_SMSG_WAREHOUSE_ERR5,";キャラのアイテム数が100個を超えてしまうためキャンセルされました";
	#GAME_SMSG_WAREHOUSE_ERR6,";イベントアイテムは預けられません";
	#GAME_SMSG_WAREHOUSE_ERR7,";指定した格納場所は使用できません";
	#GAME_SMSG_WAREHOUSE_ERR8,";変身中のマリオネットは預ける事ができません";
	#それ以外
	#GAME_SMSG_WAREHOUSE_ERR99,";倉庫移動に失敗しました";
	return general.pack_int(result_id)

def make_0a08(result_id):
	"""搬送結果"""
	#0
	#GAME_SMSG_TRANSPORT_ERR0,";アイテムを搬送しました";
	#-1〜-4
	#GAME_SMSG_TRANSPORT_ERR1,";倉庫を開けていません";
	#GAME_SMSG_TRANSPORT_ERR2,";指定されたアイテムは存在しません";
	#GAME_SMSG_TRANSPORT_ERR3,";指定された数量が不正です";
	#GAME_SMSG_TRANSPORT_ERR4,";倉庫のアイテム数が上限を超えてしまうためキャンセルされました";
	return general.pack_int(result_id)