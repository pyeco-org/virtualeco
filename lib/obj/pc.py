#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
import traceback
import time
from lib import env
from lib import general
from lib import server
from lib import db
from lib import pets
from lib import users
from lib import script
from lib import dumpobj
from lib.obj import pc_data_lib

class PC:
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.id, self.name)
	
	def load(self):
		with self.lock:
			pc_data_lib.load(self)
	
	def save(self):
		with self.lock:
			pc_data_lib.save(self)
			#general.log(self, "save")
	
	def map_send(self, *args):
		if not self.user.map_client:
			general.log("[ pc  ] skip map_send", *args)
			return
		self.user.map_client.send(*args)
	
	def map_send_map(self, *args):
		if not self.user.map_client:
			general.log("[ pc  ] skip map_send_map", *args)
			return
		self.user.map_client.send_map(*args)
	
	def map_send_map_without_self(self, *args):
		if not self.user.map_client:
			general.log("[ pc  ] skip map_send_map_without_self", *args)
			return
		self.user.map_client.send_map_without_self(*args)
	
	def map_send_server(self, *args):
		if not self.user.map_client:
			general.log("[ pc  ] skip map_send_server", *args)
			return
		self.user.map_client.send_server(*args)
	
	def login_send(self, *args):
		if not self.user.login_client:
			general.log("[ pc  ] skip login_send", *args)
			return
		self.user.login_client.send(*args)
	
	def update_item_status(self):
		self.update_status()
		self.map_send("0230", self) #現在CAPA/PAYL
		self.map_send("0231", self) #最大CAPA/PAYL
	
	def update_equip_status(self):
		self.update_status()
		self.map_send("0230", self) #現在CAPA/PAYL
		self.map_send("0231", self) #最大CAPA/PAYL
		self.map_send_map("0221", self) #最大HP/MP/SP
		self.map_send_map("021c", self) #現在のHP/MP/SP/EP
		self.map_send("157c", self) #キャラの状態
		self.map_send("0212", self) #ステータス・補正・ボーナスポイント
		self.map_send("0217", self) #詳細ステータス
		self.map_send("0226", self, 0) #スキル一覧 一次職
		self.map_send("0226", self, 1) #スキル一覧 エキスパ
		self.map_send("022d", self) #HEARTスキル
		self.map_send("0223", self) #属性値
		self.map_send("0244", self) #ステータスウィンドウの職業
	
	def get_item_part(self, *args):
		with self.lock:
			return self._get_item_part(*args)
	def _get_item_part(self, iid):
		if not iid:
			return
		item = self.item.get(iid)
		if item is None:
			return
		for equip in (self.equip_std, self.equip_dem):
			if iid == equip.head:
				if item.check_type(general.HEAD_TYPE_LIST):
					return 0x06
				elif item.check_type(general.ACCESORY_HEAD_TYPE_LIST):
					return 0x07
			elif iid == equip.face:
				if item.check_type(general.FULLFACE_TYPE_LIST):
					return 0x06 #0x08 before ver315
				elif item.check_type(general.ACCESORY_FACE_TYPE_LIST):
					return 0x08 #0x09 before ver315
			elif iid == equip.chestacce:
				return 10
			elif iid == equip.tops:
				return 11
			elif iid == equip.bottoms:
				return 12
			elif iid == equip.backpack:
				return 13
			elif iid == equip.right:
				return 14
			elif iid == equip.left:
				return 15
			elif iid == equip.shoes:
				return 16
			elif iid == equip.socks:
				return 17
			elif iid == equip.pet:
				return 18
		return 0x02 #body
	
	def set_map(self, *args):
		with self.lock:
			return self._set_map(*args)
	def _set_map(self, map_id=None):
		if not map_id:
			map_id = self.map_id
		map_obj = db.map_obj.get(map_id)
		if not map_obj:
			return False
		#general.log(self, "set_map", map_obj)
		with self.user.lock:
			self.unset_pet()
			if map_id:
				self.map_send_map_without_self("1211", self) #PC消去
		self.map_id = map_id
		if self.map_obj:
			with self.map_obj.lock:
				self.map_obj.pc_list.remove(self)
		self.map_obj = map_obj
		with self.map_obj.lock:
			if self not in self.map_obj.pc_list:
				with self.map_obj.lock:
					self.map_obj.pc_list.append(self)
		return True
	
	def set_visible(self, visible):
		with self.lock:
			self.visible = True if visible else False
	
	def set_motion(self, motion_id, motion_loop):
		with self.lock:
			self.motion_id = motion_id
			self.motion_loop = True if motion_loop else False
		self.map_send_map("121c", self) #モーション通知
		#let pet motion refer master
		if not self.pet:
			return
		if motion_id == 135 and motion_loop:
			self.pet.wait_motion = 135 #座る
			self.pet.wait_motion_loop = True
			self.pet.wait_motion_time = time.time()+0.5
		elif self.pet.motion_id == 135:
			self.pet.wait_motion = 111 #立つ
			self.pet.wait_motion_loop = True
			self.pet.wait_motion_time = time.time()+0.5
	
	def set_coord(self, x, y):
		with self.lock:
			self.x = x #float, pack with unsigned byte
			self.y = y #float, pack with unsigned byte
			if self.x < 0: self.x += 256
			if self.y < 0: self.y += 256
			if not self.map_obj:
				return
			self.rawx = int((self.x - self.map_obj.centerx)*100.0)
			self.rawy = int((self.map_obj.centery - self.y)*100.0)
	def set_raw_coord(self, rawx, rawy):
		with self.lock:
			self.rawx = rawx
			self.rawy = rawy
			if not self.map_obj:
				return
			self.x = self.map_obj.centerx + rawx/100.0 #no int()
			self.y = self.map_obj.centery - rawy/100.0 #no int()
			if self.x < 0: self.x += 256
			if self.y < 0: self.y += 256
	
	def set_dir(self, d):
		with self.lock:
			self.dir = d
			self.rawdir = d*45
	def set_raw_dir(self, rawdir):
		with self.lock:
			self.rawdir = rawdir
			self.dir = int(round(rawdir/45.0, 0))
	
	def set_equip(self, *args):
		with self.lock:
			return self._set_equip(*args)
	def _set_equip(self, iid):
		item = self.item.get(iid)
		if not item:
			general.log_error("[ pc  ] set_equip iid %d not exist"%iid, self)
			return False
		unset_iid_list = []
		set_part = 0
		if item.check_type(general.HEAD_TYPE_LIST): #頭
			unset_iid_list.append(self.equip.head)
			self.equip.head = iid
			set_part = 6
		elif item.check_type(general.ACCESORY_HEAD_TYPE_LIST): #頭
			unset_iid_list.append(self.equip.head)
			self.equip.head = iid
			set_part = 7
		elif item.check_type(general.FULLFACE_TYPE_LIST): #顔
			unset_iid_list.append(self.equip.face)
			self.equip.face = iid
			set_part = 6 #8 before ver315
		elif item.check_type(general.ACCESORY_FACE_TYPE_LIST): #顔
			unset_iid_list.append(self.equip.face)
			self.equip.face = iid
			set_part = 8 #9 before ver315
		elif item.check_type(general.ACCESORY_TYPE_LIST): #胸アクセサリ
			unset_iid_list.append(self.equip.chestacce)
			self.equip.chestacce = iid
			set_part = 10
		elif item.check_type(general.ONEPIECE_TYPE_LIST): #...
			unset_iid_list.append(self.equip.tops)
			unset_iid_list.append(self.equip.bottoms)
			self.equip.tops = iid
			self.equip.bottoms = 0
			set_part = 11
		elif item.check_type(general.UPPER_TYPE_LIST): #上半身
			unset_iid_list.append(self.equip.tops)
			self.equip.tops = iid
			set_part = 11
		elif item.check_type(general.LOWER_TYPE_LIST): #下半身
			item_tops = self.item.get(self.equip.tops)
			if item_tops and item_tops.check_type(general.ONEPIECE_TYPE_LIST):
				unset_iid_list.append(self.equip.tops)
				self.equip.tops = 0
			unset_iid_list.append(self.equip.bottoms)
			self.equip.bottoms = iid
			set_part = 12
		elif item.check_type(general.BACKPACK_TYPE_LIST): #背中
			unset_iid_list.append(self.equip.backpack)
			self.equip.backpack = iid
			set_part = 13
		elif item.check_type(general.RIGHT_TYPE_LIST): #右手装備
			unset_iid_list.append(self.equip.right)
			self.equip.right = iid
			set_part = 14
		elif item.check_type(general.LEFT_TYPE_LIST): #左手装備
			unset_iid_list.append(self.equip.left)
			self.equip.left = iid
			set_part = 15
		elif item.check_type(general.BOOTS_TYPE_LIST): #靴
			unset_iid_list.append(self.equip.shoes)
			self.equip.shoes = iid
			set_part = 16
		elif item.check_type(general.SOCKS_TYPE_LIST): #靴下
			unset_iid_list.append(self.equip.socks)
			self.equip.socks = iid
			set_part = 17
		elif item.check_type(general.PET_TYPE_LIST): #ペット
			unset_iid_list.append(self.equip.pet)
			self.unset_pet()
			self.equip.pet = iid
			self.set_pet()
			set_part = 18
		else: #装備しようとする装備タイプが不明の場合
			general.log_error("[ pc  ] set_equip unknow item type", item)
			self.map_send("09e8", iid, -1, -2, 1) #アイテム装備
			return False
		general.log("[ pc  ] set_equip", item)
		unset_iid_list = filter(None, unset_iid_list)
		for i in unset_iid_list:
			self.sort.item.remove(i)
			self.sort.item.append(i)
			self.map_send("09e3", i, 0x02) #アイテム保管場所変更 #body
			#self.map_send("0203", self.item[i], i, 0x02) #インベントリ情報
		self.map_send("09e8", iid, set_part, 0, 1) #アイテム装備
		self.map_send_map("09e9", self) #キャラの見た目を変更
		#self.map_send_map_without_self("020e", self.pc) #キャラ情報
		self.update_equip_status()
		return True
	
	def unset_equip(self, *args):
		with self.lock:
			return self._unset_equip(*args)
	def _unset_equip(self, iid, part):
		if iid == 0:
			general.log_error("[ pc  ] unset_equip iid == 0", self)
			return False
		if iid not in self.item:
			general.log_error("[ pc  ] unset_equip iid %d not exist"%iid, self)
			return False
		if self.equip.pet == iid:
			self.unset_pet()
		for attr in general.EQUIP_ATTR_LIST:
			if getattr(self.equip, attr) == iid:
				setattr(self.equip, attr, 0)
		general.log_error("[ pc  ] unset_equip iid %d"%iid)
		self.sort.item.remove(iid)
		self.sort.item.append(iid)
		self.map_send("09e3", iid, part) #アイテム保管場所変更
		self.map_send("09e8", -1, -1, 1, 1) #アイテムを外す
		self.map_send_map("09e9", self) #キャラの見た目を変更
		self.update_equip_status()
		return True
	
	def unset_all_equip(self):
		with self.lock:
			#part body 0x02
			for attr in general.EQUIP_ATTR_LIST:
				i = getattr(self.equip, attr)
				if i:
					self._unset_equip(i, 0x02)
	
	def in_equip(self, iid):
		if iid == 0:
			return
		for equip in (self.equip_std, self.equip_dem):
			for attr in general.EQUIP_ATTR_LIST:
				if getattr(equip, attr) == iid:
					return True
		return False
	
	def get_equip_list(self):
		with self.lock:
			item_list = []
			for attr in general.EQUIP_ATTR_LIST:
				i = getattr(self.equip, attr)
				if i:
					item_list.append(self.item.get(i))
		return filter(None, item_list)
	
	def item_append(self, item, place=0x02):
		if len(self.item) >= env.MAX_ITEM_STOCK:
			script.msg(self, "item_append error: stock limit")
			return item
		#0x02: body
		with self.lock:
			item_iid = general.make_id(self.sort.item+self.sort.warehouse)
			self.item[item_iid] = item
			self.sort.item.append(item_iid)
			if self.online:
				#アイテム取得
				self.map_send("09d4", item, item_iid, place)
				script.msg(self, "%sを%s個入手しました"%(item.name, item.count))
	
	def item_pop(self, iid):
		with self.lock:
			try:
				item = self.item.pop(iid)
				self.sort.item.remove(iid)
			except KeyError:
				general.log_error(traceback.format_exc())
				return None
			if self.online:
				#インベントリからアイテム消去
				self.map_send("09ce", iid)
				script.msg(self, "%sを%s個失いました"%(item.name, item.count))
		return item
	
	def warehouse_append(self, item):
		if len(self.warehouse) >= env.MAX_WAREHOURSE_STOCK:
			script.msg(self, "warehouse_append error: stock limit")
			return item
		with self.lock:
			item_iid = general.make_id(self.sort.item+self.sort.warehouse)
			self.warehouse[item_iid] = item
			self.sort.warehouse.append(item_iid)
			if self.online:
				#倉庫インベントリーデータ
				self.map_send("09f9", item, item_iid, 30)
				script.msg(self, "%sを%s個預りました"%(item.name, item.count))
	
	def warehouse_pop(self, iid):
		with self.lock:
			try:
				item = self.warehouse.pop(iid)
				self.sort.warehouse.remove(iid)
			except KeyError:
				general.log_error(traceback.format_exc())
				return None
			if self.online:
				script.msg(self, "%sを%s個取り出しました"%(item.name, item.count))
		return item
	
	def get_trade_target(self):
		if not self.trade_target_id:
			return None
		if not self.online:
			general.log("[ pc  ] get_trade_target: not self.online")
			return False
		p = users.get_pc_from_id(self.trade_target_id)
		if not p:
			general.log("[ pc  ] get_trade_target: not p")
			return False
		if not p.online:
			general.log("[ pc  ] get_trade_target: not p.online")
			return False
		if self.map_id != p.map_id:
			general.log("[ pc  ] get_trade_target: self.map_id != p.map_id")
			return False
		return p
	
	def cancel_trade(self):
		with self.lock and self.user.lock:
			if not self.online:
				self.reset_trade()
				return
			general.log("[ pc  ] cancel_trade")
			p = self.get_trade_target()
			#自分・相手がOKやキャンセルを押した際に双方に送信される
			self.map_send("0a19", self)
			self.reset_trade()
			self.map_send("0a1c") #トレード終了通知
			if not p:
				return
			with p.lock and p.user.lock:
				#自分・相手がOKやキャンセルを押した際に双方に送信される
				p.map_send("0a19", p)
				p.reset_trade()
				p.map_send("0a1c") #トレード終了通知
	
	def set_trade_ok(self):
		#won't send item list, item list will send when call set_trade_list
		with self.lock:
			self.trade_state = -1 #OK押した状態
			p = self.get_trade_target()
			if not p:
				return
			with p and p.user.lock:
				#自分・相手がOKやキャンセルを押した際に双方に送信される
				self.map_send("0a19", self, p)
				#自分・相手がOKやキャンセルを押した際に双方に送信される
				p.map_send("0a19", p, self)
	
	def set_trade_list(self, trade_gold, trade_list):
		with self.lock and self.user.lock:
			if not self.online:
				return
			self.trade_gold = trade_gold
			self.trade_list = trade_list
			general.log("[ pc  ] self.trade_gold", self.trade_gold)
			general.log("[ pc  ] self.trade_list", self.trade_list)
			if not self.check_trade_list:
				self.cancel_trade()
			p = self.get_trade_target()
			if p is False:
				self.cancel_trade()
			elif p is None:
				return
			with p.lock and p.user.lock:
				p.map_send("0a1f", self.trade_gold) #trade gold
				p.map_send("0a20") #trade item header
				for iid, count in self.trade_list:
					item = self.item.get(iid)
					p.map_send("0a1e", item, count)
				p.map_send("0a21") #trade item footer
	
	def check_trade_list(self):
		with self.lock:
			if not self.online:
				return
			if self.trade_gold > self.gold:
				return False
			for iid, count in self.trade_list:
				item = self.item.get(iid)
				if not item:
					return False
				if item.count < count:
					return False
				if self.in_equip(iid):
					return False
		return True
	
	def set_trade_return(self):
		#move item and gold to trade_return_list and trade_return_gold
		#must check_trade_list before
		with self.lock and self.user.lock:
			if not self.online:
				return
			general.log("[ pc  ] set_trade_return")
			script.takegold(self, self.trade_gold)
			self.trade_return_gold = self.trade_gold
			for iid, count in self.trade_list:
				item = self.item.get(iid)
				if item.count > count:
					item.count -= count
					item_return = general.copy(item)
					item_return.count = count
					self.trade_return_list.append(item_return)
					#self.map_send("09cf", item, iid) #アイテム個数変化
					script.msg(self, "%sを%s個失いました"%(item.name, count))
				else:
					item_return = self.item_pop(iid)
					item_return.count = count
					self.trade_return_list.append(item_return)
	
	def set_trade_finish(self):
		with self.lock and self.user.lock:
			if not self.online:
				return
			general.log("[ pc  ] set_trade_finish")
			return self._set_trade_finish()
	def _set_trade_finish(self):
		if not self.check_trade_list():
			self.cancel_trade()
			return
		if not self.trade:
			return
		self.trade_state = 1 #トレード完了してる状態
		p = self.get_trade_target()
		if p:
			with p.lock and p.user.lock:
				if not p.trade:
					return
				if len(self.item)+len(p.trade_list) > env.MAX_ITEM_STOCK:
					script.msg(self, "trade error: self stock limit")
					script.msg(p, "trade error: target stock limit")
					self.cancel_trade()
					p.cancel_trade()
					return
				if len(p.item)+len(self.trade_list) > env.MAX_ITEM_STOCK:
					script.msg(self, "trade error: target stock limit")
					script.msg(p, "trade error: self stock limit")
					self.cancel_trade()
					p.cancel_trade()
					return
				if p.trade_state == 1: #exchange item and gold
					if not p.check_trade_list():
						self.cancel_trade()
						return
					self.set_trade_return()
					p.set_trade_return()
					if self.trade_return_gold:
						script.gold(p, self.trade_return_gold)
					for item in self.trade_return_list:
						if item.stock:
							script.item(p, item.item_id, item.count)
						else:
							p.item_append(item)
					if p.trade_return_gold:
						script.gold(self, p.trade_return_gold)
					for item in p.trade_return_list:
						if item.stock:
							script.item(self, item.item_id, item.count)
						else:
							self.item_append(item)
					self.reset_trade()
					p.reset_trade()
					self.map_send("0a1c") #トレード終了通知
					p.map_send("0a1c") #トレード終了通知
					self.update_item_status()
					p.update_item_status()
					script.update_item(self)
					script.update_item(p)
				else: #send trade status
					#自分・相手がOKやキャンセルを押した際に双方に送信される
					self.map_send("0a19", self, p)
					#自分・相手がOKやキャンセルを押した際に双方に送信される
					p.map_send("0a19", p, self)
		elif p is False:
			#target offline or map changed
			self.cancel_trade()
		else: #p is None: npctrade
			self.set_trade_return()
			self.reset_trade(False) #don't clear return list
			self.map_send("0a1c") #トレード終了通知
			self.update_item_status()
			script.update_item(self)
	
	def reset_trade(self, reset_return=True):
		with self.lock:
			self.trade = False
			self.trade_state = 0 #OK押してない状態
			self.trade_gold = 0
			self.trade_list = []
			if reset_return:
				self.trade_return_gold = 0
				self.trade_return_list = []
			self.trade_target_id = 0 #target id, = 0 if npc
	
	def reset_login(self):
		self.reset_map()
	
	def reset_map(self):
		with self.lock:
			if self.map_obj:
				if self.online:
					self.unset_pet(True)
					#PC消去
					script.send_map_obj(self.map_obj, (self,), "1211", self)
				with self.map_obj.lock:
					self.map_obj.pc_list.remove(self)
			self.online = False
			self.visible = False
			self.size = 1000
			self.motion_id = 111
			self.motion_loop = False
			self.rawx = 0
			self.rawy = 0
			self.rawdir = 0
			self.battlestatus = 0
			self.wrprank = 0
			self.event_id = 0
			self.item_event_id = 0
			#self.loginevent = False
			self.logout = False
			self.pet = None #Pet()
			self.kanban = ""
			self.map_obj = None
			self.warehouse_open = None #warehouse_id
			self.shop_open = None #shop_id or shop_item_list
			self.select_result = None
			self.reset_trade()
	
	def set_pet(self):
		return pets.set_pet(self)
	
	def unset_pet(self, logout=False):
		return pets.unset_pet(self, logout)
	
	def set_battlestatus(self, i):
		self.battlestatus = int(i)
		self.map_send_map("0fa6", self) #戦闘状態変更通知
	
	def exp_add(self, exp, job_exp):
		#self.exp += exp
		#self.job_exp += job_exp
		script.msg(self, "基本経験値 %s、職業経験値 %sを取得しました"%(exp, job_exp))
	
	def dem_form_change(self, status):
		if self.race != 3:
			self.map_send("1e7e", -1, 0) #dem form change failed
			return False
		with self.lock:
			#if not stable, it will back to unset all equip before change
			#self.unset_all_equip()
			if status:
				self.equip = self.equip_dem
			else:
				self.equip = self.equip_std
			self.form = status
			script.update(self)
			self.map_send("1e7e", 0, status) #dem form change success
		return True
	
	def dem_form_status(self):
		return (self.race == 3 and self.form != 0)
	
	def get_status(self, LV, STR, DEX, INT, VIT, AGI, MAG):
		def get_base_status(self):
			status.minatk1 = int(STR+(STR/9)**2)
			status.minatk2 = status.minatk1
			status.minatk3 = status.minatk1
			status.maxatk1 = int(((STR+14)/5)**2)
			status.maxatk2 = status.maxatk1
			status.maxatk3 = status.maxatk1
			status.minmatk = int(MAG+((MAG+9)/8)**2)
			status.maxmatk = int(MAG+((MAG+17)/6)**2)
			status.shit = int(DEX+DEX/10*11+LV+3)
			status.lhit = int(INT+INT/10*11+LV+3)
			status.mhit = status.lhit #mag hit
			status.chit = int((DEX+1)/8) #critical hit
			status.leftdef = int(VIT/3+(VIT/9)**2)
			status.leftmdef = int(INT/3+VIT/4)
			status.savoid = int(AGI+((AGI+18)/9)**2+LV/3-1)
			status.lavoid = int(INT*5/3+AGI+LV/3+3)
			status.aspd = int(AGI*3+((AGI+63)/9)**2+129)
			status.cspd = int(DEX*3+((DEX+63)/9)**2+129)
			status.maxhp = int(VIT*3+(VIT/5)**2+LV*2+(LV/5)**2+50)
			status.maxmp = int(MAG*3+LV+(LV/9)**2+30)
			status.maxsp = int(INT+VIT+LV+(LV/9)**2+20)
			status.maxpayl = STR*2.0/3.0+VIT/3.0+400
			status.maxcapa = DEX/5.0+INT/10.0+200
			status.hpheal = int(100+VIT/3)
			status.mpheal = int(100+MAG/3)
			status.spheal = int(100+(INT+VIT)/6)
		def get_race_status(self):
			if self.race == 0: #エミル
				status.maxpayl = int(status.maxpayl*1.3)
			elif self.race == 1: #タイタニア
				status.maxpayl = int(status.maxpayl*0.9)
			elif self.race == 2: #ドミニオン
				status.maxpayl = int(status.maxpayl*1.1)
		def get_job_status(self):
			job = db.job.get(self.job)
			if not job:
				general.log_error("[ pc  ] unknow job id:", self.job)
				return
			status.maxhp = int(status.maxhp*job.hp_rate)
			status.maxmp = int(status.maxmp*job.mp_rate)
			status.maxsp = int(status.maxsp*job.sp_rate)
			status.maxpayl = status.maxpayl*job.payl_rate
			status.maxcapa = status.maxcapa*job.capa_rate
		def get_equip_status(self):
			status.rightdef = 0
			status.rightmdef = 0
			for item in self.get_equip_list(): #filter include False
				status.minatk1 += int(item.atk1)
				status.minatk2 += int(item.atk2)
				status.minatk3 += int(item.atk3)
				status.maxatk1 += int(item.atk1)
				status.maxatk2 += int(item.atk2)
				status.maxatk3 += int(item.atk3)
				status.minmatk += int(item.matk)
				status.maxmatk += int(item.matk)
				status.shit += int(item.s_hit)
				status.lhit += int(item.l_hit)
				status.mhit += int(item.magic_hit)
				status.chit += int(item.critical_hit)
				status.rightdef += int(item.DEF)
				status.rightmdef += int(item.mdef)
				status.savoid += int(item.s_avoid)
				status.lavoid += int(item.l_avoid)
				#status.aspd += int(item.aspd)
				#status.cspd += int(item.cspd)
				status.maxhp += int(item.hp)
				status.maxmp += int(item.mp)
				status.maxsp += int(item.sp)
				status.maxpayl += int(item.payl_add)
				status.maxcapa += int(item.capa_add)
				status.hpheal += int(item.heal_hp)
				status.mpheal += int(item.heal_mp)
				#status.spheal += int(item.heal_sp)
				status.speed += int(item.speed)
		def get_item_status(self):
			status.capa = 0
			status.payl = 0
			for item in self.item.itervalues():
				status.capa += item.capa
				status.payl += item.weight
			status.capa /= 10.0
			status.payl /= 10.0
		def get_skill_status(self):
			pass
		def get_variable_status(self):
			if status.hp is None:
				status.hp = status.maxhp
			if status.mp is None:
				status.mp = status.maxmp
			if status.sp is None:
				status.sp = status.maxsp
			status.delay_attack = 2*(1-status.aspd/1000.0)
		status = PC.Status()
		with self.lock:
			get_base_status(self)
			get_race_status(self)
			get_job_status(self)
			get_equip_status(self)
			get_item_status(self)
			get_skill_status(self)
			get_variable_status(self)
		return status
	
	def update_status(self):
		STR = self.str + self.stradd
		DEX = self.dex + self.dexadd
		INT = self.int + self.intadd
		VIT = self.vit + self.vitadd
		AGI = self.agi + self.agiadd
		MAG = self.mag + self.magadd
		LV = self.lv_base
		with self.lock:
			status = self.get_status(LV, STR, DEX, INT, VIT, AGI, MAG)
			del self.status
			self.status = status
	
	def reset_attack(self):
		if not self.attack:
			return
		print "[ pc  ] reset_attack from %s"%traceback.extract_stack()[-2][2]
		self.attack = False
		self.attack_target = None
		self.attack_delay = 0
	
	def __init__(self, user, path):
		self.path = path
		self.lock = threading.RLock()
		self.user = user
		self.online = False
		self.visible = False
		self.map_id = 0
		self.map_obj = None
		self.attack = False
		self.attack_target = None
		self.attack_delay = 0
		self.sort = PC.Sort()
		self.equip_std = PC.Equip()
		self.equip_dem = PC.Equip()
		self.equip = self.equip_std
		self.status = PC.Status()
		self.reset_login()
		self.load()
		#self.update_status() #on login
	
	class Sort:
		def __init__(self):
			pass
	class Equip:
		def __init__(self):
			for attr in general.EQUIP_ATTR_LIST:
				setattr(self, attr, 0)
	class Status:
		def __init__(self):
			self.maxhp = 0
			self.maxmp = 0
			self.maxsp = 0
			self.maxep = 30
			self.hp = None #if None: hp = maxhp
			self.mp = None #if None: mp = maxmp
			self.sp = None #if None: sp = maxsp
			self.ep = 0
			
			self.minatk1 = 0
			self.minatk2 = 0
			self.minatk3 = 0
			self.maxatk1 = 0
			self.maxatk2 = 0
			self.maxatk3 = 0
			self.minmatk = 0
			self.maxmatk = 0
			
			self.leftdef = 0
			self.rightdef = 0
			self.leftmdef = 0
			self.rightmdef = 0
			self.shit = 0
			self.lhit = 0
			self.mhit = 0
			self.chit = 0
			self.savoid = 0
			self.lavoid = 0
			
			self.hpheal = 0
			self.mpheal = 0
			self.spheal = 0
			self.aspd = 0
			self.cspd = 0
			self.speed = 410 #move speed
			
			self.maxcapa = 0
			self.maxpayl = 0
			self.capa = 0
			self.payl = 0
			
			self.maxrightcapa = 0
			self.maxleftcapa = 0
			self.maxbackcapa = 0
			self.maxrightpayl = 0
			self.maxleftpayl = 0
			self.maxbackpayl = 0
			self.rightcapa = 0
			self.leftcapa = 0
			self.backcapa = 0
			self.rightpayl = 0
			self.leftpayl = 0
			self.backpayl = 0