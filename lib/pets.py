#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
from lib import general
PET_ID_START_FROM = 20000
MAX_PET_ID = 30000
pet_id_list = []
pet_list = []
pet_list_lock = threading.RLock()

def set_pet(pc):
	with pc.lock:
		if pc.pet:
			#general.log("[ pet ] set_pet failed: pc.pet exist")
			return
		if not pc.equip.pet:
			#general.log("[ pet ] set_pet failed: pc.equip.pet not exist")
			return False
		item = pc.item.get(pc.equip.pet)
		if not item:
			#general.log("[ pet ] set_pet failed: item not exist")
			return False
		pet = general.get_pet(item.petid)
		if not pet:
			#general.log("[ pet ] set_pet failed: pet not exist")
			return False
		pet.reset()
		with pet_list_lock:
			pet_id = general.make_id(pet_id_list, PET_ID_START_FROM)
			if pet_id >= MAX_PET_ID:
				general.log_error("[ pet ] ERROR: pet_id [%s] >= MAX_PET_ID"%pet_id)
				return False
			pet.id = pet_id
			pet_list.append(pet)
			pet_id_list.append(pet.id)
		with pc.user.lock and pet.lock:
			pc.pet = pet
			pet.master = pc
			pet.set_map(pc.map_id)
			pet.set_coord_from_master()
			pet.set_dir(pc.dir)
			pc.user.map_client.send_map("122f", pet) #pet info
			general.log("[ pet ] set pet id %s"%(pc.pet.id))
	return True

def unset_pet(pc, logout):
	with pc.lock:
		if not pc.pet:
			#general.log("[ pet ] unset_pet failed: pc.pet not exist")
			return
		with pc.user.lock and pc.pet.lock:
			if logout:
				pc.user.map_client.send_map_without_self("1234", pc.pet) ##hide pet
			else:
				pc.user.map_client.send_map("1234", pc.pet) ##hide pet
			with pet_list_lock:
				pet_list.remove(pc.pet)
				pet_id_list.remove(pc.pet.id)
			general.log("[ pet ] del pet id %s"%(pc.pet.id))
			pc.pet.reset()
			pc.pet = None
	return True

def get_pet_list():
	l = []
	with pet_list_lock:
		for pet in pet_list:
			l.append(pet)
	return l

def get_pet_from_id(i):
	for pet in get_pet_list():
		with pet.lock:
			if pet.id == i:
				return pet
