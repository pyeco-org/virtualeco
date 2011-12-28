#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

class Map:
	def __init__(self, row):
		self.id = row[0]
		self.name = row[1]
		self.centerx = row[2]
		self.centery = row[3]
	
	def copy(self):
		return copy.copy(self)