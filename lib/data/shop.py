#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Shop:
	def __init__(self, d):
		d.update(self.__dict__)
		self.__dict__ = d
		self.item = filter(None, (int(self.__dict__[i]) for i in xrange(1, 14)))
