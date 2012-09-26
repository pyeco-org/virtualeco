#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
#import thread
import threading
import hashlib
import traceback
import ConfigParser
from lib import env
PC_CONFIG_MAX = 4
MAX_USER_ID = 10000
MAX_PC_ID = 10000
MIN_USER_ID = 100
MIN_PC_ID = 100
user_list = []
user_id_set = set()
pc_id_set = set()
user_list_lock = threading.RLock()

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
		return "%s<%s, %s>"%(repr(self), self.user_id, self.name)
	
	def load(self):
		cfg = general.get_config(os.path.join(
			self.path, env.USER_CONFIG_NAME
		), base=env.USER_DIR)
		self.password = cfg.get("main","password")
		self.delpassword = cfg.get("main","delpassword")
		self.user_id = cfg.getint("main","user_id")
		if self.pc_list:
			general.log_error("[users] ERROR: pc_list already load.", self)
			return
		for i in xrange(PC_CONFIG_MAX):
			path = os.path.join(self.path, env.PC_CONIG_NAME%i)
			if not os.path.exists(path):
				self.pc_list.append(None)
				continue
			self.pc_list.append(PC(self, path))
		with user_list_lock:
			user_id_set.add(self.user_id)
			for p in self.pc_list:
				if p: pc_id_set.add(p.id)
	
	def save(self):
		cfg = ConfigParser.SafeConfigParser()
		cfg.add_section("main")
		cfg.set("main", "password", self.password)
		cfg.set("main", "delpassword", self.delpassword)
		cfg.set("main", "user_id", str(self.user_id))
		cfg.write(open(os.path.join(
			self.path, env.USER_CONFIG_NAME
		), "wb", base=env.USER_DIR))
	
	def reset_login(self):
		with self.lock:
			if self.login_client:
				self.login_client._stop()
			for p in self.pc_list:
				if not p: continue
				if p.online:
					p.reset_login()
					general.log("[users] reset save", p)
					p.save()
			self.login_client = None
		self.reset_map()
	
	def reset_map(self):
		with self.lock:
			if self.map_client:
				self.map_client._stop()
			self.map_client = None

def make_new_user(user_name, password, delpassword):
	if get_user_from_name(user_name):
		return False
	with user_list_lock:
		user_id = general.make_id(user_id_set, MIN_USER_ID)
		if user_id >= MAX_USER_ID:
			general.log_error("[users] ERROR: user_id [%s] >= MAX_USER_ID"%user_id)
			return False
		general.log("[users] add user id", user_id)
		user_id_set.add(user_id)
	cfg = general.get_config()
	cfg.add_section("main")
	cfg.set("main", "user_id", str(user_id))
	cfg.set("main", "password", hashlib.md5(password).hexdigest())
	cfg.set("main", "delpassword", hashlib.md5(delpassword).hexdigest())
	if not os.path.exists(os.path.join(env.USER_DIR, user_name)):
		os.mkdir(os.path.join(env.USER_DIR, user_name), base=env.USER_DIR)
	cfg.write(open(os.path.join(
		env.USER_DIR, user_name, env.USER_CONFIG_NAME
	), "wb", base=env.USER_DIR))
	with user_list_lock:
		user_list.append(User(user_name, os.path.join(env.USER_DIR, user_name)))
	return True

def delete_user(user_name, password, delete_password):
	user = get_user_from_name(user_name)
	if not user: return 0x01 #user name not exist
	with user.lock:
		password_md5 = hashlib.md5(password).hexdigest()
		delete_password_md5 = hashlib.md5(delete_password).hexdigest()
		if user.password != password_md5: return 0x02 #password error
		if user.delpassword != delete_password_md5: return 0x02 #password error
		user.reset_login() #close connection
		with user_list_lock:
			try:
				user_list.remove(user)
				general.log("[users] remove user id", user.user_id)
				user_id_set.remove(user.user_id)
				for p in user.pc_list:
					if p:
						general.log("[users] remove pc id", p.id)
						pc_id_set.remove(p.id)
			except:
				general.log_error(traceback.format_exc())
		for name in os.listdir(user.path, base=env.USER_DIR):
			os.remove(os.path.join(user.path, name), base=env.USER_DIR)
		os.rmdir(user.path, base=env.USER_DIR)
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
	path = os.path.join(user.path, env.PC_CONIG_NAME%num)
	if os.path.exists(path):
		return False
	with user_list_lock:
		pc_id = general.make_id(pc_id_set, MIN_PC_ID)
		if pc_id >= MAX_PC_ID:
			general.log_error("[users] ERROR: pc_id [%s] >= MAX_PC_ID"%pc_id)
			return False
		general.log("[users] add pc id", pc_id)
		pc_id_set.add(pc_id)
	cfg = general.get_config()
	cfg.add_section("main")
	cfg.set("main", "id", str(pc_id))
	cfg.set("main", "name", str(name))
	cfg.set("main", "gmlevel", str(env.DEFAULT_GMLEVEL))
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
	cfg.write(open(path, "wb", base=env.USER_DIR))
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
				l += user.pc_list
	return filter(None, l)
def get_pc_from_name(name):
	for p in get_pc_list():
		if p.name == name:
			return p
def get_pc_from_id(i):
	for p in get_pc_list():
		if p.id == i:
			return p
def get_online_pc_list():
	return filter(lambda p:p.online, get_pc_list())

def backup_user_data():
	try:
		zip_path = os.path.join(env.USER_BAK_DIR, "%s.zip"%general.get_today())
		if os.path.exists(zip_path):
			return
		if not os.path.exists(env.USER_BAK_DIR):
			os.mkdir(env.USER_BAK_DIR)
		general.save_zip(env.USER_DIR, zip_path, env.USER_DIR, env.USER_BAK_DIR)
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
		general.start_thread(backup_user_data_every_day_thread, ())

def save_user_data():
	try:
		for p in get_online_pc_list():
			try:
				p.save()
			except:
				general.log_error(traceback.format_exc(), p)
	except:
		general.log_error(traceback.format_exc())
def save_user_data_every_min_thread():
	while True:
		save_user_data()
		time.sleep(60)
save_user_data_every_min_thread_running = False
def save_user_data_every_min():
	global save_user_data_every_min_thread_running
	if not save_user_data_every_min_thread_running:
		save_user_data_every_min_thread_running = True
		general.start_thread(save_user_data_every_min_thread, ())
def save_user_data_atexit():
	for p in get_online_pc_list():
		try:
			general.log("[users] save atexit", p)
			p.save()
		except:
			general.log_error(traceback.format_exc(), p)
def upgrade_user_data():
	for p in get_pc_list():
		try:
			p.save()
		except:
			general.log_error(traceback.format_exc(), p)

def load():
	global general, PC, server
	from lib import general
	from lib.obj.pc import PC
	from lib import server
	with user_list_lock:
		for name in os.listdir(env.USER_DIR):
			try:
				user_list.append(User(name, os.path.join(env.USER_DIR, name)))
			except:
				general.log_error("load error:", name)
				raise
	#for user in get_user_list():
	#	general.log(user)
	#for p in get_pc_list():
	#	general.log(p)
	if env.BACKUP_USER_DATA_EVERY_DAY:
		backup_user_data_every_day()
	save_user_data_every_min()
