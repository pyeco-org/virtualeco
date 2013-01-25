#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
import traceback
#import thread
from lib import general
from lib import db
from lib import script

class Monster:
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.monster_id, self.name)
	
	def set_map(self, *args):
		with self.lock:
			return self._set_map(*args)
	def _set_map(self, map_id=None):
		if not map_id:
			map_id = self.map_id
		map_obj = db.map_obj.get(map_id)
		if not map_obj:
			return False
		#general.log(self, "set_map", map_obj)
		self.map_id = map_id
		if self.map_obj:
			with self.map_obj.lock:
				self.map_obj.monster_list.remove(self)
		self.map_obj = map_obj
		with self.map_obj.lock:
			if self not in self.map_obj.monster_list:
				with self.map_obj.lock:
					self.map_obj.monster_list.append(self)
		return True
	
	def set_coord(self, x, y):
		with self.lock:
			self.x = x #float, pack with unsigned byte
			self.y = y #float, pack with unsigned byte
			if self.x < 0: self.x += 256
			if self.y < 0: self.y += 256
			if not self.map_obj:
				return
			self.rawx = int((self.x - self.map_obj.centerx)*100.0)
			self.rawy = int((self.map_obj.centery - self.y)*100.0)
	def set_raw_coord(self, rawx, rawy):
		with self.lock:
			self.rawx = rawx
			self.rawy = rawy
			if not self.map_obj:
				return
			self.x = self.map_obj.centerx + rawx/100.0 #no int()
			self.y = self.map_obj.centery - rawy/100.0 #no int()
			if self.x < 0: self.x += 256
			if self.y < 0: self.y += 256
	
	def set_dir(self, d):
		with self.lock:
			self.dir = d
			self.rawdir = d*45
	def set_raw_dir(self, rawdir):
		with self.lock:
			self.rawdir = rawdir
			self.dir = int(round(rawdir/45.0, 0))
	
	def damage(self, i):
		with self.lock:
			if self.status.hp <= 0:
				general.log_error("[monster] monster.hp <= 0", self)
				return 0
			state_list = dict((j, 0) for j in xrange(10))
			self.status.hp -= i
			if self.status.hp <= 0:
				self.status.hp = 0
				state_list[0] |= 0x200 #行動不能
				general.start_thread(monsters.delete_monster_thread, (self,))
		script.send_map_obj(self.map_obj, (), "021c", self) #現在のHP/MP/SP/EP
		script.send_map_obj(self.map_obj, (), "157c", self, state_list) #キャラの状態
		return self.status.hp
	
	def reset(self):
		if self.map_obj:
			with self.map_obj.lock:
				self.map_obj.monster_list.remove(self)
				#print "self.map_obj.monster_list", self.map_obj.monster_list
		self.id = 0 # must large than 10000
		self.lock = threading.RLock()
		self.x = 0
		self.y = 0
		self.dir = 0
		self.centerx = 0
		self.centery = 0
		self.rawx = 0
		self.rawy = 0
		self.rawdir = 0
		self.status = Monster.Status()
		self.die = 0 #hide after 5 sec
		self.damage_dic = None #if set {} , will bug with copy.copy
	
	def __init__(self, d):
		d.update(self.__dict__)
		self.__dict__ = d
		self.map_id = 0
		self.map_obj = None
	
	class Status:
		def __init__(self):
			self.speed = 410
			self.hp = 100
			self.maxhp = 100
			self.mp = 1
			self.maxmp = 1
			self.sp = 1
			self.maxsp = 1
			self.ep = 0
			self.maxep = 0

def init():
	global monsters
	from lib import monsters