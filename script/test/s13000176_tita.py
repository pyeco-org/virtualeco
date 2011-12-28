#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *

class Script:
	def get_id(self):
		event_id = []
		event_id.append(13000176)
		return event_id
	def main(self,pc):
		say(pc,"......","ティタ",131)
		#npcshop(pc,event,1)
		#itemlist = npctrade(pc,event)
		#for x in itemlist:
		#	print x.Id,x.Count
		#print "npctrade over"
