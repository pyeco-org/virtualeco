#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import csv
import marshal
import traceback

def _detect_type(s):
	if s == "" or s == ".": return 0
	try: return int(s)
	except:
		try: return float(s)
		except: return s

def get_raw_list(path, len_min):
	modify_time = int(os.stat(path).st_mtime)
	dump_path = "%s.dump"%path
	python_ver = int("".join(__builtin__.map(str, sys.version_info[:3])))
	raw_list = []
	if os.path.exists(dump_path):
		with open(dump_path, "rb") as dump:
			try:
				if (general.unpack_int(dump.read(4)) == modify_time and
					general.unpack_int(dump.read(4)) == python_ver):
					raw_list = marshal.loads(dump.read())
			except:
				print "dump file %s broken."%dump_path, traceback.format_exc()
	if not raw_list:
		for row in csv.reader(open(path, "rb")):
			if len(row) < len_min: continue
			if row[0].startswith("\xef\xbb\xbf"): row[0] = row[0][3:]
			if row[0].startswith("#"): continue
			raw_list.append(__builtin__.map(_detect_type, row))
		with open(dump_path, "wb") as dump:
			dump.write(general.pack_int(modify_time))
			dump.write(general.pack_int(python_ver))
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
	global general
	from lib import general
	global __builtin__
	import __builtin__
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