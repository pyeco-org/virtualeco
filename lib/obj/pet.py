#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import threading
from lib import db

class Pet:
	def __init__ (self, row):
		self.pet_id = row[0] #pet id
		self.name = row[1]
		self.pict_id = row[2] #pet pictid
		self.hp = row[19]
		self.maxhp = row[19]
		self.map_id = 0
		self.map_obj = None
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.pet_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))
	
	def reset(self):
		if self.map_obj:
			self.map_obj.pet_list.remove(self)
		self.id = 0
		self.lock = threading.RLock()
		self.master = None # PC()
		self.map_id = 0
		self.map_obj = None
		self.x = 0
		self.y = 0
		self.dir = 0
		self.rawx = 0
		self.rawy = 0
		self.rawdir = 0
		self.speed = 310 #410
		self.motion_id = 0
		self.motion_loop = False
		self.lv_base = 1
		#for CreatePacket.create020e
		self.race = 0
		self.form = 0
		self.gender = 1
		self.hair = 0
		self.haircolor = 0
		self.wig = 0
		self.face = 0
		self.base_lv = 0
		self.ex = 0
		self.wing = 0
		self.wingcolor = 0
		self.wrprank = 0
		self.item = {1: Pet.Item(self.pict_id)}
		self.equip = Pet.Equip()
	
	def set_map(self, *args):
		with self.lock:
			return self._set_map(*args)
	def _set_map(self, map_id=None):
		if not map_id:
			map_id = self.map_id
		map_obj = db.map_obj.get(map_id)
		if not map_obj:
			return False
		#print self, "set_map", map_obj
		self.map_id = map_id
		if self.map_obj:
			with self.map_obj.lock:
				self.map_obj.pet_list.remove(self)
		self.map_obj = map_obj
		with self.map_obj.lock:
			if self not in self.map_obj.pc_list:
				self.map_obj.pet_list.append(self)
		return True
	
	def set_coord_from_master(self):
		with self.lock and self.master.lock:
			if self.master.dir == 0:
				self.set_coord(self.master.x, self.master.y-0.5)
			elif self.master.dir == 1:
				self.set_coord(self.master.x+0.5, self.master.y-0.5)
			elif self.master.dir == 2:
				self.set_coord(self.master.x+0.5, self.master.y)
			elif self.master.dir == 3:
				self.set_coord(self.master.x+0.5, self.master.y+0.5)
			elif self.master.dir == 4:
				self.set_coord(self.master.x, self.master.y+0.5)
			elif self.master.dir == 5:
				self.set_coord(self.master.x-0.5, self.master.y+0.5)
			elif self.master.dir == 6:
				self.set_coord(self.master.x-0.5, self.master.y)
			elif self.master.dir == 7:
				self.set_coord(self.master.x-0.5, self.master.y-0.5)
			else:
				self.set_coord(self.master.x, self.master.y)
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
	
	class Item:
		def __init__(self, i):
			self.item_id = i
			self.type = "HELM"
	class Equip:
		def __init__(self):
			self.head = 1
			self.face = 0
			self.chestacce = 0
			self.tops = 0
			self.bottoms = 0
			self.backpack = 0
			self.right = 0
			self.left = 0
			self.shoes = 0
			self.socks = 0
			self.pet = 0
