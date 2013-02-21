#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
from lib.packet import packet
from lib.packet import login_data_handler
from lib.packet import map_data_handler
from lib.packet.packet_struct import *
ID = 110
PACKET_START = 0x020d
PACKET_END = 0x020d
PACKET_KNOWN_LIST = packet.name_map.keys()
PACKET_KNOWN_LIST += login_data_handler.LoginDataHandler.name_map.keys()
PACKET_KNOWN_LIST += map_data_handler.MapDataHandler.name_map.keys()

def make_122f(pet):
	"""pet info"""
	result = pack_int(pet.id)
	result += "\x03" #unknow
	result += pack_int(pet.master.id)
	result += pack_int(pet.master.id)
	result += pack_byte(pet.master.lv_base)
	result += pack_int(pet.master.wrprank)
	result += "\x00" #unknow
	result += pack_unsigned_byte(int(pet.x))
	result += pack_unsigned_byte(int(pet.y))
	result += pack_short(pet.speed)
	result += pack_byte(pet.dir)
	result += pack_int(pet.hp)
	result += pack_int(pet.maxhp)
	return result

def main(pc):
	from lib import monsters
	from lib import general
	#create data
	data_type = pack_unsigned_short(0x122f)
	data_value = make_122f(pc.pet)
	#skip known type
	#if data_type.encode("hex") in PACKET_KNOWN_LIST:
	#	general.log("skip", data_type.encode("hex"))
	#	continue
	#create raw packet
	packet_raw = pack_short(len(data_value)+2)
	packet_raw += data_type
	packet_raw += data_value
	#create encrypted packet
	packet_enc = general.encode(packet_raw, pc.user.map_client.rijndael_obj)
	#send
	general.log("send", data_type.encode("hex"), data_value.encode("hex"))
	pc.user.map_client.send_packet(packet_enc)
	#break
