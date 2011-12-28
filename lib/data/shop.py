#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

class Shop:
	def __init__(self, row):
		self.item = map(int, filter(None, row[1:]))
	
	def copy(self):
		return copy.copy(self)