#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *

class Script:
	def get_id(self):
		event_id = []
		event_id.append("00000010")
		return event_id

	def main(self,pc):
		testword = "テスト_ディクショナリー"
		option = list()
		option.append("set pc.dic[\""+testword+"\"] True")
		option.append("set pc.dic[\""+testword+"\"] False")
		option.append("cancel")
		while True:
			value = pc.dic.get(testword)
			title = "pc.dic[\""+testword+"\"] is "+str(value)
			result = select(pc, option, title)
			if result == 1:
				pc.dic[testword] = "True"
			elif result == 2:
				pc.dic[testword] = "False"
			else:
				break



