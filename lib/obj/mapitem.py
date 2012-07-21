#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import threading

class MapItem:
	def __init__(self, item, x, y, id_from, id):
		self.id = id
		self.id_from = id_from
		self.x = int(x)
		self.y = int(y)
		self.item = item
		self.lock = threading.RLock()