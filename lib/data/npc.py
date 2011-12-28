#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

class Npc:
	def __init__(self, row):
		self.id = row[0]
		self.name = row[1]
	
	def copy(self):
		return copy.copy(self)
