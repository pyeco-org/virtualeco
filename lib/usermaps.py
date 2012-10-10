#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
import traceback
from lib import env
from lib import general
from lib import script
MIN_USERMAP_ROPE_ID = 70000000
MAX_USERMAP_ROPE_ID = 71000000
USERMAP_TYPE_NONE = 0
USERMAP_TYPE_TENT = 1
USERMAP_TYPE_FLYGARDEN = 2
USERMAP_TYPE_HOME = 3
USERMAP_DEFAULT_ATTR = {
	USERMAP_TYPE_TENT: {
		"map_id": 0, "name": "テント", "centerx": 2.5, "centery": 3.5},
	USERMAP_TYPE_FLYGARDEN: {
		"map_id": 0, "name": "飛空庭", "centerx": 6.5, "centery": 6.5},
	USERMAP_TYPE_HOME: {
		"map_id": 0, "name": "家の中", "centerx": 5.5, "centery": 6.5,},
}
#id: UserMap
usermap_list = {}
usermap_list_lock = threading.RLock()

def id_in_range_rope(i):
	return (MIN_USERMAP_ROPE_ID < i < MAX_USERMAP_ROPE_ID)

def set_usermap(pc, usermap_type, x, y):
	unset_usermap(pc)
	with pc.lock:
		with usermap_list_lock:
			i = general.make_id(usermap_list, MIN_USERMAP_ROPE_ID)
			usermap_obj = obj_usermap.UserMap(usermap_type)
			usermap_obj.id = i
			usermap_obj.master = pc
			usermap_obj.map_id = i
			usermap_obj.entrance_map_id = pc.map_obj.map_id
			usermap_obj.entrance_x = x
			usermap_obj.entrance_y = y
			usermap_obj.entrance_event_id = i
			usermap_obj.entrance_title = "%sさんの飛空庭"%pc.name
			pc.usermap_obj = usermap_obj
			usermap_list[i] = usermap_obj
		general.log("[umaps] set usermap id", i)
		pc.map_send_map("0bb8", pc) #飛空庭のひも・テント表示
		script.unlock_move(pc)

def unset_usermap(pc, logout=False):
	with pc.lock:
		if not pc.usermap_obj:
			return
		i = pc.usermap_obj.id
		general.log("[umaps] del usermap id", i)
		usermap_obj = pc.usermap_obj
		map_obj = general.get_map(usermap_obj.entrance_map_id)
		if not map_obj:
			general.log_error(
				"[umaps] unset_usermap error: entrance_map_id not exist",
				usermap_obj.entrance_map_id,
			)
			return
		if logout:
			script.send_map_obj(map_obj, (pc,), "0bb9", pc) #飛空庭のひも・テント消去
		else:
			script.send_map_obj(map_obj, (), "0bb9", pc) #飛空庭のひも・テント消去
		for p in general.copy(usermap_obj.pc_list):
			if logout and p == pc:
				pc.set_map(usermap_obj.entrance_map_id)
				pc.set_coord(usermap_obj.entrance_x, usermap_obj.entrance_y)
				continue
			try:
				script.warp(
					p,
					usermap_obj.entrance_map_id,
					usermap_obj.entrance_x,
					usermap_obj.entrance_y,
				)
			except:
				general.log_error(traceback.format_exc())
		with usermap_list_lock:
			del usermap_list[i]
			pc.usermap_obj = None

def init():
	global obj_usermap, script
	from lib.obj import usermap as obj_usermap
	from lib import script
	obj_usermap.init()