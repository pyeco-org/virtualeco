#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import struct
import marshal
import traceback
try: from cStringIO import StringIO
except: from StringIO import StringIO

def pack_int(i):
	return struct.pack(">i", i)

def pack_short(i):
	return struct.pack(">h", i)

def pack_byte(i):
	return struct.pack(">b", i)

def pack_long(i):
	return struct.pack(">q", i)

def pack_unsigned_int(i):
	return struct.pack(">I", i)

def pack_unsigned_short(i):
	return struct.pack(">H", i)

def pack_unsigned_byte(i):
	return struct.pack(">B", i)

def pack_unsigned_long(i):
	return struct.pack(">Q", i)

def unpack_int(s):
	return struct.unpack(">i", s)[0]

def unpack_short(s):
	return struct.unpack(">h", s)[0]

def unpack_byte(s):
	return struct.unpack(">b", s)[0]

def unpack_long(i):
	return struct.unpack(">q", i)[0]

def unpack_unsigned_int(s):
	return struct.unpack(">I", s)[0]

def unpack_unsigned_short(s):
	return struct.unpack(">H", s)[0]

def unpack_unsigned_byte(s):
	return struct.unpack(">B", s)[0]

def unpack_unsigned_long(s):
	return struct.unpack(">Q", s)[0]

def unpack_str(code):
	io = StringIO(code)
	string = io_unpack_str(io)
	return string, io.tell()

def unpack_raw(code):
	io = StringIO(code)
	string = io_unpack_raw(io)
	return string, io.tell()

def unpack_array(code):
	io = StringIO(code)
	array = io_unpack_array(StringIO(code))
	return array, io.tell()

def io_unpack_int(io):
	return struct.unpack(">i", io.read(4))[0]

def io_unpack_short(io):
	return struct.unpack(">h", io.read(2))[0]

def io_unpack_byte(io):
	return struct.unpack(">b", io.read(1))[0]

def io_unpack_long(io):
	return struct.unpack(">q", io.read(8))[0]

def io_unpack_unsigned_int(io):
	return struct.unpack(">I", io.read(4))[0]

def io_unpack_unsigned_short(io):
	return struct.unpack(">H", io.read(2))[0]

def io_unpack_unsigned_byte(io):
	return struct.unpack(">B", io.read(1))[0]

def io_unpack_unsigned_long(io):
	return struct.unpack(">Q", io.read(8))[0]

def pack_str(string):
	#65636f -> 04 65636f00
	if not string:
		return "\x01\x00"
	string += "\x00"
	length = len(string)
	if length >= 253:
		return pack_unsigned_byte(253)+pack_unsigned_int(length)+string
	else:
		return pack_unsigned_byte(length)+string

def io_unpack_str(io):
	string = io_unpack_raw(io)
	while string.endswith("\x00"):
		string = string[:-1]
	return string

def io_unpack_raw(io):
	length = io_unpack_unsigned_byte(io)
	if length >= 253:
		length = io_unpack_unsigned_int(io)
	return io.read(length)

def io_unpack_short_str(io):
	string = io_unpack_short_raw(io)
	while string.endswith("\x00"):
		string = string[:-1]
	return string

def io_unpack_short_raw(io):
	length_data = io.read(2)
	if length_data == "":
		return ""
	length = unpack_unsigned_short(length_data)
	return io.read(length)

def pack_array(mod, array):
	if type(array) not in (list, tuple):
		array = tuple(array)
	length = len(array)
	if length >= 253:
		string = pack_unsigned_byte(253)+pack_unsigned_int(length)
	else:
		string = pack_unsigned_byte(length)
	for i in array:
		string += mod(i)
	return string

def io_unpack_array(mod, io):
	array = []
	length = io_unpack_unsigned_byte(io)
	if length >= 253:
		length = io_unpack_unsigned_int(io)
	for i in xrange(length):
		array.append(mod(io))
	return array

def pack_user_data(pack, user, attr):
	result = "\x04"
	for p in user.pc_list:
		result += pack(getattr(p, attr) if p else 0)
	return result

def pack_user_byte(*args):
	return pack_user_data(pack_byte, *args)

def pack_user_short(*args):
	return pack_user_data(pack_short, *args)

def pack_user_int(*args):
	return pack_user_data(pack_int, *args)

def pack_pict_id(item, item_type):
	return pack_int(item.get_pict_id(item_type) if item else 0)

def pack_item_int_attr(item, item_type, attr):
	return pack_int(item.get_int_attr(attr, item_type) if item else 0)

def pack_item_short_attr(item, attr, item_type):
	return pack_short(item.get_int_attr(attr, item_type) if item else 0)

def pack_item_byte_attr(item, attr, item_type):
	return pack_byte(item.get_int_attr(attr, item_type) if item else 0)

def pack_item_unsigned_byte_attr(item, attr, item_type):
	return pack_unsigned_byte(item.get_int_attr(attr, item_type) if item else 0)

def pack_item_str_attr(item, attr, item_type):
	return pack_str(item.get_str_attr(attr, item_type) if item else 0)
