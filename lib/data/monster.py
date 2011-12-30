#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

class Monster:
	def __init__(self, row):
		self.monster_id = row[0]
		self.name = row[1]
		self.sid = 0 # >10000
		self.charid = 0 # = sid
		self.map = 0
		self.x = 0
		self.y = 0
		self.dir = 0
		self.centerx = 0
		self.centery = 0
		self.rawx = 0
		self.rawy = 0
		self.rawdir = 0
		self.speed = 420
		self.hp = 100
		self.maxhp = 100
		self.mp = 1
		self.maxmp = 1
		self.sp = 1
		self.maxsp = 1
		self.ep = 0
		self.maxep = 0
		self.npc = False
		self.last_move_count = 0
		self.counter_attack_delay_count = 0
		self.moveable_area = 5
		self.die = 0 #hide after 5 sec
		self.damagedic = None #if set {} , will bug on copy.copy
	
	def copy(self):
		return copy.copy(self)