#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import dbmap
import traceback
import __builtin__
DATA_DIR = "./data"

def _detect_type(s):
	if s == "" or s == ".": return 0
	try: return int(s)
	except:
		try: return float(s)
		except: return s

def get_raw_dict(name):
	db_path = dbmap.DATABASE_PATH[name]
	raw_dict = general.load_dump(db_path, DATA_DIR)
	if raw_dict and type(raw_dict) == dict:
		return raw_dict
	
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
			key = row_map_raw.get(attr)
			if key is None:
				general.log_error("attr not define:", attr)
				continue
			if not key:
				continue
			if i > min_length:
				min_length = i
			row_map[i] = key
		min_length += 1
		row_map.update(row_map_ext)
		
		for line in db_file:
			if line.startswith("#"):
				continue
			row = line.split(",")
			if len(row) < min_length:
				continue
			d = {}
			for i, key in row_map.iteritems():
				d[key] = _detect_type(row[i])
			raw_dict[_detect_type(row[0])] = d
	
	general.save_dump(db_path, raw_dict, DATA_DIR)
	return raw_dict

def load_database(name, obj):
	db_path = dbmap.DATABASE_PATH[name]
	general.log_line("Load %-20s"%("%s ..."%db_path))
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
	import data
	global general
	from lib import general
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



