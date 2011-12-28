#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import struct
try: from cStringIO import StringIO
except: from StringIO import StringIO
from lib import db
from lib.site_packages import rijndael

ACCESORY_TYPE_LIST = ("ACCESORY_NECK",
				"JOINT_SYMBOL",
				)
UPPER_TYPE_LIST = ("ARMOR_UPPER",
				"ONEPIECE",
				"COSTUME",
				"BODYSUIT",
				"WEDDING",
				"OVERALLS",
				"FACEBODYSUIT",
				)
LOWER_TYPE_LIST = ("ARMOR_LOWER",
				"SLACKS",
				)
RIGHT_TYPE_LIST = ("CLAW",
				"HAMMER",
				"STAFF",
				"SWORD",
				"AXE",
				"SPEAR",
				"HANDBAG",
				"GUN",
				"ETC_WEAPON",
				"SHORT_SWORD",
				"RAPIER",
				"BOOK",
				"DUALGUN",
				"RIFLE",
				"THROW",
				"ROPE",
				"BULLET",
				"ARROW",
				)
LEFT_TYPE_LIST = ("BOW",
				"SHIELD",
				"LEFT_HANDBAG",
				"ACCESORY_FINGER",
				"STRINGS",
				)
BOOTS_TYPE_LIST = ("LONGBOOTS",
				"BOOTS",
				"SHOES",
				"HALFBOOTS",
				)
PET_TYPE_LIST = ("BACK_DEMON",
				"PET",
				"RIDE_PET",
				"PET_NEKOMATA",
				)

class Log:
	def __init__(self, handle, logpath):
		self.handle = handle
		self.logfile = open(logpath, "ab")
		self.logtime = True
	def write(self, s):
		self.handle.write(s)
		self.handle.flush()
		if self.logtime:
			self.logfile.write(time.strftime("[%y-%m-%d %H:%M:%S]", time.localtime()))
			self.logfile.write(" ")
		self.logfile.write(s)
		self.logtime = False
		if s.endswith("\n"):
			self.flush()
			self.logtime = True
	def flush(self):
		self.handle.flush()
		self.logfile.flush()
	def close(self):
		self.logfile.close()

def list_to_str(l):
	def appendspliter(item):
		return "%s,"%item
	return "".join(map(appendspliter, l))

def str_to_list(string):
	return list(map(int, filter(None, string.split(","))))

def get_item(item_id):
	item = db.item.get(int(item_id))
	if not item:
		item = db.item.get(10000000)
	return item.copy()

def get_config_io(path):
	with open(path, "rb") as r:
		config = r.read()
	if config.startswith("\xef\xbb\xbf"):
		config = config[3:]
	return StringIO(config.replace("\r\n", "\n"))

def pack(s, length):
	i = int(s)
	if length == 1:	return pack_byte(i)
	elif length == 2:	return pack_short(i)
	elif length == 4:	return pack_int(i)
	else:			print "pack error: unknow length", length
def unpack(s):
	if len(s) == 1:	return unpack_byte(s)
	elif len(s) == 2:	return unpack_short(s)
	elif len(s) == 4:	return unpack_int(s)
	else:			print "unpack error: unknow length", len(s)
def pack_int(i):
	return struct.pack(">I", i)
def pack_short(i):
	return struct.pack(">H", i)
def pack_byte(i):
	return struct.pack(">B", i)
def unpack_int(s):
	return struct.unpack(">I", s)[0]
def unpack_short(s):
	return struct.unpack(">H", s)[0]
def unpack_byte(s):
	return struct.unpack(">B", s)[0]
def pack_str(string):
	#65636f -> 04 65636f00
	if not string:
		return "\x01\x00"
	return pack_byte(len(string))+string+"\x00"
def unpack_str(code):
	length = unpack_byte(code[0])
	string = code[1:length+1]
	if string.endswith("\x00"):
		string = string[:-1]
	return string, length+1

def encode(string):
	if not string:
		print "encode error: not string"
		return
	key = "\x00"*16
	string_size = len(string)
	string += "\x00"*(16-len(string)%16)
	r = rijndael.rijndael(key, block_size=16)
	code = ""
	while string:
		code += r.encrypt(string[:16])
		string = string[16:]
	code_size = len(code)
	return pack_int(code_size)+pack_int(string_size)+code

def decode(code):
	if not code:
		print "decode error: not code"
		return
	#00000010 0000000c 6677bcf44144b39e28281ae8777db574
	string_size = unpack_int(code[4:8])
	code = code[8:]
	if len(code) % 16:
		print "decode error: len(code) % 16 != 0", code.encode("hex")
		return
	key = "\x00"*16
	r = rijndael.rijndael(key, block_size=16)
	string = ""
	while code:
		string += r.decrypt(code[:16])
		code = code[16:]
	return string[:string_size]
