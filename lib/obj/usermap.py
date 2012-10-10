#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from lib import general
from lib.obj import map as obj_map

class UserMap(obj_map.Map):
	def __init__(self, usermap_type):
		obj_map.Map.__init__(self, {})
		self.__dict__.update(usermaps.USERMAP_DEFAULT_ATTR[usermap_type])
		self.usermap_type = usermap_type
		self.id = 0
		self.master = None
		self.entrance_map_id = 0
		self.entrance_x = 0
		self.entrance_y = 0
		self.entrance_event_id = 0
		self.entrance_title = ""
		self.flygarden = None
	
	def set_flygarden(self):
		self.flygarden = UserMap.Flygarden()
		self.flygarden.flying_base = 0
		self.flygarden.flying_sail = 0
		self.flygarden.garden_floor = 30010054 #芝生
		self.flygarden.garden_modelhouse = 30001200 #小さな家
		self.flygarden.house_outside_wall = 0
		self.flygarden.house_roof = 0
		self.flygarden.room_floor = 30050100 #クラシックな床
		self.flygarden.room_wall = 30040000 #クラシックな壁紙
		self.flygarden.unknow01 = 0
		self.flygarden.unknow02 = 0
		self.flygarden.unknow03 = 0
	
	class Flygarden:
		def __init__(self):
			for attr in general.FLYGARDEN_ATTR_LIST:
				setattr(self, attr, 0)

def init():
	global usermaps
	from lib import usermaps