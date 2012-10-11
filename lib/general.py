#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import struct
import marshal
import traceback
import zipfile
#import thread
import hashlib
import random
import copy as py_copy
import ConfigParser
import math
import imp
import threading
import socket
try: from cStringIO import StringIO
except: from StringIO import StringIO
from lib import env
from lib import db
from lib import security
from lib.site_packages import rijndael
from lib.packet.packet_struct import *
RANGE_INT = (-2147483648, 2147483647)
RANGE_UNSIGNED_INT = (0, 4294967295)
RANGE_SHORT = (-32768, 32767)
RANGE_UNSIGNED_SHORT = (0, 65535)
RANGE_BYTE = (-128, 127)
RANGE_UNSIGNED_BYTE = (0, 255)
NULL = 0

ACCESORY_TYPE_LIST = (
	"ACCESORY_NECK",
	"JOINT_SYMBOL",
)
UPPER_TYPE_LIST = (
	"ARMOR_UPPER",
	"COSTUME",
	"BODYSUIT",
	"WEDDING",
	"OVERALLS",
	"FACEBODYSUIT",
	"PARTS_BODY", #dem
)
LOWER_TYPE_LIST = (
	"ARMOR_LOWER",
	"SLACKS",
	"PARTS_LEG", #dem
)
RIGHT_TYPE_LIST = (
	"CLAW",
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
	"STRINGS",
	"EXSWORD",
	"PARTS_BLOW", #dem
	"PARTS_SLASH", #dem
	"PARTS_STAB", #dem
	"PARTS_LONGRANGE", #dem
	"UNION_WEAPON", #pet
)
LEFT_TYPE_LIST = (
	"BOW",
	"SHIELD",
	"LEFT_HANDBAG",
	"ACCESORY_FINGER",
)
BOOTS_TYPE_LIST = (
	"LONGBOOTS",
	"BOOTS",
	"SHOES",
	"HALFBOOTS",
)
PET_TYPE_LIST = (
	"BACK_DEMON",
	"PET",
	"RIDE_PET",
	"PET_NEKOMATA",
)
HEAD_TYPE_LIST = (
	"HELM",
	"PARTS_HEAD", #dem
)
ACCESORY_HEAD_TYPE_LIST = (
	"ACCESORY_HEAD",
)
FULLFACE_TYPE_LIST = (
	"FULLFACE",
)
ACCESORY_FACE_TYPE_LIST = (
	"ACCESORY_FACE",
)
ONEPIECE_TYPE_LIST = (
	"ONEPIECE",
)
BACKPACK_TYPE_LIST = (
	"BACKPACK",
	"PARTS_BACK", #dem
)
SOCKS_TYPE_LIST = (
	"SOCKS",
)
PARTS_SET_TYPE_LIST = (
	#not using
	"SETPARTS_BLOW",
	"SETPARTS_STAB",
	"SETPARTS_SLASH",
)
EQUIP_ATTR_LIST = (
	"head",
	"face",
	"chestacce",
	"tops",
	"bottoms",
	"backpack",
	"right",
	"left",
	"shoes",
	"socks",
	"pet",
)
FLYGARDEN_ATTR_LIST = (
	"flying_base",
	"flying_sail",
	"garden_floor",
	"garden_modelhouse",
	"house_outside_wall",
	"house_roof",
	"room_floor",
	"room_wall",
	#"unknow01",
	#"unknow02",
	#"unknow03",
)

class NullClass: pass

class Log:
	def __init__(self, i, log_path):
		self.i = i
		self.log_path = log_path
		self.log_name = get_today()
		self.log_file = open(log_path%get_today(), "ab", base=env.LOG_DIR)
		self.log_time = True
	def write(self, s):
		try:
			self.i.write(get_str_log(s))
			self.i.flush()
			if self.log_time:
				if self.log_name != get_today():
					self.log_file.flush()
					self.log_file.close()
					self.log_name = get_today()
					self.log_file = open(
						self.log_path%self.log_name, "ab", base=env.LOG_DIR
					)
				self.log_file.write(time.strftime("[%H:%M:%S] ", time.localtime()))
			self.log_file.write(s.replace("\r\n", "\n").replace("\n", "\r\n"))
			self.log_time = False
			if s.endswith("\n"):
				self.flush()
				self.log_time = True
		except:
			env.STDERR.write("Log.write error: %s"%traceback.format_exc())
	def flush(self):
		try:
			self.i.flush()
			self.log_file.flush()
		except:
			env.STDERR.write("Log.flush error: %s"%traceback.format_exc())
	def close(self):
		try:
			self.i.close()
			self.log_file.close()
		except:
			env.STDERR.write("Log.close error: %s"%traceback.format_exc())

class LogConsole:
	def __init__(self, i):
		self.i = i
	def write(self, s):
		try:
			self.i.write(get_str_log(s))
		except:
			env.STDERR.write(traceback.format_exc())
	def flush(self):
		try:
			self.i.flush()
		except:
			env.STDERR.write(traceback.format_exc())
	def close(self):
		try:
			self.i.close()
		except:
			env.STDERR.write(traceback.format_exc())

def init():
	security.init(env.DEFAULT_BASE)
	security.secure_chdir()
	if env.USE_LOGFILE:
		if not os.path.exists(env.LOG_DIR):
			os.mkdir(env.LOG_DIR)
		sys.stdout = Log(env.STDOUT, env.STDOUT_LOG)
		sys.stderr = Log(env.STDERR, env.STDERR_LOG)
	else:
		sys.stdout = LogConsole(env.STDOUT)
		sys.stderr = LogConsole(env.STDERR)
	#ignore KeyboardInterrupt
	#break with EOFError or IOError [Errno 4]
	import signal
	signal.signal(signal.SIGINT, lambda *args: None)

def get_str(s):
	return str(s) if type(s) != unicode else s.encode("utf-8")
def get_unicode(s):
	try:
		return str(s).decode("utf-8") if type(s) != unicode else s
	except UnicodeDecodeError: #0x80+ bomb
		return unicode(s, "latin-1")
def get_str_log(s):
	return get_unicode(s).encode(env.SYSTEM_ENCODING)

def log(*args):
	sys.stdout.write(" ".join(map(get_str, args))+"\n")
def log_line(*args):
	sys.stdout.write(" ".join(map(get_str, args)))
def log_error(*args):
	sys.stderr.write(" ".join(map(get_str, args))+"\n")
def log_error_line(*args):
	sys.stderr.write(" ".join(map(get_str, args)))

def list_to_str(l):
	return ",".join(map(str, l))
def str_to_list(string):
	return list(map(int, filter(None, string.split(","))))

def stringio(string):
	return StringIO(string)
def copy(obj):
	return py_copy.deepcopy(obj)
def get_today():
	return time.strftime("%Y-%m-%d", time.localtime())
def randint(*args):
	return random.randint(*args)

def get_item(item_id):
	item = db.item.get(item_id)
	if not item:
		item = db.item.get(10000000)
	return copy(item)
def get_pet(pet_id):
	pet = db.pet_obj.get(pet_id)
	if not pet:
		return
	return pet
def get_monster(monster_id):
	monster = db.monster_obj.get(monster_id)
	if not monster:
		return
	return copy(monster)
def get_map(map_id):
	map_obj = db.map_obj.get(map_id)
	if not map_obj:
		return
	return map_obj #not need copy

def get_config_io(path, base=None):
	with open(path, "rb", base=base) as r:
		config = r.read()
	if config.startswith("\xef\xbb\xbf"):
		config = config[3:]
	return StringIO(config.replace("\r\n", "\n"))
def get_config(path=None, base=None):
	cfg = ConfigParser.SafeConfigParser()
	if path:
		cfg.readfp(get_config_io(path, base))
	return cfg

def load_dump(path, base=None):
	#simplejson and cPickle compatible all version of python but cannot dump script
	dump_path = str(path)+".dump"
	if not os.path.exists(dump_path):
		return
	magic_number = imp.get_magic()
	modify_time = struct.pack("<I", int(os.stat(path).st_mtime))
	with open(dump_path, "rb", base=base) as dump:
		try:
			if dump.read(4) != magic_number:
				return
			if dump.read(4) != modify_time:
				return
			if env.DUMP_WITH_ZLIB:
				return marshal.loads(dump.read().decode("zlib"))
			else:
				return marshal.loads(dump.read())
		except:
			log_error("dump file %s broken."%dump_path, traceback.format_exc())
def save_dump(path, obj, base=None):
	dump_path = str(path)+".dump"
	magic_number = imp.get_magic()
	modify_time = struct.pack("<I", int(os.stat(path).st_mtime))
	with open(dump_path, "wb", base=base) as dump:
		dump.write(magic_number)
		dump.write(modify_time)
		if env.DUMP_WITH_ZLIB:
			dump.write(marshal.dumps(obj).encode("zlib"))
		else:
			dump.write(marshal.dumps(obj))

def save_zip(*args):
	security.secure_save_zip(*args, compress=env.ZIP_COMPRESS)

def get_name_map(namespace, head):
	name_map = {}
	head_length = len(head)
	for key, value in namespace.iteritems():
		if not callable(value):
			continue
		if not key.startswith(head):
			continue
		name_map[key[head_length:]] = value
	return name_map

def int_to_bytes(i, length=0x100):
	hex_code = hex(i)
	if hex_code.startswith("0x"):
		hex_code = hex_code[2:]
	if hex_code.endswith("L"):
		hex_code = hex_code[:-1]
	return "0"*(length-len(hex_code))+hex_code
	#return hex_code+"0"*(length-len(hex_code))
def bytes_to_int(bytes):
	return int(bytes, 16)
def get_prime():
	#openssl genrsa -out private.key 2048
	#openssl rsa -in private.key -out public.key -pubout
	#openssl rsa -in private.key -text -noout
	#openssl prime prime
	#prime from rsa 2048 (prime1)
	#00:f9:39:fe:e9:20:9a:68:f2:4c:43:49:e1:c2:8e:
	#e2:31:7a:ec:6f:bd:16:80:f7:1d:14:a0:b3:76:0c:
	#62:05:bc:52:e6:50:bf:35:15:3c:ad:67:1b:be:1d:
	#a1:63:3d:63:e3:b2:1f:1d:a0:2a:f4:42:fd:f6:02:
	#b3:be:ba:09:fc:be:09:13:66:8f:4b:86:1e:14:d7:
	#a1:91:49:a9:d2:44:07:38:5f:30:b7:84:48:9f:5e:
	#29:3e:1d:d7:f4:72:56:12:d0:1f:ea:ed:07:2d:68:
	#79:ce:2b:3f:59:21:9e:df:72:b1:5c:5b:35:63:05:
	#42:72:03:f1:12:17:5d:bc:fd
	#int(..., 16)
	return 175012832246148469004952309893923119007504294868274830650101802243580016468616226644476369579140157420542034349400995694097261371077961674039236035533383172308367706779425637041402045013194820474112524204508905916696893254410707373670063475235242589213472899328698912258375583335003993274863729669402122894589
def get_private_key():
	#server private key
	return int(hashlib.sha512(str(time.time())).hexdigest(), 16)
def get_public_key(generator, private_key, prime):
	#server public key
	return pow(generator, private_key, prime)
def get_share_key_bytes(client_public_key, server_private_key, prime):
	#for get_rijndael_key
	return int_to_bytes(pow(client_public_key, server_private_key, prime))
def get_rijndael_key(share_key_bytes):
	rijndael_key_hex = ""
	for s in share_key_bytes[:32].lower():
		#if ord(s) > 57: rijndael_key_bytes += chr(ord(s)-48)
		#else: rijndael_key_bytes += s
		if s == "a": rijndael_key_hex += "1"
		elif s == "b": rijndael_key_hex += "2"
		elif s == "c": rijndael_key_hex += "3"
		elif s == "d": rijndael_key_hex += "4"
		elif s == "e": rijndael_key_hex += "5"
		elif s == "f": rijndael_key_hex += "6"
		else: rijndael_key_hex += s
	return rijndael_key_hex.decode("hex")

def encode(string, rijndael_obj):
	if not string:
		log_error("[error] encode error: string empty", string)
		return
	string_size = len(string)
	string += "\x00"*(16-len(string)%16)
	code = ""
	io = StringIO(string)
	with rijndael_obj.lock:
		while True:
			s = io.read(16)
			if not s:
				break
			code += rijndael_obj.encrypt(s)
	code_size = len(code)
	return pack_unsigned_int(code_size)+pack_unsigned_int(string_size)+code

def decode(code, rijndael_obj):
	if not code:
		log_error("[error] decode error: code empty", code)
		return
	if (len(code)-4) % 16:
		log_error("[error] decode error: length error", code.encode("hex"))
		return
	#0000000c 6677bcf44144b39e28281ae8777db574
	io = StringIO(code)
	string_size = io_unpack_int(io)
	string = ""
	with rijndael_obj.lock:
		while True:
			s = io.read(16)
			if not s:
				break
			string += rijndael_obj.decrypt(s)
	return string[:string_size]

def sin(angle): return math.sin(math.radians(angle))
def cos(angle): return math.cos(math.radians(angle))
def tan(angle): return math.tan(math.radians(angle))
def asin(ratio): return math.degrees(math.asin(ratio))
def acos(ratio): return math.degrees(math.acos(ratio))
def atan(ratio): return math.degrees(math.atan(ratio))
def get_angle_from_coord(pcx, pcy, x, y):
	disx = float(pcx-x)
	disy = float(pcy-y)
	if disx == 0:
		if disy == 0: return None
		elif disy > 0: return 180
		elif disy < 0: return 0
	elif disy == 0:
		if disx > 0: return 90
		elif disx < 0: return 270
	else:
		angle = abs(atan(disy/disx))
		if disx < 0 and disy > 0: # |/
			return 270-angle
		elif disx < 0 and disy < 0: # |\
			return 270+angle
		elif disx > 0 and disy > 0: # \|
			return 90+angle
		elif disx > 0 and disy < 0: # /|
			return 90-angle

def assert_value_range(name, value, value_range):
	if value < value_range[0]:
		raise ValueError(
			"%s < %s [%s]"%tuple(map(str, (name, value_range[0], value)))
		)
	elif value > value_range[1]:
		raise ValueError(
			"%s > %s [%s]"%tuple(map(str, (name, value_range[1], value)))
		)

def assert_address_not_used(addr):
	#cannot connect (0.0.0.0, port) on windows, socket errno 10049
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:	
		#s.settimeout(0.01)
		s.connect(addr)
	except:
		return
	finally:
		s.close()
	raise Exception("Address [%s] already in use"%str(addr))

def make_id(id_list_exist, min_id=0):
	#not thread safe
	i = min_id
	sorted_list = sorted(id_list_exist)
	for j in sorted_list:
		if j < min_id:
			continue
		if j > i+1:
			break
		else:
			i = j
	i += 1
	log("[gener] make_id", sorted_list, min_id, i)
	return i

def coord_in_range(x, y, xsrc, ysrc, xyr):
	xrad, yrad = (xyr[0]-1)/2, (xyr[1]-1)/2
	return ((abs(abs(x)-abs(xsrc)) <= xrad) and (abs(abs(y)-abs(ysrc)) <= yrad))

def start_thread(method, args):
	#use threading.Thread replace thread.start_new_thread
	#will list the active thread in threading.enumerate
	i = threading.Thread(None, method, None, args)
	i.setDaemon(True)
	i.start()
	return i