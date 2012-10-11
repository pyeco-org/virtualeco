#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from lib import script
from lib import general
from lib import usermaps
ID = usermaps.MIN_FLYGARDEN_ID

def master_event(pc):
	r = script.select(pc, ("enter", "close", "cancel"), "master rope")
	if r == 1:
		script.warp(pc, pc.event_id, random.randint(6, 7), random.randint(10, 11))
	elif r == 2:
		usermaps.unset_usermap(pc)

def guest_event(pc):
	r = script.select(pc, ("enter", "cancel"), "guest rope")
	if r == 1:
		script.warp(pc, pc.event_id, random.randint(6, 7), random.randint(10, 11))

def main(pc):
	usermap_obj = usermaps.get_usermap_from_map_id(pc.event_id)
	if not usermap_obj:
		script.msg(pc, "rope error: usermap id %s not exist"%pc.event_id)
		return
	general.log(usermap_obj.master, pc)
	if usermap_obj.master == pc:
		master_event(pc)
	else:
		guest_event(pc)