#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
import random

ID = {
	10000170: (20000000, 62, 23, 66, 24), #東アクロニア海岸→大陸の洞窟Ｂ１Ｆ
	10000182: (20010000, 62, 11, 65, 13), #スノップ雪原→氷結の坑道Ｂ１Ｆ
	10000484: (20014000, 241, 12, 243, 14), #ノース中央山脈（南側）→ノーザンダンジョン
	10000236: (20030000, 62, 10, 65, 12) #軍艦島→廃炭鉱Ｂ１Ｆ
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

#Copyright (C) ゆとり鯖 All Rights Reserved.
