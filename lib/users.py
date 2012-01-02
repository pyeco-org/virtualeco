#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import thread
import threading
import hashlib
import traceback
import ConfigParser
USER_DIR = "./user"
USER_BAK_DIR = "./user_bak"
USER_CONFIG_NAME = "user.ini"
PC_CONIG_NAME = "%d.ini"
PC_CONFIG_MAX = 4
user_list = []
user_list_lock = threading.RLock()
next_id_lock = threading.RLock()
next_user_id = 1
next_pc_id = 1

class User:
	def __init__(self, name, path):
		self.name = name
		self.path = path
		self.pc_list = []
		self.login_client = None
		self.map_client = None
		self.lock = threading.RLock()
		self.load()
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.user_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))
	
	def load(self):
		cfg = general.get_config(os.path.join(self.path, USER_CONFIG_NAME))
		self.password = cfg.get("main","password")
		self.delpassword = cfg.get("main","delpassword")
		self.user_id = cfg.getint("main","user_id")
		for i in xrange(PC_CONFIG_MAX):
			path = os.path.join(self.path, PC_CONIG_NAME%i)
			if not os.path.exists(path):
				self.pc_list.append(None)
				continue
			self.pc_list.append(PC(self, path))
		with next_id_lock:
			global next_user_id
			global next_pc_id
			if next_user_id <= self.user_id:
				next_user_id = self.user_id+1
			for pc in self.pc_list:
				if not pc: continue
				if next_pc_id <= pc.id:
					next_pc_id = pc.id+1
	
	def save(self):
		cfg = ConfigParser.SafeConfigParser()
		cfg.add_section("main")
		cfg.set("main", "password", self.password)
		cfg.set("main", "delpassword", self.delpassword)
		cfg.set("main", "user_id", str(self.user_id))
		cfg.write(open(os.path.join(self.path, USER_CONFIG_NAME), "wb"))
	
	def reset_login(self):
		with self.lock:
			if self.login_client:
				self.login_client._stop()
			for pc in self.pc_list:
				if not pc: continue
				if pc.online: pc.save()
				pc.reset_login()
			self.login_client = None
		self.reset_map()
	
	def reset_map(self):
		with self.lock:
			if self.map_client:
				self.map_client._stop()
			for pc in self.pc_list:
				if not pc: continue
				if pc.online: pc.save()
				pc.reset_map()
			self.map_client = None

def make_new_user(user_name, password, delpassword):
	if get_user_from_name(user_name):
		return False
	with next_id_lock:
		global next_user_id
		user_id = next_user_id
		next_user_id += 1
		general.log("[users] next_user_id", next_user_id)
	cfg = general.get_config()
	cfg.add_section("main")
	cfg.set("main", "user_id", str(user_id))
	cfg.set("main", "password", hashlib.md5(password).hexdigest())
	cfg.set("main", "delpassword", hashlib.md5(delpassword).hexdigest())
	if not os.path.exists(os.path.join(USER_DIR, user_name)):
		os.mkdir(os.path.join(USER_DIR, user_name))
	cfg.write(open(os.path.join(USER_DIR, user_name, USER_CONFIG_NAME), "wb"))
	with user_list_lock:
		user_list.append(User(user_name, os.path.join(USER_DIR, user_name)))
	return True

def delete_user(user_name, password, delete_password):
	user = get_user_from_name(user_name)
	if not user: return 0x01 #user name not exist
	with user.lock:
		password_md5 = hashlib.md5(password).hexdigest()
		delete_password_md5 = hashlib.md5(delete_password).hexdigest()
		if user.password != password_md5: return 0x02 #password error
		if user.delpassword != delete_password_md5: return 0x02 #password error
		with user_list_lock:
			user_list.remove(user)
		user.reset_login() #close connection
		for name in os.listdir(user.path):
			os.remove(os.path.join(user.path, name))
		os.rmdir(user.path)
		del user
	return 0x00 #success

def modify_password(user_name,
	old_password, old_delete_password, password, delete_password):
	user = get_user_from_name(user_name)
	if not user: return 0x01 #user name not exist
	with user.lock:
		old_password_md5 = hashlib.md5(old_password).hexdigest()
		old_delete_password_md5 = hashlib.md5(old_delete_password).hexdigest()
		#general.log(old_password_md5, old_delete_password_md5)
		if user.password != old_password_md5: return 0x02 #password error
		if user.delpassword != old_delete_password_md5: return 0x02 #password error
		user.password = hashlib.md5(password).hexdigest()
		user.delpassword = hashlib.md5(delete_password).hexdigest()
		user.save()
	return 0x00 #success

def make_new_pc(user, num, name, race, gender, hair, hair_color, face):
	with user.lock:
		if user.pc_list[num]:
			return False
	path = os.path.join(user.path, PC_CONIG_NAME%num)
	if os.path.exists(path):
		return False
	with next_id_lock:
		global next_pc_id
		pc_id = next_pc_id
		next_pc_id += 1
		general.log("[users] next_pc_id", next_pc_id)
	cfg = general.get_config()
	cfg.add_section("main")
	cfg.set("main", "id", str(pc_id))
	cfg.set("main", "name", str(name))
	cfg.set("main", "gmlevel", str(server.config.defaultgmlevel))
	cfg.set("main", "race", str(race))
	cfg.set("main", "form", "0")
	cfg.set("main", "gender", str(gender))
	cfg.set("main", "hair", str(hair))
	cfg.set("main", "haircolor", str(hair_color))
	cfg.set("main", "wig", "-1")
	cfg.set("main", "face", str(face))
	cfg.set("main", "base_lv", "0")
	cfg.set("main", "ex", "0")
	cfg.set("main", "wing", "0")
	cfg.set("main", "wingcolor", "0")
	cfg.set("main", "job", "0")
	cfg.set("main", "map_id", "30203000")
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
		user.pc_list[num] = PC(user, path)
	return True

def get_user_list():
	l = []
	with user_list_lock:
		for user in user_list:
			l.append(user)
	return l
def get_user_from_name(name):
	for user in get_user_list():
		with user.lock:
			if user.name == name:
				return user
def get_user_from_id(i):
	for user in get_user_list():
		with user.lock:
			if user.user_id == i:
				return user

def get_pc_list():
	l = []
	with user_list_lock:
		for user in user_list:
			with user.lock:
				for pc in filter(None, user.pc_list):
					l.append(pc)
	return l
def get_pc_from_name(name):
	for pc in get_pc_list():
		with pc.lock:
			if pc.name == name:
				return pc
def get_pc_from_id(i):
	for pc in get_pc_list():
		with pc.lock:
			if pc.id == i:
				return pc

def backup_user_data():
	try:
		zip_path = os.path.join(USER_BAK_DIR, "%s.zip"%general.get_today())
		if os.path.exists(zip_path):
			return
		if not os.path.exists(USER_BAK_DIR):
			os.mkdir(USER_BAK_DIR)
		general.save_zip(USER_DIR, zip_path)
	except:
		general.log_error("backup_user_data", traceback.format_exc())
def backup_user_data_every_day_thread():
	while True:
		backup_user_data()
		time.sleep(3600) #every hour
backup_user_data_every_day_thread_running = False
def backup_user_data_every_day():
	global backup_user_data_every_day_thread_running
	if not backup_user_data_every_day_thread_running:
		backup_user_data_every_day_thread_running = True
		thread.start_new_thread(backup_user_data_every_day_thread, ())

def save_user_data():
	try:
		for pc in get_pc_list():
			if pc.online:
				pc.save()
	except:
		general.log_error("save_user_data", traceback.format_exc())
def save_user_data_every_min_thread():
	while True:
		save_user_data()
		time.sleep(60)
save_user_data_every_min_thread_running = False
def save_user_data_every_min():
	global save_user_data_every_min_thread_running
	if not save_user_data_every_min_thread_running:
		save_user_data_every_min_thread_running = True
		thread.start_new_thread(save_user_data_every_min_thread, ())

def load():
	global general
	from lib import general
	global PC
	from lib.obj.pc import PC
	global server
	from lib import server
	with user_list_lock:
		for name in os.listdir(USER_DIR):
			try:
				user_list.append(User(name, os.path.join(USER_DIR, name)))
			except:
				general.log_error("load error:", name)
				raise
	for user in get_user_list():
		general.log(user)
	for pc in get_pc_list():
		general.log(pc)
	general.log("[users] next_user_id", next_user_id)
	general.log("[users] next_pc_id", next_pc_id)