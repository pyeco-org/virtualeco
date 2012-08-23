#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import threading
import traceback
from lib import general
from lib import server
from lib import db
from lib import pets
from lib import users
from lib import script

class PC:
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))
	
	def load(self):
		with self.lock:
			self._load()
	def _load(self):
		cfg = general.get_config(self.path, base=users.USER_DIR)
		self.id = cfg.getint("main","id")
		self.name = cfg.get("main","name")
		self.gmlevel = cfg.getint("main","gmlevel")
		self.race = cfg.getint("main","race")
		self.form = cfg.getint("main","form")
		self.gender = cfg.getint("main","gender")
		self.hair = cfg.getint("main","hair")
		self.haircolor =cfg.getint("main","haircolor")
		self.wig = cfg.getint("main","wig")
		self.face = cfg.getint("main","face")
		self.base_lv = cfg.getint("main","base_lv")
		self.ex = cfg.getint("main","ex")
		self.wing = cfg.getint("main","wing")
		self.wingcolor = cfg.getint("main","wingcolor")
		self.job = cfg.getint("main","job")
		self.map_id = cfg.getint("main","map_id")
		self.lv_base = cfg.getint("main","lv_base")
		self.lv_job1 = cfg.getint("main","lv_job1")
		self.lv_job2x = cfg.getint("main","lv_job2x")
		self.lv_job2t = cfg.getint("main","lv_job2t")
		self.lv_job3 = cfg.getint("main","lv_job3")
		self.gold = cfg.getint("main","gold")
		self.x = cfg.getfloat("main","x")
		self.y = cfg.getfloat("main","y")
		self.dir = cfg.getint("main","dir")
		self.str = cfg.getint("status","str")
		self.dex = cfg.getint("status","dex")
		self.int = cfg.getint("status","int")
		self.vit = cfg.getint("status","vit")
		self.agi = cfg.getint("status","agi")
		self.mag = cfg.getint("status","mag")
		self.stradd = cfg.getint("status","stradd")
		self.dexadd = cfg.getint("status","dexadd")
		self.intadd = cfg.getint("status","intadd")
		self.vitadd = cfg.getint("status","vitadd")
		self.agiadd = cfg.getint("status","agiadd")
		self.magadd = cfg.getint("status","magadd")
		#{item_iid: item_object, ...}
		self.item = {}
		self.sort.item = general.str_to_list(cfg.get("sort", "item"))
		for i in self.sort.item:
			itemcfg = general.str_to_list(cfg.get("item", str(i)))
			item = general.get_item(itemcfg[0])
			item.count = itemcfg[1]
			self.item[i] = item
		#{item_iid: item_object, ...}
		self.warehouse = {}
		self.sort.warehouse = general.str_to_list(cfg.get("sort", "warehouse"))
		for i in self.sort.warehouse:
			itemcfg = general.str_to_list(cfg.get("warehouse", str(i)))
			item = general.get_item(itemcfg[0])
			item.count = itemcfg[1]
			item.warehouse = itemcfg[2]
			self.warehouse[i] = item
		#equip.place = iid
		self.equip.head = cfg.getint("equip","head")
		self.equip.face = cfg.getint("equip","face")
		self.equip.chestacce = cfg.getint("equip","chestacce")
		self.equip.tops = cfg.getint("equip","tops")
		self.equip.bottoms = cfg.getint("equip","bottoms")
		self.equip.backpack = cfg.getint("equip","backpack")
		self.equip.right = cfg.getint("equip","right")
		self.equip.left = cfg.getint("equip","left")
		self.equip.shoes = cfg.getint("equip","shoes")
		self.equip.socks = cfg.getint("equip","socks")
		self.equip.pet = cfg.getint("equip","pet")
		#{name: value, ...}
		self.dic = {}
		for option in cfg.options("dic"):
			self.dic[option] = cfg.get("dic", option)
		#[skill_id, ...]
		self.skill_list = general.str_to_list(cfg.get("skill", "list"))
	
	def save(self):
		with self.lock:
			self._save()
			#general.log(self, "save")
	def _save(self):
		cfg = general.get_config()
		cfg.add_section("main")
		cfg.set("main", "id", str(self.id))
		cfg.set("main", "name", str(self.name))
		cfg.set("main", "gmlevel", str(self.gmlevel))
		cfg.set("main", "race", str(self.race))
		cfg.set("main", "form", str(self.form))
		cfg.set("main", "gender", str(self.gender))
		cfg.set("main", "hair", str(self.hair))
		cfg.set("main", "haircolor", str(self.haircolor))
		cfg.set("main", "wig", str(self.wig))
		cfg.set("main", "face", str(self.face))
		cfg.set("main", "base_lv", str(self.base_lv))
		cfg.set("main", "ex", str(self.ex))
		cfg.set("main", "wing", str(self.wing))
		cfg.set("main", "wingcolor", str(self.wingcolor))
		cfg.set("main", "job", str(self.job))
		cfg.set("main", "map_id", str(self.map_id))
		cfg.set("main", "lv_base", str(self.lv_base))
		cfg.set("main", "lv_job1", str(self.lv_job1))
		cfg.set("main", "lv_job2x", str(self.lv_job2x))
		cfg.set("main", "lv_job2t", str(self.lv_job2t))
		cfg.set("main", "lv_job3", str(self.lv_job3))
		cfg.set("main", "gold", str(self.gold))
		cfg.set("main", "x", str(self.x))
		cfg.set("main", "y", str(self.y))
		cfg.set("main", "dir", str(self.dir))
		cfg.add_section("status")
		cfg.set("status", "str", str(self.str))
		cfg.set("status", "dex", str(self.dex))
		cfg.set("status", "int", str(self.int))
		cfg.set("status", "vit", str(self.vit))
		cfg.set("status", "agi", str(self.agi))
		cfg.set("status", "mag", str(self.mag))
		cfg.set("status", "stradd", str(self.stradd))
		cfg.set("status", "dexadd", str(self.dexadd))
		cfg.set("status", "intadd", str(self.intadd))
		cfg.set("status", "vitadd", str(self.vitadd))
		cfg.set("status", "agiadd", str(self.agiadd))
		cfg.set("status", "magadd", str(self.magadd))
		cfg.add_section("equip")
		cfg.set("equip", "head", str(self.equip.head))
		cfg.set("equip", "face", str(self.equip.face))
		cfg.set("equip", "chestacce", str(self.equip.chestacce))
		cfg.set("equip", "tops", str(self.equip.tops))
		cfg.set("equip", "bottoms", str(self.equip.bottoms))
		cfg.set("equip", "backpack", str(self.equip.backpack))
		cfg.set("equip", "right", str(self.equip.right))
		cfg.set("equip", "left", str(self.equip.left))
		cfg.set("equip", "shoes", str(self.equip.shoes))
		cfg.set("equip", "socks", str(self.equip.socks))
		cfg.set("equip", "pet", str(self.equip.pet))
		#"iid,iid,iid, ..."
		cfg.add_section("sort")
		cfg.set("sort", "item", general.list_to_str(self.sort.item))
		cfg.set("sort", "warehouse", general.list_to_str(self.sort.warehouse))
		#"iid = id,count"
		cfg.add_section("item")
		for i in self.item:
			cfg.set("item", str(i),
				general.list_to_str((
				self.item[i].item_id,
				self.item[i].count)))
		#"iid = id,count,warehouse"
		cfg.add_section("warehouse")
		for i in self.warehouse:
			cfg.set("warehouse", str(i),
				general.list_to_str((
				self.warehouse[i].item_id,
				self.warehouse[i].count,
				self.warehouse[i].warehouse)))
		#"name = value"
		cfg.add_section("dic")
		for name, value in self.dic.iteritems():
			cfg.set("dic", str(name), str(value))
		#"skill_id,skill_id,skill_id, ..."
		cfg.add_section("skill")
		cfg.set("skill", "list", general.list_to_str(self.skill_list))
		#
		cfg.write(open(self.path, "wb", base=users.USER_DIR))
	
	def get_item_part(self, *args):
		with self.lock:
			return self._get_item_part(*args)
	def _get_item_part(self, iid):
		if not iid: return
		if iid not in self.item: return
		part = 0x02 #body
		item = self.item[iid]
		if iid == self.equip.head:
			if item.check_type("HELM")			: part = 6
			elif item.check_type("ACCESORY_HEAD")	: part = 7
		elif iid == self.equip.face:
			if item.check_type("FULLFACE")		: part = 6 #8 before ver315
			elif item.check_type("ACCESORY_FACE")	: part = 8 #9 before ver315
		elif iid == self.equip.chestacce			: part = 10
		elif iid == self.equip.tops				: part = 11
		elif iid == self.equip.bottoms			: part = 12
		elif iid == self.equip.backpack			: part = 13
		elif iid == self.equip.right				: part = 14
		elif iid == self.equip.left				: part = 15
		elif iid == self.equip.shoes				: part = 16
		elif iid == self.equip.socks				: part = 17
		elif iid == self.equip.pet				: part = 18
		return part
	
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
			if self.user.map_client:
				self.unset_pet()
				if map_id:
					self.user.map_client.send_map_without_self("1211", self) #PC消去
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
		unset_iid_list = []
		set_part = 0
		item = self.item.get(iid)
		if not item: return unset_iid_list, set_part
		if item.check_type("HELM"): #頭
			unset_iid_list.append(self.equip.head)
			self.equip.head = iid
			set_part = 6
		elif item.check_type("ACCESORY_HEAD"): #頭
			unset_iid_list.append(self.equip.head)
			self.equip.head = iid
			set_part = 7
		elif item.check_type("FULLFACE"): #顔
			unset_iid_list.append(self.equip.face)
			self.equip.face = iid
			set_part = 6 #8 before ver315
		elif item.check_type("ACCESORY_FACE"): #顔
			unset_iid_list.append(self.equip.face)
			self.equip.face = iid
			set_part = 8 #9 before ver315
		elif item.check_type(general.ACCESORY_TYPE_LIST): #胸アクセサリ
			unset_iid_list.append(self.equip.chestacce)
			self.equip.chestacce = iid
			set_part = 10
		elif item.check_type("ONEPIECE"): #...
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
			if item_tops and item_tops.check_type("ONEPIECE"):
				unset_iid_list.append(self.equip.tops)
				self.equip.tops = 0
			unset_iid_list.append(self.equip.bottoms)
			self.equip.bottoms = iid
			set_part = 12
		elif item.check_type("BACKPACK"): #背中
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
		elif item.check_type("SOCKS"): #靴下
			unset_iid_list.append(self.equip.socks)
			self.equip.socks = iid
			set_part = 17
		elif item.check_type(general.PET_TYPE_LIST): #ペット
			unset_iid_list.append(self.equip.pet)
			self.unset_pet()
			self.equip.pet = iid
			self.set_pet()
			set_part = 18
		return filter(None, unset_iid_list), set_part
	
	def unset_equip(self, *args):
		with self.lock:
			return self._unset_equip(*args)
	def _unset_equip(self, iid):
		if iid == 0:
			return
		elif self.equip.head == iid:
			self.equip.head = 0
		elif self.equip.face == iid:
			self.equip.face = 0
		elif self.equip.chestacce == iid:
			self.equip.chestacce = 0
		elif self.equip.tops == iid:
			self.equip.tops = 0
		elif self.equip.bottoms == iid:
			self.equip.bottoms = 0
		elif self.equip.backpack == iid:
			self.equip.backpack = 0
		elif self.equip.right == iid:
			self.equip.right = 0
		elif self.equip.left == iid:
			self.equip.left = 0
		elif self.equip.shoes == iid:
			self.equip.shoes = 0
		elif self.equip.socks == iid:
			self.equip.socks = 0
		elif self.equip.pet == iid:
			self.equip.pet = 0
			self.unset_pet()
	
	def in_equip(self, iid):
		if iid == 0: return
		elif self.equip.head == iid: return True
		elif self.equip.face == iid: return True
		elif self.equip.chestacce == iid: return True
		elif self.equip.tops == iid: return True
		elif self.equip.bottoms == iid: return True
		elif self.equip.backpack == iid: return True
		elif self.equip.right == iid: return True
		elif self.equip.left == iid: return True
		elif self.equip.shoes == iid: return True
		elif self.equip.socks == iid: return True
		elif self.equip.pet == iid: return True
		else: return False
	
	def get_equip_list(self):
		with self.lock:
			item_list = []
			item_list.append(self.equip.head and self.item.get(self.equip.head))
			item_list.append(self.equip.face and self.item.get(self.equip.face))
			item_list.append(
				self.equip.chestacce and self.item.get(self.equip.chestacce))
			item_list.append(self.equip.tops and self.item.get(self.equip.tops))
			item_list.append(
				self.equip.bottoms and self.item.get(self.equip.bottoms))
			item_list.append(
				self.equip.backpack and self.item.get(self.equip.backpack))
			item_list.append(self.equip.right and self.item.get(self.equip.right))
			item_list.append(self.equip.left and self.item.get(self.equip.left))
			item_list.append(self.equip.shoes and self.item.get(self.equip.shoes))
			item_list.append(self.equip.socks and self.item.get(self.equip.socks))
			#item_list.append(self.equip.pet and self.item.get(self.equip.pet))
			return filter(None, item_list)
	
	def item_append(self, item, place=0x02):
		#0x02: body
		with self.lock:
			item_iid = general.make_id(self.sort.item+self.sort.warehouse)
			self.item[item_iid] = item
			self.sort.item.append(item_iid)
			if self.online:
				#アイテム取得
				self.user.map_client.send("09d4", item, item_iid, place)
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
				self.user.map_client.send("09ce", iid)
				script.msg(self, "%sを%s個失いました"%(item.name, item.count))
		return item
	
	def warehouse_append(self, item):
		with self.lock:
			item_iid = general.make_id(self.sort.item+self.sort.warehouse)
			self.warehouse[item_iid] = item
			self.sort.warehouse.append(item_iid)
			if self.online:
				#倉庫インベントリーデータ
				self.user.map_client.send("09f9", item, item_iid, 30)
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
			self.user.map_client.send("0a19", self)
			self.reset_trade()
			self.user.map_client.send("0a1c") #トレード終了通知
			if not p:
				return
			with p.lock and p.user.lock:
				#自分・相手がOKやキャンセルを押した際に双方に送信される
				p.user.map_client.send("0a19", p)
				p.reset_trade()
				p.user.map_client.send("0a1c") #トレード終了通知
	
	def set_trade_ok(self):
		#won't send item list, item list will send when call set_trade_list
		with self.lock:
			self.trade_state = -1 #OK押した状態
			p = self.get_trade_target()
			if not p:
				return
			with p and p.user.lock:
				#自分・相手がOKやキャンセルを押した際に双方に送信される
				self.user.map_client.send("0a19", self, p)
				#自分・相手がOKやキャンセルを押した際に双方に送信される
				p.user.map_client.send("0a19", p, self)
	
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
				p.user.map_client.send("0a1f", self.trade_gold) #trade gold
				p.user.map_client.send("0a20") #trade item header
				for iid, count in self.trade_list:
					item = self.item.get(iid)
					p.user.map_client.send("0a1e", item, count)
				p.user.map_client.send("0a21") #trade item footer
	
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
					#self.user.map_client.send("09cf", item, iid) #アイテム個数変化
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
		self.trade_state = 1 #トレード完了してる状態
		p = self.get_trade_target()
		if p:
			with p.lock and p.user.lock:
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
					self.user.map_client.send("0a1c") #トレード終了通知
					p.user.map_client.send("0a1c") #トレード終了通知
					self.user.map_client.update_item_status()
					p.user.map_client.update_item_status()
					script.update_item(self)
					script.update_item(p)
				else: #send trade status
					#自分・相手がOKやキャンセルを押した際に双方に送信される
					self.user.map_client.send("0a19", self, p)
					#自分・相手がOKやキャンセルを押した際に双方に送信される
					p.user.map_client.send("0a19", p, self)
		elif p is False:
			#target offline or map changed
			self.cancel_trade()
		else: #p is None: npctrade
			self.set_trade_return()
			self.reset_trade(False) #don't clear return list
			self.user.map_client.send("0a1c") #トレード終了通知
			self.user.map_client.update_item_status()
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
			#self.loginevent = False
			self.logout = False
			self.pet = None #Pet()
			self.kanban = ""
			self.map_obj = None
			self.warehouse_open = None #warehouse_id
			self.shop_open = None #shop_id
			self.select_result = None
			self.reset_trade()
	
	def set_pet(self):
		return pets.set_pet(self)
	
	def unset_pet(self, logout=False):
		return pets.unset_pet(self, logout)
	
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
		self.equip = PC.Equip()
		self.status = PC.Status()
		self.reset_login()
		self.load()
		#self.update_status() #on login
	
	class Sort:
		def __init__(self):
			pass
	class Equip:
		def __init__(self):
			pass
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