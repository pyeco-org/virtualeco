#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
import traceback
from lib import env
from lib import general
from lib import server
from lib import db
from lib import pets
from lib import users
from lib import script
from lib import dumpobj
ITEM_DUMP_ATTR_LIST = (
	"item_id",
	"pict_id",
	"count",
	"warehouse",
)

def item_dumps(i):
	l = {}
	for attr in ITEM_DUMP_ATTR_LIST:
		l[attr] = getattr(i, attr)
	return dumpobj.dumps(l)

def item_loads(s):
	l = dumpobj.loads(s)
	i = general.get_item(l["item_id"])
	i.__dict__.update(l)
	return i

def save(self):
	data = general.get_config()
	data.add_section("main")
	data.set("main","data_ver", str(env.USERDATA_FORMAT_VERSION))
	data.set("main", "id", str(self.id))
	data.set("main", "name", str(self.name))
	data.set("main", "gmlevel", str(self.gmlevel))
	data.set("main", "race", str(self.race))
	data.set("main", "form", str(self.form))
	data.set("main", "gender", str(self.gender))
	data.set("main", "hair", str(self.hair))
	data.set("main", "haircolor", str(self.haircolor))
	data.set("main", "wig", str(self.wig))
	data.set("main", "face", str(self.face))
	data.set("main", "base_lv", str(self.base_lv))
	data.set("main", "ex", str(self.ex))
	data.set("main", "wing", str(self.wing))
	data.set("main", "wingcolor", str(self.wingcolor))
	data.set("main", "job", str(self.job))
	data.set("main", "map_id", str(self.map_id))
	data.set("main", "lv_base", str(self.lv_base))
	data.set("main", "lv_job1", str(self.lv_job1))
	data.set("main", "lv_job2x", str(self.lv_job2x))
	data.set("main", "lv_job2t", str(self.lv_job2t))
	data.set("main", "lv_job3", str(self.lv_job3))
	data.set("main", "gold", str(self.gold))
	data.set("main", "x", str(self.x))
	data.set("main", "y", str(self.y))
	data.set("main", "dir", str(self.dir))
	data.add_section("status")
	data.set("status", "str", str(self.str))
	data.set("status", "dex", str(self.dex))
	data.set("status", "int", str(self.int))
	data.set("status", "vit", str(self.vit))
	data.set("status", "agi", str(self.agi))
	data.set("status", "mag", str(self.mag))
	data.set("status", "stradd", str(self.stradd))
	data.set("status", "dexadd", str(self.dexadd))
	data.set("status", "intadd", str(self.intadd))
	data.set("status", "vitadd", str(self.vitadd))
	data.set("status", "agiadd", str(self.agiadd))
	data.set("status", "magadd", str(self.magadd))
	data.add_section("equip")
	for attr in general.EQUIP_ATTR_LIST:
		data.set("equip", attr, str(getattr(self.equip_std, attr)))
	data.add_section("equip_dem")
	for attr in general.EQUIP_ATTR_LIST:
		data.set("equip_dem", attr, str(getattr(self.equip_dem, attr)))
	#"iid,iid,iid, ..."
	data.add_section("sort")
	data.set("sort", "item", general.list_to_str(self.sort.item))
	data.set("sort", "warehouse", general.list_to_str(self.sort.warehouse))
	#"iid = id,count"
	data.add_section("item")
	for key, value in self.item.iteritems():
		data.set("item", str(key), item_dumps(value))
	#"iid = id,count,warehouse"
	data.add_section("warehouse")
	for key, value in self.warehouse.iteritems():
		data.set("warehouse", str(key), item_dumps(value))
	#"name = value"
	data.add_section("var")
	for key, value in self.var.iteritems():
		try:
			dump = dumpobj.dumps(value)
		except:
			general.log_error("[ pc  ] dump var error", self, key, value)
			general.log_error(traceback.format_exc())
			dump = str(value)
		data.set("var", str(key), dump)
	#"skill_id,skill_id,skill_id, ..."
	data.add_section("skill")
	data.set("skill", "list", general.list_to_str(self.skill_list))
	#
	data.write(open(self.path, "wb", base=env.USER_DIR))

def load(self):
	data = general.get_config(self.path, base=env.USER_DIR)
	if data.has_option("main", "data_ver"):
		data_ver = data.get("main","data_ver")
	else:
		data_ver = "1.0.0"
	name_map[data_ver](self, data)

def load_1_0_0(self, data):
	self.id = data.getint("main","id")
	self.name = data.get("main","name")
	self.gmlevel = data.getint("main","gmlevel")
	self.race = data.getint("main","race")
	self.form = data.getint("main","form")
	self.gender = data.getint("main","gender")
	self.hair = data.getint("main","hair")
	self.haircolor =data.getint("main","haircolor")
	self.wig = data.getint("main","wig")
	self.face = data.getint("main","face")
	self.base_lv = data.getint("main","base_lv")
	self.ex = data.getint("main","ex")
	self.wing = data.getint("main","wing")
	self.wingcolor = data.getint("main","wingcolor")
	self.job = data.getint("main","job")
	self.map_id = data.getint("main","map_id")
	self.lv_base = data.getint("main","lv_base")
	self.lv_job1 = data.getint("main","lv_job1")
	self.lv_job2x = data.getint("main","lv_job2x")
	self.lv_job2t = data.getint("main","lv_job2t")
	self.lv_job3 = data.getint("main","lv_job3")
	self.gold = data.getint("main","gold")
	self.x = data.getfloat("main","x")
	self.y = data.getfloat("main","y")
	self.dir = data.getint("main","dir")
	self.str = data.getint("status","str")
	self.dex = data.getint("status","dex")
	self.int = data.getint("status","int")
	self.vit = data.getint("status","vit")
	self.agi = data.getint("status","agi")
	self.mag = data.getint("status","mag")
	self.stradd = data.getint("status","stradd")
	self.dexadd = data.getint("status","dexadd")
	self.intadd = data.getint("status","intadd")
	self.vitadd = data.getint("status","vitadd")
	self.agiadd = data.getint("status","agiadd")
	self.magadd = data.getint("status","magadd")
	#{item_iid: item_object, ...}
	self.item = {}
	self.sort.item = general.str_to_list(data.get("sort", "item"))
	for i in self.sort.item:
		if i <= 0:
			general.log_error("[ pc  ] item iid <= 0", self)
		itemdata = general.str_to_list(data.get("item", str(i)))
		item = general.get_item(itemdata[0])
		item.count = itemdata[1]
		self.item[i] = item
	#{item_iid: item_object, ...}
	self.warehouse = {}
	self.sort.warehouse = general.str_to_list(data.get("sort", "warehouse"))
	for i in self.sort.warehouse:
		if i <= 0:
			general.log_error("[ pc  ] warehouse iid <= 0", self)
		itemdata = general.str_to_list(data.get("warehouse", str(i)))
		item = general.get_item(itemdata[0])
		item.count = itemdata[1]
		item.warehouse = itemdata[2]
		self.warehouse[i] = item
	#equip.place = iid
	for attr in general.EQUIP_ATTR_LIST:
		setattr(self.equip_std, attr, data.getint("equip", attr))
	if data.has_section("equip_dem"):
		for attr in general.EQUIP_ATTR_LIST:
			setattr(self.equip_dem, attr, data.getint("equip_dem", attr))
	#{name: value, ...}
	self.var = {}
	if data.has_section("dic"):
		for option in data.options("dic"):
			self.var[option] = data.get("dic", option)
	if data.has_section("var"):
		for key in data.options("var"):
			try:
				self.var[key] = dumpobj.loads(data.get("var", key))
			except:
				general.log_error("[ pc  ] load var error", self, key)
				general.log_error(traceback.format_exc())
	#[skill_id, ...]
	self.skill_list = general.str_to_list(data.get("skill", "list"))
	if self.dem_form_status():
		self.equip = self.equip_dem
	else:
		self.equip = self.equip_std

def load_1_1_0(self, data):
	self.id = data.getint("main","id")
	self.name = data.get("main","name")
	self.gmlevel = data.getint("main","gmlevel")
	self.race = data.getint("main","race")
	self.form = data.getint("main","form")
	self.gender = data.getint("main","gender")
	self.hair = data.getint("main","hair")
	self.haircolor =data.getint("main","haircolor")
	self.wig = data.getint("main","wig")
	self.face = data.getint("main","face")
	self.base_lv = data.getint("main","base_lv")
	self.ex = data.getint("main","ex")
	self.wing = data.getint("main","wing")
	self.wingcolor = data.getint("main","wingcolor")
	self.job = data.getint("main","job")
	self.map_id = data.getint("main","map_id")
	self.lv_base = data.getint("main","lv_base")
	self.lv_job1 = data.getint("main","lv_job1")
	self.lv_job2x = data.getint("main","lv_job2x")
	self.lv_job2t = data.getint("main","lv_job2t")
	self.lv_job3 = data.getint("main","lv_job3")
	self.gold = data.getint("main","gold")
	self.x = data.getfloat("main","x")
	self.y = data.getfloat("main","y")
	self.dir = data.getint("main","dir")
	self.str = data.getint("status","str")
	self.dex = data.getint("status","dex")
	self.int = data.getint("status","int")
	self.vit = data.getint("status","vit")
	self.agi = data.getint("status","agi")
	self.mag = data.getint("status","mag")
	self.stradd = data.getint("status","stradd")
	self.dexadd = data.getint("status","dexadd")
	self.intadd = data.getint("status","intadd")
	self.vitadd = data.getint("status","vitadd")
	self.agiadd = data.getint("status","agiadd")
	self.magadd = data.getint("status","magadd")
	#{item_iid: item_object, ...}
	self.item = {}
	self.sort.item = general.str_to_list(data.get("sort", "item"))
	for i in self.sort.item:
		if i <= 0:
			general.log_error("[ pc  ] item iid <= 0", self)
		self.item[i] = item_loads(data.get("item", str(i)))
	#{item_iid: item_object, ...}
	self.warehouse = {}
	self.sort.warehouse = general.str_to_list(data.get("sort", "warehouse"))
	for i in self.sort.warehouse:
		if i <= 0:
			general.log_error("[ pc  ] warehouse iid <= 0", self)
		self.warehouse[i] = item_loads(data.get("warehouse", str(i)))
	#equip.place = iid
	for attr in general.EQUIP_ATTR_LIST:
		setattr(self.equip_std, attr, data.getint("equip", attr))
	if data.has_section("equip_dem"):
		for attr in general.EQUIP_ATTR_LIST:
			setattr(self.equip_dem, attr, data.getint("equip_dem", attr))
	#{name: value, ...}
	self.var = {}
	if data.has_section("var"):
		for key in data.options("var"):
			try:
				self.var[key] = dumpobj.loads(data.get("var", key))
			except:
				general.log_error("[ pc  ] load var error", self, key)
				general.log_error(traceback.format_exc())
	#[skill_id, ...]
	self.skill_list = general.str_to_list(data.get("skill", "list"))
	if self.dem_form_status():
		self.equip = self.equip_dem
	else:
		self.equip = self.equip_std

name_map = {
	"1.0.0": load_1_0_0,
	"1.1.0": load_1_1_0, #2012-09-21
}