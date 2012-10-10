#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from lib import script
from lib import general
from lib import usermaps
ID = 12001110 #操舵輪

def master_event(pc, usermap_obj):
	r = script.select(pc, ("leave", "cancel"), "master panel")
	if r == 1:
		script.warp(
			pc,
			usermap_obj.entrance_map_id,
			usermap_obj.entrance_x,
			usermap_obj.entrance_y,
		)

def guest_event(pc, usermap_obj):
	r = script.select(pc, ("leave", "cancel"), "guest panel")
	if r == 1:
		script.warp(
			pc,
			usermap_obj.entrance_map_id,
			usermap_obj.entrance_x,
			usermap_obj.entrance_y,
		)

def main(pc):
	with usermaps.usermap_list_lock:
		usermap_obj = usermaps.usermap_list.get(pc.map_obj.map_id)
	if not usermap_obj:
		script.msg(pc, "rope error: usermap id %s not exist"%pc.map_obj.map_id)
		return
	general.log(usermap_obj.master, pc)
	if usermap_obj.master == pc:
		master_event(pc, usermap_obj)
	else:
		guest_event(pc, usermap_obj)