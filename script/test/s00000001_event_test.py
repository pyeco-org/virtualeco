#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *

class Script:
	def get_id(self):
		event_id = []
		event_id.append("00000001")
		return event_id

	def main(self,pc):
		playjin(pc, 4000)
