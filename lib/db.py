#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import marshal
import traceback

def _detect_type(s):
	if s == "" or s == ".": return 0
	try: return int(s)
	except:
		try: return float(s)
		except: return s

def get_raw_list(path, len_min):
	from lib import general
	modify_time = int(os.stat(path).st_mtime)
	dump_path = "%s.dump"%path
	raw_list = []
	if os.path.exists(dump_path):
		with open(dump_path, "rb") as dump:
			if modify_time == general.unpack_int(dump.read(4)):
				raw_list = marshal.loads(dump.read())
	if not raw_list:
		for row in csv.reader(open(path, "rb")):
			if len(row) < len_min: continue
			if row[0].startswith("\xef\xbb\xbf"): row[0] = row[0][3:]
			if row[0].startswith("#"): continue
			row_new = [] #can not use map ...
			for value in row:
				row_new.append(_detect_type(value))
			raw_list.append(row_new)
		with open(dump_path, "wb") as dump:
			dump.write(general.pack_int(modify_time))
			dump.write(marshal.dumps(raw_list))
	return raw_list

def load_database(path, obj, len_min):
	print "Load %s ..."%path,
	d = {}
	for i, row in enumerate(get_raw_list(path, len_min)):
		try:
			d[int(row[0])] = obj(row)
		except:
			print "load error: line %d"%(i+1), traceback.format_exc()
	print "\t%d \tobj load."%len(d)
	return d

def load(data_path):
	import data
	global item
	item = load_database(data_path["item"], data.item.Item, 167)
	global map
	map = load_database(data_path["map"], data.map.Map, 4)
	global monster
	monster = load_database(data_path["monster"], data.monster.Monster, 3)
	global npc
	npc = load_database(data_path["npc"], data.npc.Npc, 3)
	global pet
	pet = load_database(data_path["pet"], data.pet.Pet, 20)
	global shop
	shop = load_database(data_path["shop"], data.shop.Shop, 1)
	global skill
	skill = load_database(data_path["skill"], data.skill.Skill, 5)
