#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class Skill:
	def __init__(self, row):
		self.skill_id = row[0]
		self.name = row[1]
		self.maxlv = row[4]
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.skill_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))