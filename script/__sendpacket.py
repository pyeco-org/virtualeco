#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
from lib import general
from lib.packet import packet
from lib.packet import login_data_handler
from lib.packet import map_data_handler
ID = 110
PACKET_START = 0x0226
PACKET_END = 0x0226
#PACKET_KNOWN_LIST = packet.name_map.keys()
#PACKET_KNOWN_LIST += login_data_handler.LoginDataHandler.name_map.keys()
#PACKET_KNOWN_LIST += map_data_handler.MapDataHandler.name_map.keys()

def main(pc):
	for packet_type in xrange(PACKET_START, PACKET_END+1):
		#create data
		data_type = general.pack_unsigned_short(packet_type)
		i = 1
		data_value = general.pack_byte(i)
		data_value += general.pack_short(3054)
		data_value += general.pack_byte(i)
		data_value += general.pack_byte(5)
		data_value += general.pack_byte(i)
		data_value += general.pack_byte(0)
		data_value += general.pack_byte(i)
		data_value += general.pack_byte(0)
		data_value += general.pack_byte(0) #job
		data_value += general.pack_byte(i)
		#skip known type
		#if data_type.encode("hex") in PACKET_KNOWN_LIST:
		#	general.log("skip", data_type.encode("hex"))
		#	continue
		#create raw packet
		packet_raw = general.pack_short(len(data_value)+2)
		packet_raw += data_type
		packet_raw += data_value
		#create encrypted packet
		packet_enc = general.encode(packet_raw, pc.user.map_client.rijndael_obj)
		#send
		general.log("send", data_type.encode("hex"), data_value.encode("hex"))
		pc.user.map_client.send_packet(packet_enc)
		#break