#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
import traceback
import time
from lib import db
from lib import general

class Pet:
	def __init__ (self, d):
		d.update(self.__dict__)
		self.__dict__ = d
		self.hp = self.maxhp
		self.map_id = 0
		self.map_obj = None
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.pet_id, self.name)
	
	def reset(self, item=None):
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
		self.motion_id = 111
		self.motion_loop = False
		self.standby = False
		self.lv_base = 1
		#packet.make_020b
		self.race = -1
		self.form = -1
		self.gender = -1
		self.hair = -1
		self.haircolor = -1
		self.wig = -1
		self.face = -1
		self.base_lv = -1
		self.ex = -1
		self.wing = -1
		self.wingcolor = -1
		self.wrprank = -1
		self.size = 1000
		#packet.make_09e9
		if not item:
			return
		self.item = {1: data_item.Item({
			"item_id": -1,
			"pict_id": item.__dict__.get("pet_pict_id") or self.pict_id,
			"type": "HELM",
		})}
		self.equip = obj_pc.PC.Equip()
		self.equip.head = 1
		i = item.__dict__.get("pet_weapon_id")
		if i:
			self.item[7] = general.get_item(i)
			self.equip.right = 7
	
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
				self.map_obj.pet_list.remove(self)
		self.map_obj = map_obj
		with self.map_obj.lock:
			if self not in self.map_obj.pet_list:
				with self.map_obj.lock:
					self.map_obj.pet_list.append(self)
		return True
	
	def set_motion(self, motion_id, motion_loop):
		with self.lock:
			self.motion_id = motion_id
			self.motion_loop = True if motion_loop else False
		self.master.map_send_map(
			"121c", self.master, self.id, self.motion_id, self.motion_loop
		) #モーション通知
	
	def set_coord_from_master(self):
		#instead by _run_near_master, only use in pets.set_pet
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

class PetObject(threading.Thread, Pet):
	def __init__(self, data):
		self.__dict__.update(data.__dict__)
		threading.Thread.__init__(self)
		self.name = data.name #set thread name to pet name
		self.wait_motion = None
		self.wait_motion_loop = None
		self.wait_motion_time = None
		self.wait_move_time = None
		self.setDaemon(True)
		self.running = True
	
	def __str__(self):
		if self.master:
			return "%s<%s, %s>"%(repr(self), self.pet_id, self.master.id)
		else:
			return "%s<%s, %s>"%(repr(self), self.pet_id, -1)
	
	def stop(self):
		#will block 0 ~ sleep sec in join()
		self.running = False
		self.join()
		if self.map_obj:
			with self.map_obj.lock:
				self.map_obj.pet_list.remove(self)
		general.log("[ pet ] %s stop"%self)
	
	def _run_near_master(self):
		if self.standby:
			return
		if time.time() - self.wait_move_time < 0.5:
			return
		self.wait_move_time = time.time()
		i = self.master.x - self.x
		j = self.master.y - self.y
		n = abs(i)
		m = abs(j)
		if n<=1 and m<=1:
			return
		if n > m:
			x = self.x if (n<=1) else ((self.x+1) if (i>0) else (self.x-1))
			y = self.y if (m<=1) else ((self.y+m/n) if (j>0) else (self.y-m/n))
		else:
			x = self.x if (n<=1) else ((self.x+n/m) if (i>0) else (self.x-n/m))
			y = self.y if (m<=1) else ((self.y+1) if (j>0) else (self.y-1))
		self.set_coord(x, y)
		self.master.map_send_map("11f9", self, 0x06) #キャラ移動アナウンス #歩き
	
	def _run_set_motion(self):
		if not self.wait_motion_time:
			return
		if time.time()<self.wait_motion_time:
			return
		self.set_motion(self.wait_motion, self.wait_motion_loop)
		self.wait_motion = None
		self.wait_motion_loop = None
		self.wait_motion_time = None
	
	def _run(self):
		self._run_near_master()
		self._run_set_motion()
	
	def run(self):
		try:
			general.log("[ pet ] %s start"%self)
			self.wait_move_time = time.time()+1
			while self.running:
				self._run()
				time.sleep(0.1)
		except:
			general.log_error(traceback.format_exc())
			general.log_error(self, self.master)

def init():
	global data_item, obj_pc
	from lib.data import item as data_item
	from lib.obj import pc as obj_pc
