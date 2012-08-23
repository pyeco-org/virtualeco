#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class Job:
	def __init__(self, d):
		d.update(self.__dict__)
		self.__dict__ = d
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.job_id,
			self.name.decode("utf-8").encode(sys.getfilesystemencoding()))