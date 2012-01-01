#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import hashlib
import os
from lib import general
from lib.packet import packet
from lib import users
from lib import script
from lib import pets
WORD_FRONT = "0000"
WORD_BACK = "0000"
DATA_TYPE_NOT_PRINT = (	"11f8", #自キャラの移動
					"0032", #接続確認(マップサーバとのみ) 20秒一回
					"0fa5", #戦闘状態変更通知
					)

class MapDataHandler:
	def __init__(self):
		self.user = None
		self.pc = None
	
	def send(self, *args):
		self.send_packet(packet.make(*args))
	
	def send_map_without_self(self, *args):
		packet_data = packet.make(*args)
		with self.pc.lock:
			if not self.pc.map_obj:
				return
			with self.pc.map_obj.lock:
				for pc in self.pc.map_obj.pc_list:
					if not pc.online:
						continue
					if self.pc == pc:
						continue
					pc.user.map_client.send_packet(packet_data)
	
	def send_map(self, *args):
		self.send_map_without_self(*args)
		self.send(*args)
	
	def send_server(self, *args):
		packet_data = packet.make(*args)
		for p in users.get_pc_list():
			with p.lock and p.user.lock:
				if not p.online:
					continue
				p.user.map_client.send_packet(packet_data)
	
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
		with self.pc.lock:
			self._send_item_list()
	def _send_item_list(self):
		for iid in self.pc.sort.item:
			self.send("0203",
					self.pc.item[iid],
					iid,
					self.pc.get_item_part(iid)
					)
	
	def sync_map(self):
		with self.pc.lock:
			if self.pc.map_obj:
				with self.pc.map_obj.lock:
					for pc in self.pc.map_obj.pc_list:
						if not pc.online:
							continue
						if not pc.visible:
							continue
						if self.pc == pc:
							continue
						print "sync_map", self.pc, "<->", pc
						#他キャラ情報→自キャラ
						self.send("120c", pc)
						#自キャラ情報→他キャラ
						pc.user.map_client.send("120c", self.pc)
					for pet in self.pc.map_obj.pet_list:
						if not pet.master:
							continue
						self.send("122f", pet) #pet info
					for monster in self.pc.map_obj.monster_list:
						if monster.hp <= 0:
							continue
						self.send("122a", (monster.id,)) #モンスターID通知
						self.send("1220", monster) #モンスター情報
	
	def send_object_detail(self, i):
		if i >= pets.PET_ID_START_FROM:
			pet = pets.get_pet_from_id(i)
			if not pet:
				return
			if not pet.master:
				return
			self.send("020e", pet)
		else:
			pc = users.get_pc_from_id(i)
			if not pc:
				return
			with pc.lock:
				if not pc.online:
					return
				if not pc.visible:
					return
				self.send("020e", pc) #キャラ情報
				self.send("041b", pc) #kanban
	
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
		if not self.pc:
			num = general.unpack_byte(data[4:5])
			with self.user.lock:
				if not self.user.pc_list[num]:
					self.stop()
					return
				self.pc = self.user.pc_list[num]
			self.pc.reset_map()
			with self.pc.lock:
				self.pc.online = True
				print "[ map ] set", self.pc
		self.pc.set_visible(False)
		self.pc.set_motion(111, False)
		self.pc.set_map()
		self.pc.set_coord(self.pc.x, self.pc.y) #on login
		self.send("1239", self.pc, 10) #キャラ速度通知・変更 #マップ読み込み中は10
		self.send("1a5f") #右クリ設定
		self.send_item_list() #インベントリ情報
		self.send("01ff", self.pc) #自分のキャラクター情報
		self.send("03f2", 0x04) #システムメッセージ #構えが「叩き」に変更されました
		self.send("09ec", self.pc) #ゴールド入手 
		self.send("0221", self.pc) #最大HP/MP/SP
		self.send("021c", self.pc) #現在のHP/MP/SP/EP
		self.send("0212", self.pc) #ステータス・補正・ボーナスポイント
		self.send("0217", self.pc) #詳細ステータス
		self.send("0230", self.pc) #現在CAPA/PAYL
		self.send("0231", self.pc) #最大CAPA/PAYL
		self.send("0244", self.pc) #ステータスウィンドウの職業 
		self.send("0226", self.pc, 0) #スキル一覧 一次職
		self.send("0226", self.pc, 1) #スキル一覧 エキスパ
		self.send("022e", self.pc) #リザーブスキル
		self.send("023a", self.pc) #Lv JobLv ボーナスポイント スキルポイント
		self.send("0235", self.pc) #EXP/JOBEXP
		self.send("09e9", self.pc) #キャラの見た目を変更
		self.send("0fa7", self.pc) #キャラのモード変更
		self.send("1f72") #もてなしタイニーアイコン
		self.send("157c", self.pc) #キャラの状態
		self.send("022d", self.pc) #HEARTスキル
		self.send("0223", self.pc) #属性値
		self.send("122a") #モンスターID通知
		self.send("1bbc") #スタンプ帳詳細
		self.send("025d") #不明
		self.send("0695") #不明
		self.send("0236", self.pc) #wrp ranking関係
		self.send("1b67", self.pc) #MAPログイン時に基本情報を全て受信した後に受信される
		print "[ map ] send pc info success"
	
	def do_11fe(self, data):
		#MAPワープ完了通知
		print "[ map ]", "map load"
		self.pc.set_visible(True)
		self.send("1239", self.pc) #キャラ速度通知・変更
		self.send("196e", self.pc) #クエスト回数・時間
		self.send("0259", self.pc) #ステータス試算結果
		#self.send("1b67", self.pc) #MAPログイン時に基本情報を全て受信した後に受信される
		self.send("157c", self.pc) #キャラの状態
		self.send("0226", self.pc, 0) #スキル一覧0
		self.send("0226", self.pc, 1) #スキル一覧1
		self.send("022e", self.pc) #リザーブスキル
		self.send("022d", self.pc) #HEARTスキル
		self.send("09e9", self.pc) #キャラの見た目を変更
		self.send("021c", self.pc) #現在のHP/MP/SP/EP
		self.sync_map()
		self.pc.unset_pet()
		self.pc.set_pet()
	
	def do_0fa5(self, data):
		#戦闘状態変更通知
		with self.pc.lock:
			self.pc.battlestatus = general.unpack_byte(data[:1])
		#戦闘状態変更通知
		self.send("0fa6", self.pc)
	
	def do_121b(self, data):
		#モーションセット＆ログアウト
		motion_id = general.unpack_short(data[:2])
		loop = general.unpack_byte(data[2]) and True or False
		print "[ map ] motion %d loop %s"%(motion_id, loop)
		#self.pc.set_motion(motion_id, loop)
		#self.send_map("121c", self.pc) #モーション通知
		script.motion(self.pc, motion_id, loop)
		if motion_id == 135 and loop: #ログアウト開始
			print "[ map ]", "start logout"
			self.send("0020", self.pc, "logoutstart")
			self.pc.logout = True
	
	def do_001e(self, data):
		#ログアウト(PASS鍵リセット・マップサーバーとのみ通信)
		print "[ map ] logout"
		self.pc.unset_pet()
		self.send_map_without_self("1211", self.pc) #PC消去
	
	def do_001f(self, data):
		#ログアウト開始&ログアウト失敗
		if general.unpack_byte(data[:1]) == 0:
			print "[ map ] logout success"
		else:
			print "[ map ] logout failed"
	
	def do_11f8(self, data):
		#自キャラの移動
		if self.pc.logout:
			self.pc.logout = False
			self.send("0020", self.pc, "logoutcancel")
			print "[ map ] logout cancel"
		rawx = general.unpack_short(data[:2]); data = data[2:]
		rawy = general.unpack_short(data[:2]); data = data[2:]
		rawdir = general.unpack_short(data[:2]); data = data[2:]
		move_type = general.unpack_short(data[:2]); data = data[2:]
		#print "[ map ] move rawx %d rawy %d rawdir %d move_type %d"%(
		#	rawx, rawy, rawdir, move_type)
		self.pc.set_raw_coord(rawx, rawy)
		self.pc.set_raw_dir(rawdir)
		self.send_map_without_self("11f9", self.pc, move_type)
		with self.pc.lock:
			if not self.pc.pet:
				return
			with self.pc.pet.lock:
				self.pc.pet.set_raw_coord(rawx, rawy)
				self.pc.pet.set_raw_dir(rawdir)
				self.send_map("11f9", self.pc.pet, 0x06) #歩き
	
	def do_020d(self, data):
		#キャラクタ情報要求
		obj_id = general.unpack_int(data[:4])
		print "[ map ] request object id", obj_id
		self.send_object_detail(obj_id)
	
	def do_13ba(self, data):
		#座る/立つの通知
		if self.pc.motion_id != 135:
			script.motion(self.pc, 135, False) #座る
		else:
			script.motion(self.pc, 111, False) #立つ
	
	def do_03e8(self, data):
		#オープンチャット送信
		message = general.unpack_str(data)[0]
		if not script.handle_cmd(self.pc, message):
			self.send_map("03e9", self.pc.id, message) #オープンチャット・システムメッセージ
	
	def do_05e6(self, data):
		#イベント実行
		event_id = general.unpack_int(data[:4])
		script.run(self.pc, event_id)
	
	def do_09e2(self, data):
		#インベントリ移動
		iid = general.unpack_int(data[:4])
		part = general.unpack_byte(data[4])
		count = general.unpack_short(data[5:7])
		with self.pc.lock:
			if iid not in self.pc.item:
				print "[ map ] do_09e2 iid %d not in item list"%iid
				return
			self.pc.unset_equip(iid)
			self.pc.sort.item.remove(iid)
			self.pc.sort.item.append(iid)
			self.send("09e3", iid, part) #アイテム保管場所変更
		self.send("09e8", -1, -1, 1, 1) #アイテムを外す
		self.send("09e9", self.pc) #キャラの見た目を変更
	
	def do_09e7(self, data):
		#アイテム装備
		iid = general.unpack_int(data[:4])
		with self.pc.lock:
			if iid not in self.pc.item:
				print "[ map ] do_09e7 iid %d not in item list"%iid
				return
			unset_iid_list, set_part = self.pc.set_equip(iid)
			print "[ map ] item setup", self.pc.item.get(iid)
			#print unset_iid_list, set_part
			for i in unset_iid_list:
				self.pc.sort.item.remove(i)
				self.pc.sort.item.append(i)
				self.send("09e3", i, 0x02) #アイテム保管場所変更 #body
				#self.send("0203", pc.item[i], i, 0x02) #インベントリ情報
			if not set_part:
				#装備しようとする装備タイプが不明の場合
				self.send("09e8", iid, -1, -2, 1) #アイテム装備
			else:
				self.send("09e8", iid, set_part, 0, 1) #アイテム装備
				self.send("09e9", self.pc) #キャラの見た目を変更
	
	def do_0a16(self, data):
		#トレードキャンセル
		print "[ map ] trade: send cancel"
		self.send("0a19", self.pc) #自分・相手がOKやキャンセルを押した際に双方に送信される
		self.pc.reset_trade()
		self.send("0a1c") #トレード終了通知
	
	def do_0a14(self, data):
		#トレードのOK状態
		print "[ map ] trade: send ok"
		with self.pc.lock:
			self.pc.trade_state = -1
	
	def do_0a15(self, data):
		#トレードのTradeを押した際に送信
		print "[ map ]","trade: send trade"
		with self.pc.lock:
			self.pc.trade_state = 1
			self.pc.trade_return_list = []
			if self.pc.trade:
				for iid, count in self.pc.trade_list:
					item = self.pc.item.get(iid)
					if not item:
						continue
					if item.count < count:
						continue
					if self.pc.in_equip(iid):
						continue
					item.count -= count
					if item.count > 0:
						item_return = general.copy(item)
						item_return.count = count
						self.pc.trade_return_list.append(item_return)
						#self.send("09cf", item, iid) #アイテム個数変化
					else:
						self.pc.sort.item.remove(iid)
						item_return = self.pc.item.pop(iid)
						item_return.count = count
						self.pc.trade_return_list.append(item_return)
						self.send("09ce", iid) #インベントリからアイテム消去
			self.pc.trade = False
			self.pc.trade_list = []
			self.pc.trade_state = 0
			self.send("0a1c") #トレード終了通知
	
	def do_0a1b(self, data):
		#トレードウィンドウに置いたアイテム・金の情報を送信？
		print "[ map ]","trade send item list"
		iid_list = []
		count_list = []
		iid_count = general.unpack_byte(data[:1]); data = data[1:]
		#print "iid_count", iid_count
		for i in xrange(iid_count):
			iid_list.append(general.unpack_int(data[:4])); data = data[4:]
		count_count = general.unpack_byte(data[:1]); data = data[1:]
		#print "count_count", count_count
		for i in xrange(iid_count):
			count_list.append(general.unpack_short(data[:2])); data = data[2:]
		self.pc.trade_gold = general.unpack_int(data[:4])
		self.pc.trade_list = zip(iid_list, count_list)
		print "[ map ] self.pc.trade_list", self.pc.trade_list
		print "[ map ] self.pc.trade_gold", self.pc.trade_gold
	
	def do_09f7(self, data):
		#倉庫を閉じる
		print "[ map ] warehouse closed"
		self.pc.warehouse_open = None
	
	def do_09fb(self, data):
		#倉庫から取り出す
		item_iid = general.unpack_int(data[:4]); data = data[4:]
		item_count = general.unpack_short(data[:2])
		print "[ map ] take item from warehouse", item_iid, item_count
		with self.pc.lock:
			if self.pc.warehouse_open == None:
				#倉庫から取り出した時の結果 #倉庫を開けていません
				self.send("09fc", -1)
				return
			if item_iid not in self.pc.warehouse:
				#倉庫から取り出した時の結果 #指定されたアイテムは存在しません
				self.send("09fc", -2)
				return
			item = self.pc.warehouse[item_iid]
			if item.count < item_count:
				#倉庫から取り出した時の結果 #指定された数量が不正です
				self.send("09fc", -3)
				return
			item.count -= item_count
			if item.count <= 0:
				self.pc.sort.warehouse.remove(item_iid)
				self.pc.warehouse.pop(item_iid)
			if item.stock:
				script.item(self.pc, item.item_id, item_count)
			else:
				item_iid = self.pc.get_new_iid()
				item_take = general.copy(item)
				item_take.count = item_count
				item_take.warehouse = 0
				self.pc.sort.item.append(item_iid)
				self.pc.item[item_iid] = item_take
				self.send("09d4", item_take, item_iid, 0x02) #アイテム取得 #0x02: body
			#倉庫から取り出した時の結果 #成功
			self.send("09fc", 0)
	
	def do_09fd(self, data):
		#倉庫に預ける
		item_iid = general.unpack_int(data[:4]); data = data[4:]
		item_count = general.unpack_short(data[:2])
		print "[ map ] store item to warehouse", item_iid, item_count
		with self.pc.lock:
			if self.pc.warehouse_open == None:
				#倉庫に預けた時の結果 #倉庫を開けていません
				self.send("09fe", -1)
				return
			if item_iid not in self.pc.item:
				#倉庫に預けた時の結果 #指定されたアイテムは存在しません
				self.send("09fe", -2)
				return
			item = self.pc.item[item_iid]
			if item.count < item_count:
				#倉庫に預けた時の結果 #指定された数量が不正です
				self.send("09fe", -3)
			item.count -= item_count
			if item.count <= 0:
				self.pc.sort.item.remove(item_iid)
				self.pc.item.pop(item_iid)
				self.send("09ce", item_iid) #インベントリからアイテム消去
			else:
				self.send("09cf", item, item_iid) #アイテム個数変化
			item_iid = self.pc.get_new_iid()
			item_store = general.copy(item)
			item_store.count = item_count
			item_store.warehouse = self.pc.warehouse_open
			self.pc.sort.warehouse.append(item_iid)
			self.pc.warehouse[item_iid] = item_store
			self.send("09f9", item_store, item_iid, 30) #倉庫インベントリーデータ
			#倉庫に預けた時の結果 #成功
			self.send("09fe", 0)
	
	def do_09c4(self, data):
		#アイテム使用
		item_iid = general.unpack_int(data[:4]); data = data[4:]
		target_id = general.unpack_int(data[:4])
		with self.pc.lock:
			item = self.pc.item.get(item_iid)
			if not item:
				return
			event_id = item.eventid
		pc = users.get_pc_from_id(target_id)
		with pc.lock:
			if not pc.online:
				return
			script.run(pc, event_id)
	
	def do_0605(self, data):
		#NPCメッセージ(選択肢)の返信
		self.send("0606") #s0605で選択結果が通知された場合の応答
		with self.pc.lock:
			self.pc.select_result = general.unpack_byte(data[:1])
	
	def do_041a(self, data):
		#set kanban
		with self.pc.lock:
			self.pc.kanban = general.unpack_str(data)[0]
			self.send_map("041b", self.pc)