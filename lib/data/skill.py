#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

class Skill:
	def __init__(self, row):
		self.skill_id = row[0]
		self.name = row[1]
		self.maxlv = row[4]
	
	def copy(self):
		return copy.copy(self)