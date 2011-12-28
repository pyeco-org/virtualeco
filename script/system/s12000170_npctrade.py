#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *

class Script:
	def get_id(self):
		event_id = []
		event_id.append(12000170)
		return event_id
	def main(self, pc):
		itemlist = npctrade(pc)
		for x in itemlist:
			print "[trade]", x.id, x.count
		print "[trade]","npctrade over"
		#print abc #test exceptinfo