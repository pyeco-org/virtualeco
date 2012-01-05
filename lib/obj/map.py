#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import threading

class Map:
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.map_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))
	
	def __init__(self, row):
		self.map_id = row[0]
		self.name = row[1]
		self.centerx = row[2]
		self.centery = row[3]
		self.pc_list = []
		self.pet_list = []
		self.monster_list = []
		self.lock = threading.RLock()
