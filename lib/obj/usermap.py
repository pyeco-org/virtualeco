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

def init():
	global usermaps
	from lib import usermaps