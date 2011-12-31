#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class Npc:
	def __init__(self, row):
		self.npc_id = row[0]
		self.name = row[1]
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.npc_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))
