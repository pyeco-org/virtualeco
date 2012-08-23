#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import threading
from lib import general
from lib import script
from lib.obj import mapitem

class Map:
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.map_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))
	
	def __init__(self, d):
		d.update(self.__dict__)
		self.__dict__ = d
		self.pc_list = []
		self.pet_list = []
		self.monster_list = []
		self.mapitem_list = []
		self.lock = threading.RLock()
	
	def mapitem_append(self, item, x, y, id_from):
		with self.lock:
			mapitem_id = general.make_id(mi.id for mi in self.mapitem_list)
			mapitem_obj = mapitem.MapItem(item, x, y, id_from, mapitem_id)
			self.mapitem_list.append(mapitem_obj)
			script.send_map_obj(self, (), "07d5", mapitem_obj) #drop item info
	
	def mapitem_pop(self, mapitem_id):
		with self.lock:
			mapitem_obj = None
			for mi in self.mapitem_list:
				if mapitem_id == mi.id:
					mapitem_obj = mi
					self.mapitem_list.remove(mapitem_obj)
					break
		return mapitem_obj
