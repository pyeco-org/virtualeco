#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import threading
from lib import general
PET_ID_START_FROM = 20000
pet_id_list = []
pet_list = []
pet_list_lock = threading.RLock()

def set_pet(pc):
	with pc.lock:
		if pc.pet:
			#print "set_pet failed: pc.pet exist"
			return
		if not pc.equip.pet:
			#print "set_pet failed: pc.equip.pet not exist"
			return False
		item = pc.item.get(pc.equip.pet)
	if not item:
		#print "set_pet failed: item not exist"
		return False
	pet = general.get_pet(item.petid)
	if not pet:
		#print "set_pet failed: pet not exist"
		return False
	pet.reset()
	with pet_list_lock:
		pet.id = get_new_pet_id()
		pet_list.append(pet)
		pet_id_list.append(pet.id)
	with pc.lock and pc.user.lock and pet.lock:
		pet.set_coord(pc.x, pc.y)
		pet.set_map(pc.map_id)
		pet.set_dir(pc.dir)
		pet.master = pc
		pc.pet = pet
		pc.user.map_client.send_map("122f", pet) #pet info
		print "[ pet ] set pet id %s"%(pc.pet.id)
	return True

def unset_pet(pc, logout):
	if not pc.pet:
		#print "unset_pet failed: pc.pet not exist"
		return
	with pc.lock and pc.user.lock and pc.pet.lock:
		if logout:
			pc.user.map_client.send_map_without_self("1234", pc.pet) ##hide pet
		else:
			pc.user.map_client.send_map("1234", pc.pet) ##hide pet
		with pet_list_lock:
			pet_list.remove(pc.pet)
			pet_id_list.remove(pc.pet.id)
		print "[ pet ] del pet id %s"%(pc.pet.id)
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

def get_new_pet_id():
	last_id = PET_ID_START_FROM
	with pet_list_lock:
		for i in sorted(pet_id_list):
			if i > last_id+1:
				return last_id+1
			else:
				last_id = i
	return last_id+1