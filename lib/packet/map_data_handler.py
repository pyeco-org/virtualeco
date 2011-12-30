#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import hashlib
import os
from lib import general
from lib.packet import packet
from lib import users
from lib import script
WORD_FRONT = "0000"
WORD_BACK = "0000"
DATA_TYPE_NOT_PRINT = (	"11f8", #自キャラの移動
					"0032", #接続確認(マップサーバとのみ) 20秒一回
					"0fa5", #戦闘状態変更通知
					)

class MapDataHandler:
	def __init__(self):
		self.user = None
		self.player = None
	
	def send(self, *args):
		self.send_packet(packet.make(*args))
	def send_map_without_self(self, *args):
		packet_data = packet.make(*args)
		with self.player.lock:
			if not self.player.map_obj:
				return
			with self.player.map_obj.lock:
				for player in self.player.map_obj.player_list:
					if not player.online:
						continue
					if self.player == player:
						continue
					player.user.map_client.send_packet(packet_data)
	def send_map(self, *args):
		self.send_map_without_self(*args)
		self.send(*args)
	
	def stop(self):
		if self.user:
			self.user.reset_map()
			self.user = None
		self._stop()
	
	def handle_data(self, data_decode):
		#000a 000a 0000040d2e159d00
		while data_decode:
			data_length = general.unpack_short(data_decode[:2])
			data_type = data_decode[2:4].encode("hex")
			data = data_decode[4:data_length+2]
			data_decode = data_decode[data_length+2:]
			if data_type not in DATA_TYPE_NOT_PRINT:
				print "[ map ] %s %s %s"%(
					general.pack_short(data_length).encode("hex"),
					data_type,
					data.encode("hex"))
			try:
				handler = getattr(self, "do_%s"%data_type)
			except AttributeError:
				print "[ map ] unknow packet type", data_type, data.encode("hex")
				return
			try:
				handler(data)
			except:
				print "[ map ] handle_data error:", data.encode("hex")
				print traceback.format_exc()
	
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
	
	def sync_map(self):
		with self.player.lock:
			if self.player.map_obj:
				with self.player.map_obj.lock:
					for player in self.player.map_obj.player_list:
						if not player.online:
							continue
						if not player.visible:
							continue
						if self.player == player:
							continue
						print "sync_map", self.player, "<->", player
						#他キャラ情報→自キャラ
						self.send("120c", player)
						#自キャラ情報→他キャラ
						player.user.map_client.send("120c", self.player)
					for pet in self.player.map_obj.pet_list:
						if not pet.master:
							continue
						self.send("122f", pet) #pet info
					for monster in self.player.map_obj.monster_list:
						if monster.hp <= 0:
							continue
						self.send("122a", (monster.id,)) #モンスターID通知
						self.send("1220", monster) #モンスター情報
	
	def send_object_detail(self, i):
		for player in users.get_player_list():
			with player.lock:
				if not player.online:
					continue
				if not player.visible:
					continue
				if player.id == i:
					self.send("020e", player) #キャラ情報
					self.send("041b", player) #kanban
					return
	
	def do_000a(self, data):
		#接続・接続確認
		print "[ map ] eco version", general.unpack_int(data[:4])
		self.send("000b", data)
		self.send("000f", WORD_FRONT+WORD_BACK)
	
	def do_0032(self, data):
		#接続確認(マップサーバとのみ) 20秒一回
		self.send("0033", True) #reply_ping=True
	
	def do_0010(self, data):
		#マップサーバーに認証情報の送信
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
		#選択したキャラ番号通知
		if not self.player:
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
		self.player.visible = False
		self.player.motion_id = 111
		self.player.motion_loop = False
		self.player.set_map()
		self.send("1239", self.player, 10) #キャラ速度通知・変更 #マップ読み込み中は10
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
		self.send("0244", self.player) #ステータスウィンドウの職業 
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
	
	def do_11fe(self, data):
		#MAPワープ完了通知
		print "[ map ]", "map load"
		self.player.visible = True
		self.send("1239", self.player) #キャラ速度通知・変更
		self.send("196e", self.player) #クエスト回数・時間
		self.send("0259", self.player) #ステータス試算結果
		#self.send("1b67", self.player) #MAPログイン時に基本情報を全て受信した後に受信される
		self.send("157c", self.player) #キャラの状態
		self.send("0226", self.player, 0) #スキル一覧0
		self.send("0226", self.player, 1) #スキル一覧1
		self.send("022e", self.player) #リザーブスキル
		self.send("022d", self.player) #HEARTスキル
		self.send("09e9", self.player) #キャラの見た目を変更
		self.send("021c", self.player) #現在のHP/MP/SP/EP
		self.sync_map()
		#self.player.unset_pet()
		#self.player.set_pet()
	
	def do_0fa5(self, data):
		#戦闘状態変更通知
		with self.player.lock:
			self.player.battlestatus = general.unpack_byte(data[:1])
		#戦闘状態変更通知
		self.send("0fa6", self.player)
	
	def do_121b(self, data):
		#モーションセット＆ログアウト
		motion_id = general.unpack_short(data[:2])
		loop = general.unpack_byte(data[2]) and True or False
		print "[ map ] motion %d loop %s"%(motion_id, loop)
		self.player.set_motion(motion_id, loop)
		self.send_map("121c", self.player) #モーション通知
		if motion_id == 135 and loop: #ログアウト開始
			print "[ map ]", "start logout"
			self.send("0020", self.player, "logoutstart")
			self.player.logout = True
	
	def do_001e(self, data):
		#ログアウト(PASS鍵リセット・マップサーバーとのみ通信)
		print "[ map ] logout"
		#self.player.unset_pet()
		self.send_map_without_self("1211", self.player) #PC消去
	
	def do_001f(self, data):
		#ログアウト開始&ログアウト失敗
		if general.unpack_byte(data[:1]) == 0:
			print "[ map ] logout success"
		else:
			print "[ map ] logout failed"
	
	def do_11f8(self, data):
		#自キャラの移動
		if self.player.logout:
			self.player.logout = False
			self.send("0020", self.player, "logoutcancel")
			print "[ map ] logout cancel"
		rawx = general.unpack_short(data[:2]); data = data[2:]
		rawy = general.unpack_short(data[:2]); data = data[2:]
		rawdir = general.unpack_short(data[:2]); data = data[2:]
		move_type = general.unpack_short(data[:2]); data = data[2:]
		#print "[ map ] move rawx %d rawy %d rawdir %d move_type %d"%(
		#	rawx, rawy, rawdir, move_type)
		self.player.set_raw_coord(rawx, rawy)
		self.player.set_raw_dir(rawdir)
		self.send_map_without_self("11f9", self.player, move_type)
	
	def do_020d(self, data):
		#キャラクタ情報要求
		obj_id = general.unpack_int(data[:4])
		print "[ map ] request object id", obj_id
		self.send_object_detail(obj_id)
	
	def do_13ba(self, data):
		#座る/立つの通知
		if self.player.motion_id != 135:
			self.player.set_motion(135, False) #座る
		else:
			self.player.set_motion(111, False) #立つ
		self.send_map("121c", self.player) #モーション通知
	
	def do_03e8(self, data):
		#オープンチャット送信
		message = general.unpack_str(data)[0]
		self.send_map("03e9", self.player.id, message) #オープンチャット・システムメッセージ
	
	def do_05e6(self, data):
		#イベント実行
		event_id = general.unpack_int(data[:4])
		script.run(self.player, event_id)
