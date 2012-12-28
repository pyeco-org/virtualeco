#!/usr/bin/env python
# -*- coding: utf-8 -*-
# packet structure reference from
# www22.atpages.jp/ecore/packet/index.cgi
from lib import env
from lib import general
from lib import db
from lib import usermaps
from lib.packet.packet_struct import *

def make(data_type, *args):
	if args and hasattr(args[0], "lock"):
		with args[0].lock:
			data_value = name_map[data_type](*args)
	else:
		data_value = name_map[data_type](*args)
	if data_value is None:
		general.log_error("packet make error:", data_type, args)
		return ""
	packet = pack_short(len(data_value)+2)
	packet += data_type.decode("hex")
	packet += data_value
	return packet

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
	result = pack_int(0)
	#result += pack_str(";")
	#result += pack_int(0)
	result += "\x01\x00"
	result += "\x48\x6e\xb4\x20"
	return result

def make_0020(user, _type):
	"""アカウント認証結果/ログアウト開始/ログアウトキャンセル"""
	if _type == "loginsucess":
		return "\x00\x00\x00\x00"+pack_int(user.user_id)+"\x00\x00\x00\x00"*2
	elif _type == "loginfaild":
		return "\xFF\xFF\xFF\xFE"+pack_int(user.user_id)+"\x00\x00\x00\x00"*2
	elif _type == "isonline":
		return "\xFF\xFF\xFF\xFB"+pack_int(user.user_id)+"\x00\x00\x00\x00"*2
	elif _type == "logoutstart":
		return "\x00"
	elif _type == "logoutcancel":
		return "\xF9"
	else:
		general.log_error("make_0020: type not exist", _type)

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
		general.log_error("make_00a1: type not exist", _type)

def make_00a6(sucess):
	"""キャラクター削除結果"""
	return ("\x00" if sucess else "\x9c")

def make_00a8(pc):
	"""キャラクターマップ通知"""
	return pack_int(pc.map_id)

def make_0028(user):
	"""4キャラクターの基本属性"""
	result = pack_byte(len(user.pc_list)) #キャラ数
	for p in user.pc_list:
		result += pack_str(p.name) if p else "\x00" #名前
	result += pack_user_byte(user, "race") #種族
	result += pack_user_byte(user, "form") #フォーム（DEMの）
	result += pack_user_byte(user, "gender") #性別
	result += pack_user_short(user, "hair") #髪型
	result += pack_user_byte(user, "haircolor") #髪色
	#ウィング #ない時は\xFF\xFF
	result += pack_user_short(user, "wig")
	result += pack_byte(len(user.pc_list)) #不明
	for p in user.pc_list:
		result += pack_byte(-1 if p else 0)
	result += pack_user_short(user, "face") #顔
	#転生前のレベル #付ければ上位種族になる
	result += pack_user_byte(user, "base_lv")
	result += pack_user_byte(user, "ex") #転生特典？
	#if pc.race = 1 than pc.ex = 32 || 111+
	result += pack_user_byte(user, "wing") #転生翼？
	#if pc.race = 1 than pc.wing = 35 ~ 39
	result += pack_user_byte(user, "wingcolor") #転生翼色？
	#if pc.race = 1 than pc.wingcolor = 45 ~ 55
	result += pack_user_byte(user, "job") #職業
	result += pack_user_int(user, "map_id") #マップ
	result += pack_user_byte(user, "lv_base") #レベル
	result += pack_user_byte(user, "lv_job1") #1次職レベル
	result += pack_byte(len(user.pc_list)) #残りクエスト数
	for p in user.pc_list:
		result += pack_short(3 if p else 0)
	result += pack_user_byte(user, "lv_job2x") #2次職レベル
	result += pack_user_byte(user, "lv_job2t") #2.5次職レベル
	result += pack_user_byte(user, "lv_job3") #3次職レベル
	return result

def make_0033(reply_ping=False):
	"""接続先通知要求(ログインサーバ/0032)の応答"""
	if reply_ping:
		result = ""
	else:
		result = "\x01"
		result += pack_str(env.SERVER_BROADCAST_ADDR)
		result += pack_int(env.MAP_SERVER_PORT)
	return result

def make_09e9(pc):
	"""装備情報 IDのキャラの見た目を変更"""
	result = pack_int(pc.id)
	result += "\x0e" #装備の数 #353+ 13->14 (effect)
	item_head = pc.item.get(pc.equip.head)
	item_face = pc.item.get(pc.equip.face)
	item_chestacce = pc.item.get(pc.equip.chestacce)
	item_tops = pc.item.get(pc.equip.tops)
	item_buttoms = pc.item.get(pc.equip.bottoms)
	item_backpack = pc.item.get(pc.equip.backpack)
	item_right = pc.item.get(pc.equip.right)
	item_left = pc.item.get(pc.equip.left)
	item_shoes = pc.item.get(pc.equip.shoes)
	item_socks = pc.item.get(pc.equip.socks)
	item_effect = pc.item.get(pc.equip.effect)
	#item_pet = pc.item.get(pc.equip.pet)
	#左手モーション 片手
	l_s_motion = pack_item_unsigned_byte_attr(
		item_left, "s_motion", general.LEFT_TYPE_LIST
	)
	#左手モーション 両手
	l_d_motion = pack_item_unsigned_byte_attr(
		item_left, "d_motion", general.LEFT_TYPE_LIST
	)
	#右手モーション 片手
	r_s_motion = pack_item_unsigned_byte_attr(
		item_right, "s_motion", general.RIGHT_TYPE_LIST
	)
	#右手モーション 両手
	r_d_motion = pack_item_unsigned_byte_attr(
		item_right, "d_motion", general.RIGHT_TYPE_LIST
	)
	#頭
	result += pack_pict_id(item_head, general.HEAD_TYPE_LIST)
	#頭アクセサリ
	result += pack_pict_id(item_head, general.ACCESORY_HEAD_TYPE_LIST)
	#顔
	result += pack_pict_id(item_face, general.FULLFACE_TYPE_LIST)
	#顔アクセサリ
	result += pack_pict_id(item_face, general.ACCESORY_FACE_TYPE_LIST)
	#胸アクセサリ
	result += pack_pict_id(item_chestacce, general.ACCESORY_TYPE_LIST)
	#上半身+下半身
	if item_tops and item_tops.check_type(general.ONEPIECE_TYPE_LIST):
		result += pack_pict_id(item_tops, None)
		result += pack_int(0)
	else:
		result += pack_pict_id(item_tops, general.UPPER_TYPE_LIST)
		result += pack_pict_id(item_buttoms, general.LOWER_TYPE_LIST)
	#背中
	result += pack_pict_id(item_backpack, general.BACKPACK_TYPE_LIST)
	#右手装備
	result += pack_pict_id(item_right, general.RIGHT_TYPE_LIST)
	#左手装備
	result += pack_pict_id(item_left, general.LEFT_TYPE_LIST)
	#靴
	result += pack_pict_id(item_shoes, general.BOOTS_TYPE_LIST)
	#靴下
	result += pack_pict_id(item_socks, general.SOCKS_TYPE_LIST)
	#ペット
	result += pack_int(0)
	#effect #353+
	result += pack_pict_id(item_effect, general.EFFECT_TYPE_LIST)
	#左手モーションタイプ size=3 (片手, 両手, 攻撃)
	result += "\x03"+l_s_motion+l_d_motion+"\x00"
	#右手モーションタイプ size=3 #chr_act_tbl.csvを参照する
	result += "\x03"+r_s_motion+r_d_motion+"\x00"
	result += "\x03"+"\x00\x00\x00" #乗り物モーションタイプ size=3
	result += pack_int(0) #乗り物アイテムID
	result += pack_byte(0) #乗り物の染色値
	result += pack_byte(0) #戦闘状態の時1#0fa6で変更要請#0fa7で変更される
	return result

def make_0029(user):
	"""4キャラクターの装備"""
	result = ""
	for p in user.pc_list:
		if p:
			result += "\x0d"+make_09e9(p)[5:5+13*4]
		else:
			result += "\x0d"+pack_int(0)*13
	return result

def make_1239(pc, speed=None):
	"""キャラ速度通知・変更"""
	result = pack_int(pc.id)
	result += pack_short(pc.status.speed if speed is None else speed)
	return result

def make_0fa7(pc, mode=0x02):
	"""キャラのモード変更"""
	result = pack_int(pc.id)
	result += pack_int(mode) #通常 00000002
	result += pack_int(0)
	return result

def make_1a5f():
	"""右クリ設定"""
	return pack_int(0)

def make_0203(item, iid, part, count=None):
	"""インベントリ情報"""
	result = pack_byte(0) #unknown #常に0
	result += "\xd6" #データサイズ
	result += pack_int(iid) #インベントリID
	result += pack_unsigned_int(item.item_id) #アイテムID
	result += pack_int(0) #見た目,フィギュア,スケッチ情報
	result += pack_byte(part) #アイテムの場所
	result += pack_int(0x01) #鑑定済み:0x01 カードロック？:0x20
	result += pack_short(item.durability_max) #耐久度
	result += pack_short(item.durability_max) #最大耐久度or最大親密度
	result += pack_short(0) #強化回数
	result += pack_short(0) #カードスロット数
	result += pack_int(0) #カードID1
	result += pack_int(0) #カードID2
	result += pack_int(0) #カードID3
	result += pack_int(0) #カードID4
	result += pack_int(0) #カードID5
	result += pack_int(0) #カードID6
	result += pack_int(0) #カードID7
	result += pack_int(0) #カードID8
	result += pack_int(0) #カードID9
	result += pack_int(0) #カードID10
	result += pack_byte(0) #染色
	result += pack_unsigned_short(count if count != None else item.count) #個数
	result += pack_unsigned_int(item.price) #ゴーレム販売価格
	result += pack_short(0) #ゴーレム販売個数
	result += pack_short(0) #憑依重量
	result += pack_short(0) #最大重量
	result += pack_short(0) #最大容量
	result += pack_short(0) #位置的に発動Skill？
	result += pack_short(0) #使用可能Skill
	result += pack_short(0) #位置的にパッシブスキル？
	result += pack_short(0) #位置的に憑依時可能Skill？
	result += pack_short(0) #位置的に憑依パッシブSkill？
	result += pack_short(item.str) #str
	result += pack_short(item.mag) #mag
	result += pack_short(item.vit) #vit
	result += pack_short(item.dex) #dex
	result += pack_short(item.agi) #agi
	result += pack_short(item.int) #int
	result += pack_short(item.luk) #luk （ペットの場合現在HP
	result += pack_short(item.cha) #cha（ペットの場合転生回数
	result += pack_short(item.hp) #HP（使用出来るアイテムは回復
	result += pack_short(item.sp) #SP（同上
	result += pack_short(item.mp) #MP（同上
	result += pack_short(item.speed) #移動速度
	result += pack_short(item.atk1) #物理攻撃力(叩)
	result += pack_short(item.atk2) #物理攻撃力(斬)
	result += pack_short(item.atk3) #物理攻撃力(突)
	result += pack_short(item.matk) #魔法攻撃力
	result += pack_short(item.DEF) #物理防御
	result += pack_short(item.mdef) #魔法防御
	result += pack_short(item.s_hit) #近命中力
	result += pack_short(item.l_hit) #遠命中力
	result += pack_short(item.magic_hit) #魔命中力
	result += pack_short(item.s_avoid) #近回避
	result += pack_short(item.l_avoid) #遠回避
	result += pack_short(item.magic_avoid) #魔回避
	result += pack_short(item.critical_hit) #クリティカル
	result += pack_short(item.critical_avoid) #クリティカル回避
	result += pack_short(item.heal_hp) #回復力？
	result += pack_short(item.heal_mp) #魔法回復力？
	result += pack_short(0) #スタミナ回復力？
	result += pack_short(item.energy) #無属性？
	result += pack_short(item.fire) #火属性
	result += pack_short(item.water) #水属性
	result += pack_short(item.wind) #風属性
	result += pack_short(item.earth) #地属性
	result += pack_short(item.light) #光属性
	result += pack_short(item.dark) #闇属性
	result += pack_short(item.poison) #毒（+なら毒回復、−なら毒状態に
	result += pack_short(item.stone) #石化
	result += pack_short(item.paralyze) #麻痺
	result += pack_short(item.sleep) #睡眠
	result += pack_short(item.silence) #沈黙
	result += pack_short(item.slow) #鈍足
	result += pack_short(item.confuse) #混乱
	result += pack_short(item.freeze) #凍結
	result += pack_short(item.stan) #気絶
	result += pack_short(0) #ペットステ（攻撃速度
	result += pack_short(0) #ペットステ（詠唱速度
	result += pack_short(0) #ペットステ？（スタミナ回復力？
	result += pack_unsigned_int(item.price) #ゴーレム露店の買取価格
	result += pack_short(0) #ゴーレム露店の買取個数
	result += pack_unsigned_int(item.price) #商人露店の販売価格
	result += pack_short(0) #商人露店の販売個数
	result += pack_int(0) #何かの価格？ 商人露店の買取価格の予約？
	result += pack_short(0) #何かの個数？
	result += pack_short(1) #unknow
	result += pack_byte(1) #unknow
	result += pack_short(0) #unknow
	result += pack_int(-1) #unknow
	result += pack_byte(0) #unknow
	return result

def make_01ff(pc):
	"""自分のキャラクター情報"""
	result = pack_int(pc.id)
	result += pack_int(pc.id) #固有ID
	result += pack_str(pc.name) #名前
	result += pack_byte(pc.race) #種族
	result += pack_byte(pc.form) #フォーム
	result += pack_byte(pc.gender) #性別
	result += pack_short(pc.hair) #髪型
	result += pack_byte(pc.haircolor) #髪色
	result += pack_short(pc.wig) #ウィング
	result += "\xff" #不明
	result += pack_short(pc.face) #顔
	result += pack_byte(pc.base_lv) #転生前のレベル
	result += pack_byte(pc.ex) #転生特典
	result += pack_byte(pc.wing) #転生翼
	result += pack_byte(pc.wingcolor) #転生翼色
	result += pack_int(pc.map_id) #マップ
	result += pack_unsigned_byte(int(pc.x))
	result += pack_unsigned_byte(int(pc.y))
	result += pack_byte(pc.dir)
	result += pack_int(pc.status.hp)
	result += pack_int(pc.status.maxhp)
	result += pack_int(pc.status.mp)
	result += pack_int(pc.status.maxmp)
	result += pack_int(pc.status.sp)
	result += pack_int(pc.status.maxsp)
	result += pack_int(pc.status.ep)
	result += pack_int(pc.status.maxep)
	result += pack_short(9) #不明
	result += "\x08" #ステータス数 #常に0x08
	result += pack_short(pc.str) #str
	result += pack_short(pc.dex) #dex
	result += pack_short(pc.int) #int
	result += pack_short(pc.vit) #vit
	result += pack_short(pc.agi) #agi
	result += pack_short(pc.mag) #mag
	result += pack_short(0) #luk
	result += pack_short(0) #cha
	result += "\x14" #equip_len?
	result += pack_short(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(-1) #憑依対象サーバーキャラID
	result += pack_byte(0) #憑依場所 ( r177b等も参照
	result += pack_int(pc.gold) #所持金
	result += make_09e9(pc)[4:] #装備の\x0dから乗り物の染色値まで
	result += pack_byte(1) #不明
	result += pack_int(0) #不明
	result += pack_int(2) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #不明
	result += pack_int(0) #unknow
	result += pack_int(0) #unknow
	result += pack_short(1) #不明
	return result

def make_03f2(msg_id):
	"""システムメッセージ""" #msg_id 0x04: 構えが「叩き」に変更されました
	return pack_short(msg_id)

def make_09ec(pc):
	"""ゴールドを更新する、値は更新後の値"""
	return pack_int(pc.gold)

def make_0221(pc):
	"""最大HP/MP/SP"""
	result = pack_int(pc.id)
	result += "\x04"
	result += pack_int(pc.status.maxhp)
	result += pack_int(pc.status.maxmp)
	result += pack_int(pc.status.maxsp)
	result += pack_int(pc.status.maxep)
	return result

def make_021c(obj):
	"""現在のHP/MP/SP/EP"""
	result = pack_int(obj.id)
	result += "\x04"
	result += pack_int(obj.status.hp)
	result += pack_int(obj.status.mp)
	result += pack_int(obj.status.sp)
	result += pack_int(obj.status.ep)
	return result

def make_0217(pc):
	"""詳細ステータス"""
	result = "\x1e" #30
	result += pack_short(pc.status.speed) #歩く速度
	result += pack_short(pc.status.minatk1) #最小ATK1
	result += pack_short(pc.status.minatk2) #最小ATK2
	result += pack_short(pc.status.minatk3) #最小ATK3
	result += pack_short(pc.status.maxatk1) #最大ATK1
	result += pack_short(pc.status.maxatk2) #最大ATK2
	result += pack_short(pc.status.maxatk3) #最大ATK3
	result += pack_short(pc.status.minmatk) #最小MATK
	result += pack_short(pc.status.maxmatk) #最大MATK
	result += pack_short(pc.status.leftdef) #基本DEF
	result += pack_short(pc.status.rightdef) #追加DEF
	result += pack_short(pc.status.leftmdef) #基本MDEF
	result += pack_short(pc.status.rightmdef) #追加MDEF
	result += pack_short(pc.status.shit) #S.HIT(近距離命中率)
	result += pack_short(pc.status.lhit) #L.HIT(遠距離命中率)
	result += pack_short(pc.status.mhit) #魔法命中
	result += pack_short(pc.status.chit) #クリティカル命中
	result += pack_short(pc.status.savoid) #S.AVOID(近距離回避力)
	result += pack_short(pc.status.lavoid) #L.AVOID(遠距離回避力)
	result += pack_short(0) #魔法回避力
	result += pack_short(pc.status.hpheal) #HP回復率
	result += pack_short(pc.status.mpheal) #MP回復率
	result += pack_short(pc.status.spheal) #SP回復率
	result += pack_short(0) #不明
	result += pack_short(pc.status.aspd) #A.SPD(攻撃速度)
	result += pack_short(pc.status.cspd) #C.SPD(詠唱速度)
	result += pack_short(0) #不明
	result += pack_short(0) #不明
	result += pack_short(0) #不明
	result += pack_short(0) #不明
	return result

def make_0230(pc):
	"""現在CAPA/PAYL"""
	result = "\x04"
	result += pack_int(int(pc.status.capa*10)) #CAPA(x0.1)
	result += pack_int(int(pc.status.rightcapa*10)) #右手かばんCAPA(x0.1)
	result += pack_int(int(pc.status.leftcapa*10)) #左手かばんCAPA(x0.1)
	result += pack_int(int(pc.status.backcapa*10)) #背中CAPA(x0.1)
	result += "\x04"
	result += pack_int(int(pc.status.payl*10)) #PAYL(x0.1)
	result += pack_int(int(pc.status.rightpayl*10)) #右手かばんPAYL(x0.1)
	result += pack_int(int(pc.status.leftpayl*10)) #左手かばんPAYL(x0.1)
	result += pack_int(int(pc.status.backpayl*10)) #背中PAYL(x0.1)
	return result

def make_0231(pc):
	"""最大CAPA/PAYL"""
	result = "\x04"
	result += pack_int(int(pc.status.maxcapa*10)) #CAPA(x0.1)
	result += pack_int(int(pc.status.maxrightcapa*10)) #右手かばんCAPA(x0.1)
	result += pack_int(int(pc.status.maxleftcapa*10)) #左手かばんCAPA(x0.1)
	result += pack_int(int(pc.status.maxbackcapa*10)) #背中CAPA(x0.1)
	result += "\x04"
	result += pack_int(int(pc.status.maxpayl*10)) #PAYL(x0.1)
	result += pack_int(int(pc.status.maxrightpayl*10)) #右手かばんPAYL(x0.1)
	result += pack_int(int(pc.status.maxleftpayl*10)) #左手かばんPAYL(x0.1)
	result += pack_int(int(pc.status.maxbackpayl*10)) #背中PAYL(x0.1)
	return result

def make_0244(pc):
	"""ステータスウィンドウの職業"""
	result = pack_int(pc.job) #職業ID
	result += pack_int(0) #ジョイントジョブID
	return result

def make_0226(pc, job):
	"""スキル一覧"""
	def get_lv(i):
		s = db.skill.get(i)
		if s is None:
			return 1
		return s.maxlv
	result = ""
	i = 0
	if job == 0:
		i = len(pc.skill_list)
		#スキルID
		result += pack_array(pack_short, pc.skill_list)
		#習得Lv
		result += pack_array(pack_unsigned_byte, (get_lv(i) for i in pc.skill_list))
		#不明
		result += pack_array(pack_unsigned_byte, (0,)*i)
		#習得可能Lv
		result += pack_array(pack_unsigned_byte, (0,)*i)
	else:
		result += pack_array(pack_short, ()) #スキルID
		result += pack_array(pack_unsigned_byte, ()) #習得Lv
		result += pack_array(pack_unsigned_byte, ()) #不明
		result += pack_array(pack_unsigned_byte, ()) #習得可能Lv
	result += pack_byte(job) #一次職0 エキスパ1 etc...
	result += pack_unsigned_byte(i) #習得スキル数
	return result

def make_022e(pc):
	"""リザーブスキル"""
	return pack_short(0)

def make_023a(pc):
	"""Lv JobLv ボーナスポイント スキルポイント"""
	result = pack_byte(pc.lv_base) #Lv
	result += pack_byte(pc.lv_job1) #JobLv(1次職)
	result += pack_byte(pc.lv_job2x) #JobLv(エキスパート)
	result += pack_byte(pc.lv_job2t) #JobLv(テクニカル)
	result += pack_byte(pc.lv_job3) #三次職のレベル？
	result += pack_byte(1) #JobLv(ジョイント？ブリーダー？)
	result += pack_short(1) #ボーナスポイント
	result += pack_short(3) #スキルポイント(1次職)
	result += pack_short(0) #スキルポイント(エキスパート)
	result += pack_short(0) #スキルポイント(テクニカル)
	result += pack_short(0) #三次職のポイント？
	return result

def make_0235(pc):
	"""EXP/JOBEXP"""
	result = pack_int(0) #EXP(x0.1%)
	result += pack_int(0) #JobEXP(x0.1%)
	result += pack_int(0) #WarRecodePoint
	result += pack_int(0) #ecoin
	result += "\x00\x00\x00\x00\x00\x00\x00\x00" #baseexp #signed long
	result += "\x00\x00\x00\x00\x00\x00\x00\x00" #jobexp #signed long
	return result

def make_1f72(show=False):
	"""もてなしタイニーアイコン""" #before login
	return pack_byte(1 if show else 0)

def make_157c(obj,
		state01=0, state02=0, state03=0,
		state04=0, state05=0, state06=0,
		state07=0, state08=0, state09=0):
	#changed from ver353+
	"""キャラの状態""" #send when loading map and after load
	#キャラの自然回復や状態異常等、様々な状態を更新する
	#状態に応じて画面上にアイコンが出る
	#毒などの場合エフェクトも出る
	result = pack_int(obj.id)
	result += pack_int(state01)
	result += pack_int(state02)
	result += pack_int(state03)
	result += pack_int(state04)
	result += pack_int(state05)
	result += pack_int(state06)
	result += pack_int(state07)
	result += pack_int(state08)
	result += pack_int(state09)
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
	result += pack_short(0) #新生属性？
	result += pack_short(0) #火
	result += pack_short(0) #水
	result += pack_short(0) #風
	result += pack_short(0) #土
	result += pack_short(0) #光
	result += pack_short(0) #闇
	result += "\x07" #防御
	result += pack_short(0) #新生属性？
	result += pack_short(0) #火
	result += pack_short(0) #水
	result += pack_short(0) #風
	result += pack_short(0) #土
	result += pack_short(0) #光
	result += pack_short(0) #闇
	return result

def make_122a(mob_id_list=()):
	"""モンスターID通知""" #send when loading map and after load and make mob
	return pack_array(pack_int, mob_id_list) #or fill to 40

def make_1bbc():
	"""スタンプ帳詳細""" #send when loading map
	result = "\x0b" #ジャンル数 常に0b
	result += pack_short(0) #スペシャル
	result += pack_short(0) #プルル
	result += pack_short(0) #平原
	result += pack_short(0) #海岸
	result += pack_short(0) #荒野
	result += pack_short(0) #大陸ダンジョン
	result += pack_short(0) #雪国
	result += pack_short(0) #廃炭鉱ダンジョン
	result += pack_short(0) #ノーザンダンジョン
	result += pack_short(0) #アイアンサウス
	result += pack_short(0) #サウスダンジョン
	return result

def make_025d():
	"""不明""" #send when loading map
	return "\x00" #不明

def make_0695():
	"""不明""" #send when loading map
	return "\x00\x00\x00\x02\x00" #不明

def make_0236(pc):
	"""wrp ranking""" #send when loading map
	result = pack_int(0)
	result += pack_int(pc.wrprank) #wrpの順位
	return result

def make_1b67(pc):
	"""マップ情報完了通知
	MAPログイン時に基本情報を全て受信した後に受信される"""
	result = pack_int(pc.id)
	result += pack_int(0) #unknow ver353+ byte->int
	return result

def make_196e(pc):
	"""クエスト回数・時間"""
	result = pack_short(3) #残り数
	result += pack_int(1) #何時間後に3追加されるか
	result += pack_int(0) #不明#常に0？
	return result

def make_0259(pc):
	"""ステータス試算結果"""
	result = make_0217(pc) #詳細ステータス
	result += "\x03" #03固定 #次のdwordの数？
	result += pack_int(pc.status.maxhp) #最大hp
	result += pack_int(pc.status.maxmp) #最大mp
	result += pack_int(pc.status.maxsp) #最大sp
	result += pack_short(int(pc.status.maxcapa)) #最大Capa
	result += pack_short(int(pc.status.maxpayl)) #最大payload
	return result

def make_120c(pc):
	"""他キャラ情報/他キャラの憑依やHP等の情報"""
	result = pack_int(pc.id) #サーバキャラID
	result += pack_unsigned_byte(int(pc.x)) #x
	result += pack_unsigned_byte(int(pc.y)) #y
	result += pack_short(pc.status.speed) #キャラの足の早さ
	result += pack_byte(pc.dir) #向き
	result += pack_int(-1) #憑依先のキャラID。（未憑依時:0xFFFFFFFF
	result += pack_byte(-1) #憑依箇所。(0:右手 1:左手 2:胸 3:鎧) (未憑依:FF)
	result += pack_int(pc.status.hp) #現在HP
	result += pack_int(pc.status.maxhp) #最大HP
	return result

def make_1220(monster):
	"""モンスター情報"""
	result = pack_int(monster.id) #server id
	result += pack_int(monster.monster_id) #mobid
	result += pack_unsigned_byte(int(monster.x)) #x
	result += pack_unsigned_byte(int(monster.y)) #y
	result += pack_short(monster.status.speed) #speed
	result += pack_byte(monster.dir) #dir
	result += pack_int(monster.status.hp) #hp
	result += pack_int(monster.status.maxhp) #maxhp
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
	result = pack_int(pc.id)
	result += pack_byte(pc.battlestatus) #00: 通常状態 01: 戦闘状態
	return result

def make_121c(pc, npc_id=None, npc_motion_id=None, npc_motion_loop=None):
	"""モーション通知"""
	result = pack_unsigned_int(
		pc.id if npc_id is None else npc_id) #サーバキャラID
	result += pack_unsigned_short(
		pc.motion_id if (npc_motion_id is None) else npc_motion_id) #モーションID
	result += pack_byte(
		pc.motion_loop if (npc_motion_loop is None) else
		(1 if npc_motion_loop else 0)) #ループさせるかどうか
	result += pack_byte(0) #不明
	return result

def make_1211(pc):
	"""PC消去"""
	return pack_int(pc.id)

def make_11f9(pc, move_type=7):
	"""キャラ移動アナウンス"""
	result = pack_int(pc.id) #server id
	result += pack_short(pc.rawx) #raw x
	result += pack_short(pc.rawy) #raw y
	result += pack_short(pc.rawdir) #raw dir
	result += pack_short(move_type) #type
	#move_type
	#0001: 向き変更のみ
	#0006: 歩き
	#0007: 走り
	#0008: 強制移動(ノックバック) (グローブ等)
	#0014: ワープ(ソーサラースキル・テレポート等)
	return result

def make_020b(pc):
	"""キャラ情報"""
	#353+ from 020e to 020b
	result = pack_int(pc.id)
	result += pack_int(pc.id)
	result += pack_str(pc.name)
	result += pack_byte(pc.race) #種族
	result += pack_byte(pc.form) #フォーム
	result += pack_byte(pc.gender) #性別
	result += pack_short(pc.hair) #髪型
	result += pack_byte(pc.haircolor) #髪色
	result += pack_short(pc.wig) #ウィング
	result += pack_byte(-1) #不明
	result += pack_short(pc.face) #顔
	result += pack_byte(pc.base_lv) #転生前のレベル
	result += pack_byte(pc.ex) #転生特典
	result += pack_byte(pc.wing) #転生翼
	result += pack_byte(pc.wingcolor) #転生翼色
	result += make_09e9(pc)[4:] #装備情報 IDのキャラの見た目を変更
	result += pack_str("") #パーティー名
	result += pack_byte(1) #パーティーリーダーor未所属なら1、それ以外は0
	result += pack_int(0) #リングID #変更時はr1ad1
	result += pack_str("") #リング名
	result += pack_byte(1) #1:リンマスorリングに入ってない 0:リングメンバ
	result += pack_str("") #看板
	result += pack_str("") #露店看板
	result += pack_byte(0) #プレイヤー露店かどうか
	result += pack_int(pc.size) #chara size (1000が標準
	result += pack_unsigned_short(pc.motion_id) #モーション#ただし座り(135)や移動や
										#武器・騎乗ペットによるモーションの場合0
	result += pack_int(0) #不明
	result += pack_int(2) #2 r0fa7参照
	result += pack_int(0) #0 r0fa7参照
	result += pack_byte(0) #演習時のエンブレムとか#1東2西4南8北Aヒーロー状態
	result += pack_byte(0) #メタモーバトルのチーム#1花2岩
	result += pack_byte(0) #1にすると/joyのモーションを取る
							#（マリオネット変身時。）2にすると〜
	result += pack_byte(0) #不明
	result += pack_byte(0) #不明 #353+ 演習関係？
	result += pack_byte(0) #不明 #353+ 演習関係？
	result += pack_byte(0) #不明 #353+ 演習関係？
	result += pack_byte(0) #ゲストIDかどうか
	result += pack_byte(pc.lv_base) #レベル（ペットは1固定
	result += pack_int(pc.wrprank) #WRP順位（ペットは -1固定。
									#別のパケで主人の値が送られてくる
	result += pack_int(0) #不明
	result += pack_byte(-1) #不明
	return result

def make_03e9(speaker_id, message):
	"""オープンチャット・システムメッセージ"""
	result = pack_int(speaker_id)
	result += pack_str(message)
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
	result = pack_int(event_id)
	result += pack_int(0)
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
	result = pack_unsigned_int(npc_id)
	result += pack_byte(0) #unknow
	result += pack_byte(1 if npc_visible else 0) #npc visible
	result += pack_str(message)
	result += pack_unsigned_short(npc_motion_id)
	result += pack_str(npc_name)
	return result

def make_09e8(iid, part, _result, r):
	"""アイテム装備"""
	result = pack_int(iid) #インベントリID, 装備をはずしたときは-1
	result += pack_byte(part) #アイテムの装備先, 装備をはずしたときは-1
	result += pack_byte(_result) #通常0, noやpartが-1のとき1
	result += pack_int(r) #射程
	return result

def make_09e3(iid, part):
	"""アイテム保管場所変更"""
	result = pack_int(iid) #移動元インベントリID
	result += pack_byte(0) #成功時は0
	result += pack_byte(part) #移動先保管場所(エラー時は-1
	return result

def make_11fd(pc):
	"""マップ変更通知"""
	result = pack_int(pc.map_id) #mapid
	result += pack_unsigned_byte(int(pc.x)) #x
	result += pack_unsigned_byte(int(pc.y)) #y
	result += pack_byte(pc.dir) #dir
	result += "\x04" #常に0x04
	result += "\xff" #常に0xff #インスDにおける移動後の部屋の位置x
	result += "\xff" #常に0xff #インスDにおける移動後の部屋の位置y
	result += pack_byte(0) #motion
	result += pack_int(0) #大体0 #値が入ってるときはかなり大きめの値
	return result

def make_09d4(item, iid, part):
	"""アイテム取得"""
	result = make_0203(item, iid, part)[1:]
	result += pack_byte(0) #unknow
	return result

def make_09cf(item, iid):
	"""アイテム個数変化"""
	result = pack_int(iid) #インベントリID
	result += pack_unsigned_short(item.count) #変化後の個数
	return result

def make_09ce(iid):
	"""インベントリからアイテム消去"""
	return pack_int(iid)

def make_0a0f(name, npc=False):
	"""トレードウィンドウ表示"""
	result = pack_str(name) #相手の名前
	result += pack_int(1 if npc else 0) #00だと人間? 01だとNPC?
	return result

def make_0a19(pc, p=None):
	"""自分・相手がOKやキャンセルを押した際に双方に送信される"""
	result = pack_byte(pc.trade_state) #state1 #自分と相手分?
	result += pack_byte(p.trade_state if p else 0) #state2 #自分と相手分?
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
	result = pack_int(warehouse_id) #倉庫の場所
	result += pack_int(num_here) #開いている倉庫にあるインベントリ数
	result += pack_int(num_all) #すべての倉庫にあるインベントリ数
	result += pack_int(num_max) #倉庫に入る最大インベントリ数
	#0 アクロポリスシティ
	#1 ファーイースト国境駐在員
	#2 アイアンサウス国境駐在員
	#3 ノーザン国境駐在員
	#4 廃炭鉱キャンプ
	#5 モーグシティ
	#6 アイアンサウス連邦
	#7 ノーザン王国
	#8 トンカシティ
	#9
	#10
	#11
	#12 ファーイースト共和国
	return result

def make_09f9(item, iid, part):
	"""倉庫インベントリーデータ"""
	result = make_0203(item, iid, part)[1:]
	#partが30(0x1e)の場合は開いた倉庫に、0の場合は別の倉庫にある。
	result += pack_byte(0)
	return result

def make_09fa():
	"""倉庫インベントリーフッタ"""
	return ""

def make_09fc(result_id):
	"""倉庫から取り出した時の結果"""
	#0 成功
	#-1 倉庫を開けていません
	#-2 指定されたアイテムは存在しません
	#-3 指定された数量が不正です
	#-4 倉庫のアイテム数が上限を超えてしまうためキャンセルされました
	#-5 キャラのアイテム数が100個を超えてしまうためキャンセルされました
	#-6 イベントアイテムは預けられません
	#-7 指定した格納場所は使用できません
	#-8 変身中のマリオネットは預ける事ができません
	#-99 倉庫移動に失敗しました
	return pack_int(result_id)

def make_09fe(result_id):
	"""倉庫に預けた時の結果"""
	#0 成功
	#-1 倉庫を開けていません
	#-2 指定されたアイテムは存在しません
	#-3 指定された数量が不正です
	#-4 倉庫のアイテム数が上限を超えてしまうためキャンセルされました
	#-5 キャラのアイテム数が100個を超えてしまうためキャンセルされました
	#-6 イベントアイテムは預けられません
	#-7 指定した格納場所は使用できません
	#-8 変身中のマリオネットは預ける事ができません
	#-99 倉庫移動に失敗しました
	return pack_int(result_id)

def make_0a08(result_id):
	"""搬送結果"""
	#0 アイテムを搬送しました
	#-1 倉庫を開けていません
	#-2 指定されたアイテムは存在しません
	#-3 指定された数量が不正です
	#-4 倉庫のアイテム数が上限を超えてしまうためキャンセルされました
	return pack_int(result_id)

def make_0604(option_list, title, show_cancel=0):
	"""NPCのメッセージのうち、選択肢から選ぶもの
	選択結果はs0605で通知する"""
	result = pack_str(title) #ウィンドウタイトル
	result += pack_array(pack_str, option_list) #選択肢 65以上でエラー
	result += pack_str("") #選んだときに確認するメッセージのタイトル
	result += pack_byte(show_cancel) #キャンセルできるかどうか
	result += pack_int(0) #timeout秒に選ばないとキャンセルしたことになる。0の場合制限無し
	return result

def make_0606():
	"""s0605で選択結果が通知された場合の応答
	箱を開けた場合は返答しない"""
	return pack_byte(0) #常に0

def make_122f(pet):
	"""pet info"""
	result = pack_int(pet.id)
	result += "\x03" #unknow
	result += pack_int(pet.master.id)
	result += pack_int(pet.master.id)
	result += pack_byte(pet.master.lv_base)
	result += pack_int(pet.master.wrprank)
	result += "\x00" #unknow
	result += pack_unsigned_byte(int(pet.x))
	result += pack_unsigned_byte(int(pet.y))
	result += pack_short(pet.speed)
	result += pack_byte(pet.dir)
	result += pack_int(pet.hp)
	result += pack_int(pet.maxhp)
	return result

def make_1234(pet):
	"""hide pet"""
	result = pack_int(pet.id)
	result += pack_byte(0) #unknow
	return result

def make_041b(pc):
	"""kanban"""
	result = pack_int(pc.id)
	result += pack_str(pc.kanban)
	return result

def make_05eb(time_ms):
	"""イベント関連のウェイト"""
	return pack_unsigned_int(time_ms) #ミリセカンド

def make_05f0(sound_id, loop=1, volume=100):
	"""音楽を再生する"""
	result = pack_int(sound_id) #MusicID #play(";data/sound/bgm_%d.wma";)
	result += pack_byte(1 if loop else 0) #ループさせるかどうか
	result += pack_byte(0) #00固定
	result += pack_int(volume) #音量 (100がMax)
	return result

def make_05f5(sound_id, loop=0, volume=100, balance=50):
	"""効果音を再生する"""
	result = pack_int(sound_id) #SoundID #play(";data/sound/se_%d.wav";)
	result += pack_byte(1 if loop else 0) #ループさせるかどうか
	result += pack_byte(0) #00固定
	result += pack_int(volume) #音量 (100がMax)
	result += pack_byte(balance) #バランス(0で左から50で中央100で右から)
	return result

def make_05fa(sound_id, loop=0, volume=100, balance=50):
	"""ジングルを再生する"""
	result = pack_int(sound_id) #SoundID #play(";data/sound/jin_%d.wav";)
	result += pack_byte(1 if loop else 0) #ループさせるかどうか
	result += pack_byte(0) #00固定
	result += pack_int(volume) #音量 (100がMax)
	result += pack_byte(balance) #バランス(0で左から50で中央100で右から)
	return result

def make_060e(pc, effect_id, id=None, x=None, y=None, dir=None):
	"""エフェクト受信"""
	result = pack_int(pc.id if id is None else id)
	result += pack_unsigned_int(effect_id) #エフェクトID(EFFECT.dat&attr.dat
	#自キャラに掛かった場合 x, yは255
	result += pack_unsigned_byte(int(255 if x is None else x))
	result += pack_unsigned_byte(int(255 if y is None else y))
	result += pack_byte(int(pc.dir if dir is None else dir))
	#result = pack_int(pc.id)
	#result += pack_int(effect_id) #エフェクトID(EFFECT.
	#result += "\xff"
	#result += "\xff"
	#result += "\x00"
	return result

def make_0613(pc, item_id_list, magnification=100):
	"""NPCのショップウィンドウ"""
	result = pack_int(magnification) #アイテムの販売価格の倍率(単位%)(100で標準)
	result += pack_array(pack_unsigned_int, item_id_list) #アイテムID（13個以上はエラー
	result += pack_int(pc.gold) #所持金
	result += pack_int(0) #銀行に預けてる金
	result += pack_byte(0) #0普通の店1CPの店2ecoin
	return result

def make_0615():
	"""NPCショップウィンドウ（売却）"""
	result = pack_int(10) #不明
	result += pack_int(4000) #不明
	result += pack_int(0) #不明
	result += pack_byte(1)+pack_int(0) #不明
	return result

def make_0209(STR, DEX, INT, VIT, AGI, MAG):
	"""ステータス上昇s0208の結果"""
	result = pack_byte(0) #unknow
	result += "\x08" #ステータス数 #常に0x08
	result += pack_short(STR) #str
	result += pack_short(DEX) #dex
	result += pack_short(INT) #int
	result += pack_short(VIT) #vit
	result += pack_short(AGI) #agi
	result += pack_short(MAG) #mag
	result += pack_short(0) #luk
	result += pack_short(0) #cha
	result += pack_short(100) #use bonus point
	return result

def make_0212(pc, STR=0, DEX=0, INT=0, VIT=0, AGI=0, MAG=0):
	"""ステータス・補正・ボーナスポイント"""
	result = "\x08" #base
	result += pack_short(pc.str) #str
	result += pack_short(pc.dex) #dex
	result += pack_short(pc.int) #int
	result += pack_short(pc.vit) #vit
	result += pack_short(pc.agi) #agi
	result += pack_short(pc.mag) #mag
	result += pack_short(0) #luk
	result += pack_short(0) #cha
	result += "\x08" #revise
	result += pack_short(pc.stradd) #str
	result += pack_short(pc.dexadd) #dex
	result += pack_short(pc.intadd) #int
	result += pack_short(pc.vitadd) #vit
	result += pack_short(pc.agiadd) #agi
	result += pack_short(pc.magadd) #mag
	result += pack_short(0) #luk
	result += pack_short(0) #cha
	result += "\x08" #bounus
	result += pack_short(STR) #str
	result += pack_short(DEX) #dex
	result += pack_short(INT) #int
	result += pack_short(VIT) #vit
	result += pack_short(AGI) #agi
	result += pack_short(MAG) #mag
	result += pack_short(0) #luk
	result += pack_short(0) #cha
	return result

def make_0fa1(src, dst, attack_type=0, damage=1, color=1):
	"""攻撃結果"""
	result = pack_int(src.id)
	result += pack_int(dst.id)
	result += pack_byte(attack_type)
	result += pack_int(damage) #hp damage(回復の場合はマイナス
	result += pack_int(0) #mp damage
	result += pack_int(0) #sp damage
	#アイテム使用やスキル使用結果のHP・MP・SPの色やエフェクト
	result += pack_int(color)
	#行動できるようになるまでの長さ(＝モーションの長さ) 2000が標準 ASPDにより短くなる 単位 0.1% ?
	result += pack_int(2000)
	#delayと同値? delayはDC等で短くなってもこの値は元のまま
	result += pack_int(2000)
	return result

def make_1225(monster):
	"""モンスター消去"""
	return pack_int(monster.id)

def make_1217(pc, emotion_id):
	"""emotion"""
	return pack_int(pc.id)+pack_unsigned_int(emotion_id)

def make_1d0c(pc, emotion_ex_id):
	"""emotion_ex"""
	return pack_int(pc.id)+pack_unsigned_byte(emotion_ex_id)

def make_00ca(name, result):
	"""whisper failed"""
	return pack_int(result)+pack_str(name)

def make_00ce(pc, message):
	"""whisper message"""
	return pack_str(pc.name)+pack_str(message)

def make_05e2(npc_id):
	"""show npc"""
	return pack_unsigned_int(npc_id)

def make_05e3(npc_id):
	"""hide npc"""
	result = pack_unsigned_int(npc_id)
	result += pack_byte(0) #353+
	result += pack_byte(0) #353+
	result += pack_byte(0) #353+
	return result

def make_0609(switch, type):
	"""blackout, whiteout"""
	result = pack_unsigned_byte(switch) #0: off, 1: on
	result += pack_unsigned_byte(type) #0: blackout, 1: whiteout
	return result

def make_1ce9(motion_ex_id):
	"""useable motion_ex_id"""
	return pack_unsigned_short(motion_ex_id)

def make_1d06(emotion_ex_enum):
	"""emotion_ex enumerate"""
	# example: 00, 03
	# enum |= 0b0001; enum |= 0b1000
	return pack_unsigned_int(emotion_ex_enum)

def make_0a0b(result):
	"""trade ask result"""
	#0 success
	#-1 トレード中です
	#-2 イベント中です
	#-3 相手がトレード中です
	#-4 相手がイベント中です
	#-5 相手が見つかりません
	#-6 トレードを断られました
	#-7 ゴーレムショップ起動中です
	#-8 相手がゴーレムショップ起動中です
	#-9 憑依中です
	#-10 相手が憑依中です
	#-11 相手のトレード設定が不許可になっています
	#-12 トレードを行える状態ではありません
	#-13 トレード相手との距離が離れすぎています
	#-14 ゲストID期間中はトレードが行なえません
	#-15 対象がゲストID期間中であるため、トレードが行なえません
	return pack_byte(result)

def make_0a0c(pc):
	"""receive trade ask"""
	return pack_str(pc.name)

def make_0a1f(gold):
	"""trade gold"""
	return pack_int(gold)

def make_0a20():
	"""trade item header"""
	return ""

def make_0a21():
	"""trade item footer"""
	return ""

def make_0a1e(item, count):
	"""trade item data"""
	result = make_0203(item, 0, 0x02, count)[1:]
	result += pack_byte(0) #unknow
	return result

def make_07d1(result):
	"""put item error (won't send if success)"""
	#-1
	#-2 存在しないアイテムです
	#-3 イベントアイテムなので捨てることが出来ません
	#-4 変身中のマリオネットは捨てることが出来ません
	#-5 起動中のゴーレムは捨てることが出来ません
	#-6 ゴーレムショップに出品中のアイテムは捨てることが出来ません
	#-7 行動不能時はアイテムを捨てる事が出来ません
	#-8 トレード中はアイテムを捨てる事が出来ません
	#-9 使用中のアイテムを捨てる事はできません
	#-10 イベント中はアイテムを捨てることが出来ません
	#-11 装備中のアイテムは捨てることが出来ません
	#-15 ゲストID期間中はアイテムをドロップすることができません。アイテムを捨てたい場合は、アイテムウィンドウにあるゴミ箱のアイコンをクリックしてください
	#-16_0 「あ、あわわわわ･･･それは捨てることはできませんよ！」
	#-16_1 「ギルド商人までお持ちください。」
	#-17 レンタルアイテムは捨てることが出来ません
	#-18 ＤＥＭ強化チップを捨てることが出来ません
	#-19 変形したアイテムを捨てることが出来ません
	#-20 変形中のアイテムを捨てることが出来ません
	#-21 ロックアイテムは捨てることが出来ません
	#-22 ユニオンペットは捨てることが出来ません
	return pack_int(-1)+pack_byte(result)

def make_07d5(mapitem_obj):
	"""drop item info"""
	#0～通常ドロップ（マップごとに割り振り, 1000000000～憑依アイテム
	result = pack_int(mapitem_obj.id) #落ちているアイテムに振られたID
	result += pack_unsigned_int(mapitem_obj.item.item_id) #アイテムのID
	result += pack_unsigned_byte(int(mapitem_obj.x))
	result += pack_unsigned_byte(int(mapitem_obj.y))
	result += pack_unsigned_short(mapitem_obj.item.count)
	#アイテムを落としたキャラのサーバキャラID。憑依アイテムは0固定
	result += pack_int(mapitem_obj.id_from)
	result += pack_int(0) #unknow
	result += pack_unsigned_byte(0) #憑依装備は1。通常アイテムは0
	result += pack_str("") #憑依装備のコメント。(憑依装備のみ)
	result += pack_int(1) #鑑定されているかどうか #353+ byte->int
	result += pack_unsigned_byte(0) #融合されてるかどうか
	return result

def make_07e6(error):
	"""pick up item error"""
	return pack_int(-1)+pack_byte(error)
	#0 アイテムを拾うことが出来ません
	#-1 存在しないアイテムです
	#-2 行動不能時はアイテムを拾うことが出来ません
	#-3 憑依中はアイテムを拾うことが出来ません
	#-4 憑依者とレベルが離れすぎているので装備出来ません
	#-5 装備箇所は既に装備中です
	#-6 憑依装備は定員オーバーです
	#-7 憑依アイテムは装備出来ません
	#-8 トレード中はアイテムを拾うことが出来ません
	#-9 イベント中はアイテムを拾うことが出来ません
	#-10 取得権限がありません
	#-11 これ以上アイテムを所持することはできません
	#-12 憑依者取得中です
	#-13 拾える状態ではありません
	#-14 憑依アイテムは闘技場モードでないと拾えません
	#-15 憑依アイテムはチャンプバトルに参戦していないと拾えません
	#-16 マシナフォーム中は憑依アイテムを拾うことができません

def make_07df(mapitem_obj):
	"""pick up item"""
	result = pack_int(mapitem_obj.id) #落ちているアイテムに振られたID
	result += pack_unsigned_byte(0) #unknow
	result += pack_int(-1) #unknow
	return result

def make_020f(pc, pc_size):
	"""size"""
	result = pack_int(pc.id)
	result += pack_unsigned_int(pc_size)
	result += pack_unsigned_int(1500)
	return result

def make_1e7e(result, status):
	"""dem form change result"""
	result = pack_byte(result) #change result
	result += pack_byte(status) #dem form status
	return result

def make_1389(pc, target_id, x, y, skill_id, skill_lv, error=0, cast=0):
	"""スキル使用通知"""
	result = pack_short(skill_id) #スキルID
	result += pack_byte(error) #エラー値 [00]成功時。失敗時に値が入っている。
	result += pack_int(pc.id) #スキル使用者のサーバキャラID
	result += pack_int(cast) #詠唱時間っぽ（ミリ秒単位）。失敗時は-1
	result += pack_int(target_id) #スキル対象者のサーバキャラID。失敗時は-1
	result += pack_unsigned_byte(x if (x!=-1) else 255)
	result += pack_unsigned_byte(y if (y!=-1) else 255)
	result += pack_byte(skill_lv) #スキルLv
	result += pack_byte(0) #H.E.ARTを使ったときの白い玉の数
	return result

def make_138a(pc, error=0):
	"""スキル使用通知"""
	result = pack_int(pc.id) #サーバキャラID
	result += pack_byte(error) #エラー値
	return result

def make_1392(pc, target_list, skill_id, skill_lv, damage_list, color_list):
	"""スキル使用結果通知（対象：単体）"""
	if not target_list:
		target_list = ()
		damage_list = ()
		color_list = ()
	else:
		assert len(target_list) == len(damage_list)
		assert len(damage_list) == len(color_list)
	i = len(target_list)
	result = pack_short(skill_id) #スキルID
	result += pack_array(pack_unsigned_byte, (0,)*i) #不明の数
	result += pack_int(pc.id) #使用キャラのサーバキャラID
	#対象のサーバキャラID #エフェクトが出る対象
	result += pack_int(target_list[0] if target_list else 0)
	result += pack_array(pack_int, target_list) #対象キャラ
	result += pack_unsigned_byte(int(255))
	result += pack_unsigned_byte(int(255))
	result += pack_array(pack_int, damage_list) #HPダメージ
	result += pack_array(pack_int, (0,)*i) #MPダメージ
	result += pack_array(pack_int, (0,)*i) #SPダメージ数
	result += pack_array(pack_int, color_list) #数字の色の数
	result += pack_byte(skill_lv) #スキルLv
	return result

def make_138d(pc, target_list, x, y, skill_id, skill_lv, damage_list, color_list):
	"""スキル使用結果通知（対象：地面）"""
	if not target_list:
		target_list = ()
		damage_list = ()
		color_list = ()
	else:
		assert len(target_list) == len(damage_list)
		assert len(damage_list) == len(color_list)
	i = len(target_list)
	result = pack_short(skill_id) #スキルID
	result += pack_array(pack_unsigned_byte, (0,)*i) #不明の数
	result += pack_int(pc.id) #使用キャラのサーバキャラID
	#対象のサーバキャラID #エフェクトが出る対象
	#result += pack_int(target_list[0] if target_list else 0)
	result += pack_array(pack_int, target_list) #対象キャラ
	result += pack_unsigned_byte(int(x))
	result += pack_unsigned_byte(int(y))
	result += pack_array(pack_int, damage_list) #HPダメージ
	result += pack_array(pack_int, (0,)*i) #MPダメージ
	result += pack_array(pack_int, (0,)*i) #SPダメージ数
	result += pack_array(pack_int, color_list) #数字の色の数
	result += pack_byte(skill_lv) #スキルLv
	return result

def make_05dc():
	"""移動ロック開始(イベント開始)"""
	return ""

def make_05dd():
	"""移動ロック終了(イベント終了)"""
	return ""

def make_09c5(pc, item_id, target_id, x, y, skill_id=0, skill_lv=0, error=0):
	"""アイテム使用結果"""
	result = pack_unsigned_int(item_id) #アイテムID （0xFFFFFFFFの場合もある)
	result += pack_short(error) #0なら成功 それ以外なら失敗
	result += pack_int(pc.id) #アイテム使用者のサーバキャラID
	result += pack_int(500) #キャスト時間 ミリ秒単位
	result += pack_int(target_id) #アイテム対象者のサーバキャラID
	result += pack_unsigned_byte(int(x)) #x
	result += pack_unsigned_byte(int(y)) #y
	result += pack_short(skill_id)
	result += pack_byte(skill_lv)
	return result
	#-1 ターゲットがいません
	#-2 指定した座標へは使用できません
	#-3 使用できない状態です
	#-4 スキル中の為使用できませんでした
	#-5 遠距離攻撃中の為使用できませんでした
	#-6 視線が通っていません
	#-7 イベント中の為使用できませんでした
	#-8 アイテムを使用する事が出来ないターゲットです
	#-9 行動不能状態の為使用できませんでした
	#-10 ゴーレムショップに出品中です
	#-11 ゴーレムは既に起動しています
	#-12 未鑑定品の為使用できませんでした
	#-13 スキルが使えませんでした
	#-14 
	#-15 宿主はマリオネットにのりうつれません
	#-16 条件が合わない為マリオネットにのりうつれません
	#-17 このマリオネットは未実装です
	#-18 再度マリオネットにのりうつるには時間を置いてください
	#-19 アイテム使用中の為使用できませんでした
	#-20 攻撃中の為使用できませんでした
	#-21 使用できませんでした
	#-22 この餌は対象ペットへは与えられません
	#-23 指定した対象へはこのアイテムは使用できません
	#-24 「メタモーバトル」のみ使用可能です
	#-25 プルルに変身中でないと使用出来ません
	#-26 このアイテムでは現在のマリオネットを解除できません
	#-27 この場所ではマリオネットにのりうつることはできません
	#-28 「メタモーバトル」中は使用できません
	#-29 このマップでは使用できません
	#-30 イベントが用意されていません
	#-31 何らかの理由で作成できませんでした
	#-32 ロボット騎乗中でないと使用できません
	#-33 ＤＥＭキャラクターはマリオネットにのりうつることができません
	#-34 ユニオンペットを装備していません
	#-35 装備中のユニオンペットに使えません
	#-36 対象のアクトキューブを既に覚えている
	#-37 アクトキューブをこれ以上覚える事が出来ない
	#-100 何らかの原因で使用できませんでした

def make_09c6(pc, item_id, target_id, x, y):
	"""アイテム使用効果 (対象：地面)"""
	result = pack_unsigned_int(item_id) #アイテムID
	result += pack_array(pack_unsigned_byte, ()) #unknow
	result += pack_int(pc.id) #アイテム使用者のサーバキャラID
	result += pack_array(pack_int, ()) #target_id
	result += pack_unsigned_byte(int(x)) #x
	result += pack_unsigned_byte(int(y)) #y
	result += pack_array(pack_int, ()) #hp #353+ short->int
	result += pack_array(pack_int, ()) #mp #353+ short->int
	result += pack_array(pack_int, ()) #sp #353+ short->int
	result += pack_array(pack_int, ()) #color_flag
	return result

def make_09c7(pc, item_id, target_id, x, y):
	"""アイテム使用効果 (対象：単体)"""
	result = pack_unsigned_int(item_id) #アイテムID
	result += pack_array(pack_unsigned_byte, (0,)) #unknow
	result += pack_int(pc.id) #アイテム使用者のサーバキャラID
	result += pack_array(pack_int, (target_id,)) #target_id
	result += pack_unsigned_byte(int(x)) #x
	result += pack_unsigned_byte(int(y)) #y
	result += pack_array(pack_int, (0,)) #hp #hp #353+ short->int
	result += pack_array(pack_int, (0,)) #mp #hp #353+ short->int
	result += pack_array(pack_int, (0,)) #sp #hp #353+ short->int
	result += pack_array(pack_int, (0,)) #color_flag
	return result

def make_09c8(pc, item_id):
	"""アイテム使用効果 (対象：自分)"""
	result = pack_unsigned_int(item_id) #アイテムID
	result += pack_array(pack_unsigned_byte, (0,)) #unknow
	result += pack_int(pc.id) #アイテム使用者のサーバキャラID
	result += pack_array(pack_int, (pc.id,)) #target_id
	result += pack_unsigned_byte(int(pc.x)) #x
	result += pack_unsigned_byte(int(pc.y)) #y
	result += pack_array(pack_int, (0,)) #hp #hp #353+ short->int
	result += pack_array(pack_int, (0,)) #mp #hp #353+ short->int
	result += pack_array(pack_int, (0,)) #sp #hp #353+ short->int
	result += pack_array(pack_int, (0,)) #color_flag
	return result

def make_0bb8(pc):
	"""飛空庭のひも・テント表示"""
	if pc.usermap_obj.usermap_type == usermaps.USERMAP_TYPE_FLYGARDEN:
		result = pack_int(pc.usermap_obj.id) #サーバキャラ
		result += pack_str("fg_rope_01") #attrファイル名 33_tent01 fg_rope_01
		result += pack_unsigned_byte(int(pc.usermap_obj.entrance_x))
		result += pack_unsigned_byte(int(pc.usermap_obj.entrance_y))
		result += pack_unsigned_byte(0x06) #04:tent 06:rope
		result += pack_int(pc.usermap_obj.entrance_event_id)
		result += pack_str(pc.usermap_obj.entrance_title)
		result += pack_int(pc.id) #呼び出したキャラの固有ID
		return result

def make_0bb9(pc):
	"""飛空庭のひも・テント消去"""
	return pack_int(pc.usermap_obj.id) #サーバキャラ

def make_1be4(pc):
	"""飛空庭ログイン #unfinished"""
	i = len(general.FLYGARDEN_ATTR_LIST)
	usermap_obj = pc.map_obj
	result = pack_int(usermap_obj.map_id)
	result += pack_unsigned_byte(int(pc.x)) #x
	result += pack_unsigned_byte(int(pc.y)) #y
	result += pack_unsigned_byte(int(pc.dir)) #dir
	result += pack_array(pack_int, [
		getattr(usermap_obj.flygarden, attr)
		for attr in general.FLYGARDEN_ATTR_LIST
	]) #item_ids
	result += pack_array(pack_byte, (0,)*i) #colors
	result += pack_byte(0) #土台色？
	general.log(result.encode("hex"))
	return result

def make_13bc(weather):
	"""飛空庭の天候"""
	return pack_byte(weather) #0なし1雨2雪
 
def make_13bd(sky):
	"""飛空庭の天体"""
	return pack_byte(sky) #0デフォ1夕2夜3宇宙 #0~14

def make_1bee(pc):
	"""家具情報ヘッダ"""
	return pack_int(pc.map_obj.map_id)

def make_1bf0(pc):
	"""家具情報フッタ"""
	return pack_int(pc.map_obj.map_id)

def make_1bef(pc):
	"""家具情報データ #unfinished"""
	usermap_obj = pc.map_obj
	result = pack_int(usermap_obj.id)
	result += pack_int(0) #家具のID
	result += pack_int(0) #フィギュアの場合 モンスターIDが入ってる
	result += pack_short(rawx)
	result += pack_short(rawy) #高さ？
	result += pack_short(rawz) #奥行き
	result += pack_short(rawdir) #傾き？
	result += pack_short(motion) #モーション
	result += pack_short(y_rotate) #y軸回転？
	result += pack_short(z_rotate) #z軸回転？ 
	result += pack_short(name) #名前
	return result

def make_1bf9(item_id, place):
	"""飛空庭に装飾品を装着・解除するの結果"""
	result = pack_int(item_id)
	result += pack_int(place)
	result += pack_byte(0)
	return result

name_map = general.get_name_map(globals(), "make_")