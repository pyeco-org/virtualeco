#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Shop:
	def __init__(self, row):
		self.item = map(int, filter(None, row[1:]))
