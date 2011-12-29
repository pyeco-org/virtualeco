#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import threading
import ConfigParser
USER_CONFIG_NAME = "user.ini"
PLAYER_CONIG_NAME = "%d.ini"
PLAYER_CONFIG_MAX = 4
user_list = []
user_list_lock = threading.RLock()

class User:
	def __init__(self, name, path):
		self.name = name
		self.path = path
		self.player = []
		self.password = None
		self.delpassword = None
		self.login_client = None
		self.map_client = None
		self.lock = threading.RLock()
		self.load()
	
	def __str__(self):
		return "%s[%s]"%(repr(self), self.name)
	
	def load(self):
		cfg = ConfigParser.SafeConfigParser()
		cfg.readfp(general.get_config_io(os.path.join(self.path, USER_CONFIG_NAME)))
		self.password = cfg.get("main","password")
		self.delpassword = cfg.get("main","delpassword")
		self.userid = cfg.get("main","userid")
		for i in xrange(PLAYER_CONFIG_MAX):
			path = os.path.join(self.path, PLAYER_CONIG_NAME%i)
			if not os.path.exists(path):
				self.player.append(None)
				continue
			self.player.append(Player(self, path))
	
	def save(self):
		cfg = ConfigParser.SafeConfigParser()
		cfg.add_section("main")
		cfg.set("main", "password", self.password)
		cfg.set("main", "delpassword", self.delpassword)
		cfg.set("main", "userid", self.userid)
		cfg.write(open(os.path.join(self.path, USER_CONFIG_NAME), "wb"))
	
	def reset_login(self):
		with self.lock:
			if self.login_client:
				self.login_client._stop()
			self.login_client = None
		self.reset_map()
	
	def reset_map(self):
		with self.lock:
			if self.map_client:
				self.map_client._stop()
			self.map_client = None

def make_new_player(user, num, name, race, gender, hair, hair_color, face):
	with user.lock:
		if user.player[num]:
			return False
	path = os.path.join(user.path, PLAYER_CONIG_NAME%num)
	if os.path.exists(path):
		return False
	charid = 0
	for player in get_player_list():
		with player.lock:
			if player.charid >= charid:
				charid = player.charid+1
	cfg = ConfigParser.SafeConfigParser()
	cfg.add_section("main")
	cfg.set("main", "charid", str(charid))
	cfg.set("main", "name", str(name))
	cfg.set("main", "gmlevel", str(server.config.defaultgmlevel))
	cfg.set("main", "race", str(race))
	cfg.set("main", "form", "0")
	cfg.set("main", "gender", str(gender))
	cfg.set("main", "hair", str(hair))
	cfg.set("main", "haircolor", str(hair_color))
	cfg.set("main", "wig", "0")
	cfg.set("main", "face", str(face))
	cfg.set("main", "base_lv", "0")
	cfg.set("main", "ex", "0")
	cfg.set("main", "wing", "0")
	cfg.set("main", "wingcolor", "0")
	cfg.set("main", "job", "0")
	cfg.set("main", "map", "30203000")
	cfg.set("main", "lv_base", "1")
	cfg.set("main", "lv_job1", "1")
	cfg.set("main", "lv_job2x", "1")
	cfg.set("main", "lv_job2t", "1")
	cfg.set("main", "lv_job3", "1")
	cfg.set("main", "gold", "0")
	cfg.set("main", "x", "13")
	cfg.set("main", "y", "8")
	cfg.set("main", "dir", "6")
	cfg.add_section("status")
	cfg.set("status", "str", "8")
	cfg.set("status", "dex", "3")
	cfg.set("status", "int", "3")
	cfg.set("status", "vit", "10")
	cfg.set("status", "agi", "4")
	cfg.set("status", "mag", "4")
	cfg.set("status", "stradd", "2")
	cfg.set("status", "dexadd", "1")
	cfg.set("status", "intadd", "1")
	cfg.set("status", "vitadd", "2")
	cfg.set("status", "agiadd", "1")
	cfg.set("status", "magadd", "1")
	cfg.add_section("equip")
	cfg.set("equip", "head", "0")
	cfg.set("equip", "face", "0")
	cfg.set("equip", "chestacce", "0")
	cfg.set("equip", "tops", "1")
	cfg.set("equip", "bottoms", "2")
	cfg.set("equip", "backpack", "0")
	cfg.set("equip", "right", "0")
	cfg.set("equip", "left", "0")
	cfg.set("equip", "shoes", "3")
	cfg.set("equip", "socks", "0")
	cfg.set("equip", "pet", "0")
	cfg.add_section("sort")
	cfg.set("sort", "item", "1,2,3,4,5")
	cfg.set("sort", "warehouse", "")
	cfg.add_section("item")
	if gender != 0: 
		cfg.set("item", "1", "50000055,1")
		cfg.set("item", "2", "50010300,1")
		cfg.set("item", "3", "50060100,1")
		cfg.set("item", "4", "10020114,1")
		cfg.set("item", "5", "60010082,1")
	else:
		cfg.set("item", "1", "50000000,1") #スモック♂
		cfg.set("item", "2", "50010300,1")
		cfg.set("item", "3", "50060150,1")
		cfg.set("item", "4", "10020114,1")
		cfg.set("item", "5", "60010082,1")
	cfg.add_section("warehouse")
	cfg.add_section("dic")
	cfg.add_section("skill")
	cfg.set("skill", "list", "")
	cfg.write(open(path, "wb"))
	with user.lock:
		user.player[num] = Player(user, path)
	return True

def get_user_list():
	l = []
	with user_list_lock:
		for user in user_list:
			l.append(user)
	return l

def get_player_list():
	l = []
	with user_list_lock:
		for user in user_list:
			with user.lock:
				for player in filter(None, user.player):
					l.append(player)
	return l

def load(path_dir):
	global general
	from lib import general
	global Player
	from lib.obj.player import Player
	global server
	from lib import server
	for name in os.listdir(path_dir):
		try:
			user_list.append(User(name, os.path.join(path_dir, name)))
		except:
			print "load error:", name
			raise
	for user in get_user_list():
		print user
	for player in get_player_list():
		print player
