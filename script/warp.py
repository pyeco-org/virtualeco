#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
import random

ID = {
	10000817: (30090001, 4, 7), #フシギ団本部→ヨーコの家
	10000807: (50033000, 6, 1, 6, 1), #ヨーコの家→フシギ団本部
	10001031: (30131001, 5, 9, 6, 9), #フシギ団の砦→フシギ団本部
	10001030: (10054000, 156, 138) #フシギ団本部→フシギ団の砦
}

def main(pc):
	warp_info = ID[pc.event_id]
	map_id = warp_info[0]
	if len(warp_info) == 3:
		x = warp_info[1]
		y = warp_info[2]
	else:
		x = random.randint(warp_info[1], warp_info[3])
		y = random.randint(warp_info[2], warp_info[4])
	script.warp(pc, map_id, x, y)
