#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
from lib.packet import packet
from lib.packet import login_data_handler
from lib.packet import map_data_handler
from lib.packet.packet_struct import *
ID = 110
PACKET_START = 0x0200
PACKET_END = 0x0400
PACKET_KNOWN_LIST = packet.name_map.keys()
PACKET_KNOWN_LIST += login_data_handler.LoginDataHandler.name_map.keys()
PACKET_KNOWN_LIST += map_data_handler.MapDataHandler.name_map.keys()

from lib import general
from lib.packet.packet import pack_item_unsigned_byte_attr, pack_pict_id
def make_09e9(pc):
	"""装備情報 IDのキャラの見た目を変更"""
	result = pack_int(pc.id)
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
	item_socks = pc.item.get(pc.equip.socks)
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
	#result += pack_pict_id(item_pet, general.PET_TYPE_LIST)
	result += pack_int(0)
	#左手モーションタイプ size=3 (片手, 両手, 攻撃)
	result += "\x03"+l_s_motion+l_d_motion+"\x00"
	#右手モーションタイプ size=3 #chr_act_tbl.csvを参照する
	result += "\x03"+r_s_motion+r_d_motion+"\x00"
	result += "\x03"+"\x00\x00\x00" #乗り物モーションタイプ size=3
	result += pack_int(0) #乗り物アイテムID
	result += pack_byte(0) #乗り物の染色値
	result += pack_byte(0) #戦闘状態の時1#0fa6で変更要請#0fa7で変更される
	return result

def make_020e(pc):
	"""キャラ情報"""
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
	result += pack_byte(0) #ゲストIDかどうか
	result += pack_byte(pc.lv_base) #レベル（ペットは1固定
	result += pack_int(pc.wrprank) #WRP順位（ペットは -1固定。
									#別のパケで主人の値が送られてくる
	result += pack_int(0) #不明
	result += pack_byte(-1) #不明
	return result

packet.name_map["09e9"] = make_09e9
packet.name_map["020e"] = make_020e
print "inject..."

def main(pc):
	for packet_type in xrange(PACKET_START, PACKET_END+1):
		#create data
		data_type = pack_unsigned_short(packet_type)
		data_value = make_020e(pc.pet)
		#skip known type
		if data_type.encode("hex") in PACKET_KNOWN_LIST:
			general.log("skip", data_type.encode("hex"))
			continue
		#create raw packet
		packet_raw = pack_short(len(data_value)+2)
		packet_raw += data_type
		packet_raw += data_value
		#create encrypted packet
		packet_enc = general.encode(packet_raw, pc.user.map_client.rijndael_obj)
		#send
		general.log("send", data_type.encode("hex"), data_value.encode("hex"))
		pc.user.map_client.send_packet(packet_enc)
		#break
