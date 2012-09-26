#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
import random
rand = random.randint
ID = 90000074

def main(pc):
	result = script.select(pc, (
		"warehouse",
		"warp",
		"help",
		"printallequip",
		"unsetallequip",
		"switchspeed",
		"cancel",
	), "select")
	if result == 1:
		script.warehouse(pc, 0)
	elif result == 2:
		script.warp(pc, 10023100, rand(252, 253), rand(126, 129))
	elif result == 3:
		script.help(pc)
	elif result == 4:
		script.printallequip(pc)
	elif result == 5:
		script.unsetallequip(pc)
	elif result == 6:
		if pc.status.speed == 410:
			script.speed(pc, 820)
		else:
			script.speed(pc, 410)
