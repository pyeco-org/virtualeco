#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from lib import script
from lib import general
from lib import usermaps
ID = usermaps.MIN_USERMAP_ROPE_ID

def master_event(pc):
	r = script.select(pc, ("enter", "close", "cancel"), "rope")
	if r == 1:
		script.warp(pc, i, random.randint(6, 7), random.randint(10, 11))
	elif r == 2:
		usermaps.unset_usermap(pc)

def guest_event(pc):
	r = script.select(pc, ("enter", "cancel"), "rope")
	if r == 1:
		script.warp(pc, i, random.randint(6, 7), random.randint(10, 11))

def main(pc):
	i = pc.event_id
	with usermaps.usermap_list_lock:
		usermap_obj = usermaps.usermap_list.get(i)
	if not usermap_obj:
		msg(pc, "rope error: usermap id %s not exist"%i)
		return
	general.log(usermap_obj.master, pc)
	if usermap_obj.master == pc:
		master_event(pc)
	else:
		guest_event(pc)