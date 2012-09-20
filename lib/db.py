#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import traceback
import __builtin__
from lib import env

def get_raw_dict(name):
	db_path = dbmap.DATABASE_PATH[name]
	dump_data = general.load_dump(db_path, env.DATABASE_DIR)
	if dump_data is not None and type(dump_data) == dict:
		ver = dump_data.get("ver")
		raw_dict = dump_data.get("raw_dict")
		if ver == env.DATABASE_FORMAT_VERSION:
			if raw_dict is not None and type(raw_dict) == dict:
				return raw_dict
	general.log("Update", name, "database dump ...")
	
	raw_dict = {}
	row_map = {}
	row_map_raw = dbmap.DATABASE_ROW_MAP_RAW[name]
	row_map_ext = dbmap.DATABASE_ROW_MAP_EXT[name]
	min_length = float("-inf")
	
	with open(db_path, "rb") as db_file:
		line_first = db_file.readline()
		if line_first.startswith("\xef\xbb\xbf"):
			line_first = line_first[3:]
		attr_table = line_first.strip().split(",")
		for i, attr in enumerate(attr_table):
			attr = attr.strip()
			if not attr:
				continue
			value = row_map_raw.get(attr)
			if value is None:
				general.log_error("attr not define:", attr)
				continue
			if value is NULL:
				continue
			if i > min_length:
				min_length = i
			row_map[i] = value
		min_length += 1
		row_map.update(row_map_ext)
		
		for line in db_file:
			if line.startswith("#"):
				continue
			if line in ("\n", "\r\n"):
				continue
			row = line.split(",")
			if len(row) < min_length:
				continue
			d = {}
			for i, value in row_map.iteritems():
				try:
					d[value[1]] = value[0](row[i])
				except:
					general.log_error("attr:", value)
					raise
			raw_dict[int(row[0])] = d
	
	general.save_dump(
		db_path,
		{"ver": env.DATABASE_FORMAT_VERSION, "raw_dict": raw_dict},
		env.DATABASE_DIR,
	)
	return raw_dict

def load_database(name, obj):
	db_path = dbmap.DATABASE_PATH[name]
	general.log_line("[load ] load %-20s"%("%s ..."%db_path))
	db_dict = {}
	raw_dict = get_raw_dict(name)
	for i, d in raw_dict.iteritems():
		try:
			db_dict[i] = obj(d)
		except:
			general.log_error("load error: id %s"%str(i), traceback.format_exc())
	general.log("	%d	%s	load."%(len(db_dict), name))
	return db_dict

def load():
	global general
	global NULL
	global dbmap
	from lib import general
	from lib.general import NULL
	import dbmap
	
	import data
	from lib import obj
	
	global item
	item = load_database("item", data.item.Item)
	global job
	job = load_database("job", data.job.Job)
	global map_obj
	map_obj = load_database("map", obj.map.Map)
	global monster_obj
	monster_obj = load_database("monster", obj.monster.Monster)
	global npc
	npc = load_database("npc", data.npc.Npc)
	global pet_obj
	pet_obj = load_database("pet", obj.pet.Pet)
	global shop
	shop = load_database("shop", data.shop.Shop)
	global skill
	skill = load_database("skill", data.skill.Skill)
