#!/usr/bin/env python
# -*- coding: utf-8 -*-
import general

def make(data_type, *args):
	if args and hasattr(args[0], "lock"):
		with args[0].lock:
			data_value = eval("make_%s"%data_type)(*args)
	else:
		data_value = eval("make_%s"%data_type)(*args)
	if data_value == None:
		general.log_error("packet make error:", data_type, args)
		return ""
	packet = general.pack_short(len(data_value)+2)
	packet += data_type.decode("hex")
	packet += data_value
	#general.log("make", packet.encode("hex"))
	return packet

def make_0001(ver):
	"""version info"""
	return general.pack_int(ver)
