#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *
import random

class Script:
	def __init__(self):
		self.warpdic = {}
		#ここからはテスト
		self.warpdic[10000817] = (30090001,4,7)#フシギ団本部→ヨーコの家
		self.warpdic[10000807] = (50033000,6,1,6,1)#ヨーコの家→フシギ団本部
		#ここまではテスト
		self.warpdic[10001031] = (30131001,5,9,6,9)#フシギ団の砦→フシギ団本部
		self.warpdic[10001030] = (10054000,156,138)#フシギ団本部→フシギ団の砦
	
	def get_id(self):
		return self.warpdic.keys()
	
	def main(self,pc):
		warpinfo = self.warpdic.get(int(pc.e.id))
		if warpinfo != None:
			mapid = warpinfo[0]
			if len(warpinfo) <= 3:
				x = warpinfo[1]
				y = warpinfo[2]
			else:
				x = random.randint(warpinfo[1], warpinfo[3])
				y = random.randint(warpinfo[2], warpinfo[4])
			warp(pc, mapid, x, y)
