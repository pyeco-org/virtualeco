#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import hashlib
import os
from lib import general
from lib.packet import packet
from lib import users
WORD_FRONT = "0000"
WORD_BACK = "0000"
DATA_TYPE_NOT_PRINT = ()

class MapDataHandler:
	def __init__(self):
		self.user = None
		self.player = None
	
	def send(self, *args):
		self.send_packet(packet.make(*args))
	
	def send_item_list(self):
		with self.player.lock:
			self._send_item_list()
	def _send_item_list(self):
		for iid in self.player.sort.item:
			self.send("0203",
					self.player.item[iid],
					iid,
					self.player.get_item_part(iid)
					)
	
	def stop(self):
		if self.user:
			self.user.reset_map()
			self.user = None
		self._stop()
	
	def handle_data(self, data):
		#000a 000a 0000040d2e159d00
		data = data[:general.unpack_short(data[:2])+2]
		data_type = data[2:4].encode("hex")
		if data_type not in DATA_TYPE_NOT_PRINT:
			print "[ map ] %s %s %s"%(
				data[:2].encode("hex"), #length #len(type+data)
				data[2:4].encode("hex"), #type
				data[4:].encode("hex"), #data
				)
		try:
			handler = getattr(self, "do_%s"%data_type)
		except AttributeError:
			print "[ map ] unknow packet type", data_type, data.encode("hex")
			return
		try:
			handler(data[4:])
		except:
			print "[ map ] handle_data error:", data.encode("hex")
			print traceback.format_exc()
	
	def do_000a(self, data):
		print "[ map ] eco version", general.unpack_int(data[:4])
		self.send("000b", data)
		self.send("000f", WORD_FRONT+WORD_BACK)
	
	def do_0032(self, data):
		"""接続確認(マップサーバとのみ)#20秒一回"""
		self.send("0033", True) #reply_ping=True
	
	def do_0010(self, data):
		print "[ map ]", "login",
		username, username_length = general.unpack_str(data)
		password_sha1 = general.unpack_str(data[username_length:])[0]
		print username, password_sha1
		for user in users.get_user_list():
			with user.lock:
				if user.name != username:
					continue
				user_password_sha1 = hashlib.sha1(
					"".join((str(general.unpack_int(WORD_FRONT)),
							user.password,
							str(general.unpack_int(WORD_BACK)),
							))).hexdigest()
				if user_password_sha1 != password_sha1:
					self.stop()
					return
				user.reset_map()
				user.map_client = self
				self.user = user
				self.send("0011") #認証結果(マップサーバーに認証情報の送信(s0010)に対する応答)
				break
		else:
			self.stop()
	
	def do_01fd(self, data):
		num = general.unpack_byte(data[4:5])
		with self.user.lock:
			if not self.user.player[num]:
				self.stop()
				return
			self.player = self.user.player[num]
		self.player.reset_map()
		with self.player.lock:
			self.player.online = True
			print "[ map ] set", self.player
		self.send("1239", self.player, True) #キャラ速度通知・変更 #マップ読み込み中は10
		self.send("1a5f") #右クリ設定
		self.send_item_list() #インベントリ情報
		self.send("01ff", self.player) #自分のキャラクター情報
		self.send("03f2", 0x04) #システムメッセージ #構えが「叩き」に変更されました
		self.send("09ec", self.player) #ゴールド入手 
		self.send("0221", self.player) #最大HP/MP/SP
		self.send("021c", self.player) #現在のHP/MP/SP/EP
		self.send("0212", self.player) #ステータス・補正・ボーナスポイント
		self.send("0217", self.player) #詳細ステータス
		self.send("0230", self.player) #現在CAPA/PAYL
		self.send("0231", self.player) #最大CAPA/PAYL
		self.send("0244", self.player) #職業
		self.send("0226", self.player, 0) #スキル一覧 一次職
		self.send("0226", self.player, 1) #スキル一覧 エキスパ
		self.send("022e", self.player) #リザーブスキル
		self.send("023a", self.player) #Lv JobLv ボーナスポイント スキルポイント
		self.send("0235", self.player) #EXP/JOBEXP
		self.send("09e9", self.player) #キャラの見た目を変更
		self.send("0fa7", self.player) #キャラのモード変更
		self.send("1f72") #もてなしタイニーアイコン
		self.send("157c", self.player) #キャラの状態
		self.send("022d", self.player) #HEARTスキル
		self.send("0223", self.player) #属性値
		self.send("122a") #モンスターID通知
		self.send("1bbc") #スタンプ帳詳細
		self.send("025d") #不明
		self.send("0695") #不明
		self.send("0236", self.player) #wrp ranking関係
		self.send("1b67", self.player) #MAPログイン時に基本情報を全て受信した後に受信される
		print "[ map ] send player info success"


