#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
import ConfigParser
from lib import general

class Player:
	def __str__(self):
		return "%s[%s]"%(repr(self), self.path)
	
	def load(self):
		with self.lock:
			self._load()
	def _load(self):
		cfg = ConfigParser.SafeConfigParser()
		cfg.readfp(general.get_config_io(self.path))
		self.charid = cfg.getint("main","charid")
		self.sid = cfg.getint("main","charid")
		self.name = cfg.get("main","name")
		self.password = cfg.get("main","password")
		self.delpassword = cfg.get("main","delpassword")
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
		self.map = cfg.getint("main","map")
		self.lv_base = cfg.getint("main","lv_base")
		self.lv_job1 = cfg.getint("main","lv_job1")
		self.lv_job2x = cfg.getint("main","lv_job2x")
		self.lv_job2t = cfg.getint("main","lv_job2t")
		self.lv_job3 = cfg.getint("main","lv_job3")
		self.gold = cfg.getint("main","gold")
		self.x = cfg.getint("main","x")
		self.y = cfg.getint("main","y")
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
	def _save(self):
		cfg = ConfigParser.SafeConfigParser()
		cfg.add_section("main")
		cfg.set("main", "charid", str(self.charid))
		cfg.set("main", "name", str(self.name))
		cfg.set("main", "password", str(self.password))
		cfg.set("main", "delpassword", str(self.delpassword))
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
		cfg.set("main", "map", str(self.map))
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
		sort = ""
		for i in self.sort.item:
			sort += ",%s"%i
		if sort: sort = sort[1:]
		cfg.set("sort", "item", sort)
		sort_warehouse = ""
		for i in self.sort.warehouse:
			sort_warehouse += ",%s"%i
		if sort_warehouse: sort_warehouse = sort_warehouse[1:]
		cfg.set("sort", "warehouse", sort_warehouse)
		#"iid = id,count"
		cfg.add_section("item")
		for i in sorted(self.item, key=int):
			cfg.set("item", str(i), "%s,%s"%(
				self.item[i].id,
				self.item[i].count))
		#"iid = id,count,warehouse"
		cfg.add_section("warehouse")
		for i in sorted(self.warehouse, key=int):
			cfg.set("warehouse", str(i), "%s,%s,%s"%(
				self.warehouse[i].id,
				self.warehouse[i].count,
				self.warehouse[i].warehouse))
		#"name = value"
		cfg.add_section("dic")
		for name, value in self.dic.iteritems():
			cfg.set("dic", str(name), str(value))
		#"skill_id,skill_id,skill_id, ..."
		cfg.add_section("skill")
		cfg.set("skill", "list", general.list_to_str(self.skill_list))
		#
		cfg.write(open(self.path, "wb"))
	
	def reset_login(self):
		with self.lock:
			self._reset_login()
	def _reset_login(self):
		if self.login_client:
			self.login_client.stop()
		self.login_client = None
		self._reset_map()
	
	def reset_map(self):
		with self.lock:
			self._reset_map()
	def _reset_map(self):
		if self.map_client:
			self.map_client.stop()
		self.map_client = None
		self.online = False
		self.rawx = 0
		self.rawy = 0
		self.rawdir = 0
		self.battlestatus = 0
		self.wrprank = 0
		self.loginevent = False
		self.logout = False
		self.sendmapserver = False
		self.pet = None #Pet()
		self.kanban = ""
	
	def __init__(self, path, filename):
		self.path = path
		self.lock = threading.RLock()
		self.username = filename.replace(".ini", "")
		self.login_client = None 
		self.map_client = None
		self.sort = Player.Sort()
		self.equip = Player.Equip()
		self.status = Player.Status()
		self.reset_login()
		self.load()
	
	class Sort:
		def __init__(self):
			pass
	class Equip:
		def __init__(self):
			pass
	class Status:
		def __init__(self):
			self.maxhp = 100
			self.maxmp = 40
			self.maxsp = 50
			self.maxep = 30
			self.hp = 100
			self.mp = 40
			self.sp = 50
			self.ep = 30
			
			self.minatk1 = 100
			self.minatk2 = 100
			self.minatk3 = 100
			self.maxatk1 = 100
			self.maxatk2 = 100
			self.maxatk3 = 100
			self.minmatk = 100
			self.maxmatk = 100
			
			self.leftdef = 50
			self.rightdef = 30
			self.leftmdef = 30
			self.rightmdef = 20
			self.shit = 7
			self.lhit = 0
			self.mhit = 7
			self.chit = 0
			self.savoid = 0
			self.lavoid = 12
			
			self.hpheal = 0
			self.mpheal = 0
			self.spheal = 0
			self.aspd = 190
			self.cspd = 187
			self.speed = 410
			self.adelay = 2*(1-self.aspd/1000.0) #attack delay
			
			self.maxcapa = 1000
			self.maxrightcapa = 0
			self.maxleftcapa = 0
			self.maxbackcapa = 0
			self.maxpayl = 1000
			self.maxrightpayl = 0
			self.maxleftpayl = 0
			self.maxbackpayl = 0
			self.capa = 30
			self.rightcapa = 0
			self.leftcapa = 0
			self.backcapa = 0
			self.payl = 30
			self.rightpayl = 0
			self.leftpayl = 0
			self.backpayl = 0
