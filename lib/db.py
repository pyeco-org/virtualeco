#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import csv
import traceback
import __builtin__
DATA_PATH = {	"item": "./data/item.csv",
			"map": "./data/map.csv",
			"monster": "./data/monster.csv",
			"npc": "./data/npc.csv",
			"pet": "./data/pet.csv",
			"shop": "./data/shop.csv",
			"skill": "./data/skill.csv",
			}

def _detect_type(s):
	if s == "" or s == ".": return 0
	try: return int(s)
	except:
		try: return float(s)
		except: return s

def get_raw_list(path, len_min):
	raw_list = general.load_dump(path)
	if not raw_list:
		raw_list = []
		for row in csv.reader(open(path, "rb")):
			if len(row) < len_min: continue
			if row[0].startswith("\xef\xbb\xbf"): row[0] = row[0][3:]
			if row[0].startswith("#"): continue
			raw_list.append(__builtin__.map(_detect_type, row))
		general.save_dump(path, raw_list)
	return raw_list

def load_database(name, obj, len_min):
	path = DATA_PATH[name]
	general.log_line("Load %s ..."%path)
	d = {}
	for i, row in enumerate(get_raw_list(path, len_min)):
		try:
			d[row[0]] = obj(row)
		except:
			general.log_error("load error: line %d"%(i+1), traceback.format_exc())
	general.log(" 	%d	%s	load."%(len(d), name))
	return d

def load():
	import data
	global general
	from lib import general
	from lib import obj
	global item
	item = load_database("item", data.item.Item, 167)
	global map_obj
	map_obj = load_database("map", obj.map.Map, 4)
	global monster
	monster = load_database("monster", data.monster.Monster, 3)
	global npc
	npc = load_database("npc", data.npc.Npc, 3)
	global pet_obj
	pet_obj = load_database("pet", obj.pet.Pet, 20)
	global shop
	shop = load_database("shop", data.shop.Shop, 1)
	global skill
	skill = load_database("skill", data.skill.Skill, 5)
