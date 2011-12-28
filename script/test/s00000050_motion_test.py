#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *

class Script:
	def get_id(self):
		event_id = []
		event_id.append("00000050")
		return event_id

	def main(self,pc):
		motionid = 400
		option = ["次へ", "前へ", "終了"]
		while True:
			title = "motion %s" % (motionid, )
			result = select(pc, option, title)
			if result == 1:
				motionid += 1
				motion(pc, motionid, 1)
			elif result == 2:
				motionid -= 1
				motion(pc, motionid, 1)
			else:
				break
