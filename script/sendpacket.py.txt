#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
from lib import general
from lib.packet import packet
from lib.packet import login_data_handler
from lib.packet import map_data_handler
ID = 110
PACKET_START = 0x1ce9
PACKET_END = 0x1cea
PACKET_KNOWN_LIST = packet.name_map.keys()
PACKET_KNOWN_LIST += login_data_handler.LoginDataHandler.name_map.keys()
PACKET_KNOWN_LIST += map_data_handler.MapDataHandler.name_map.keys()

def main(pc):
	for packet_type in xrange(PACKET_START, PACKET_END):
		#create data
		data_type = general.pack_unsigned_short(packet_type)
		data_value = "\x00\x01"
		#skip known type
		if data_type.encode("hex") in PACKET_KNOWN_LIST:
			general.log("skip", data_type.encode("hex"))
			continue
		#create raw packet
		packet_raw = general.pack_short(len(data_value)+2)
		packet_raw += data_type
		packet_raw += data_value
		#create encrypted packet
		packet_enc = general.encode(packet_raw, pc.user.map_client.rijndael_key)
		#send
		general.log("send", data_type.encode("hex"), data_value.encode("hex"))
		pc.user.map_client.send_packet(packet_enc)
		#break