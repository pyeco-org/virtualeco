#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class Job:
	def __init__(self, row):
		self.job_id = row[0]
		self.name = row[1]
		self.hp_rate = row[2]
		self.mp_rate = row[3]
		self.sp_rate = row[4]
		self.payl_rate = row[5]
		self.capa_rate = row[6]
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.job_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))