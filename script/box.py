#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
ID = 90000074

def main(pc):
	result = script.select(pc, (
			"warehouse",
			"warp",
			"help",
			"quit",
			),
		"select")
	if result == 1:
		script.warehouse(pc, 0)
	elif result == 2:
		script.warp(pc, 50033000)
	elif result == 3:
		script.help(pc)
	elif result == 4:
		pass