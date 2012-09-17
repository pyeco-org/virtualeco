#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import struct
import marshal
import traceback
import zipfile
import thread
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
from lib.site_packages import rijndael
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

# make server more safe from remote attack by special user input
# don't work if code or script writeable
def log_io(msg):
	STDERR.write(msg)
def within_base(path, base):
	return os.path.abspath(path).startswith(os.path.abspath(base))
def secure_open(name, mode="r", buffering=True, base=env.DEFAULT_BASE):
	#don't check symbolic links at this moment
	name = str(name)
	mode = str(mode)
	buffering = bool(buffering)
	base = str(base)
	#log_io("secure_open [%s] (%s) within [%s]\n"%(name, mode, base))
	if not within_base(name, base):
		raise IOError("cannot open [%s] (%s) outside of [%s]"%(name, mode, base))
	return __open(name, mode, buffering)
def secure_listdir(path, base=env.DEFAULT_BASE):
	path = str(path)
	base = str(base)
	#log_io("secure_listdir [%s] within [%s]\n"%(path, base))
	if not within_base(path, base):
		raise IOError("cannot list [%s] outside of [%s]"%(path, base))
	return __listdir(path)
def secure_remove(path, base=env.DEFAULT_BASE):
	path = str(path)
	base = str(base)
	#log_io("secure_remove [%s] within [%s]\n"%(path, base))
	if not within_base(path, base):
		raise IOError("cannot remove [%s] outside of [%s]"%(path, base))
	return __remove(path)
def secure_rmdir(path, base=env.DEFAULT_BASE):
	path = str(path)
	base = str(base)
	#log_io("secure_rmdir [%s] within [%s]\n"%(path, base))
	if not within_base(path, base):
		raise IOError("cannot remove dir [%s] outside of [%s]"%(path, base))
	return __rmdir(path)
def secure_mkdir(path, mode=0777, base=env.DEFAULT_BASE):
	path = str(path)
	mode = int(mode)
	base = str(base)
	#log_io("secure_mkdir [%s] (%s) within [%s]\n"%(path, mode, base))
	if not within_base(path, base):
		raise IOError("cannot create dir [%s] (%s) outside of [%s]"%(path, mode, base))
	return __mkdir(path)
def secure_rename(old, new, src_base=env.DEFAULT_BASE, dst_base=env.DEFAULT_BASE):
	old = str(old)
	new = str(new)
	src_base = str(src_base)
	dst_base = str(dst_base)
	#log_io("secure_rename from [%s] within [%s]\n"%(old, src_base))
	#log_io("secure_rename to [%s] within [%s]\n"%(new, dst_base))
	if not within_base(old, src_base):
		raise IOError("cannot rename from [%s] outside of [%s]"%(old, src_base))
	if not within_base(new, src_base):
		raise IOError("cannot rename to [%s] outside of [%s]"%(new, dst_base))
	return __rename(old, new)
def secure_chdir():
	return __chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
import __builtin__
__open = __builtin__.open
__listdir = os.listdir
__remove = os.remove
__rmdir = os.rmdir
__mkdir = os.mkdir
__rename = os.rename
__chdir = os.chdir
__builtin__.open = secure_open
__builtin__.file = secure_open
os.listdir = secure_listdir
os.remove = secure_remove
os.unlink = secure_remove
os.rmdir = secure_rmdir
os.mkdir = secure_mkdir
os.rename = secure_rename
def __raise(e): raise e
os.link = lambda *args: __raise(IOError("cannot create hard link everywhere"))
os.symlink = lambda *args: __raise(IOError("cannot create symbolic link everywhere"))
os.chdir = lambda *args: __raise(IOError("cannot chdir everywhere"))
if os.name == "posix":
	def secure_chmod(path, mode, base=env.DEFAULT_BASE):
		path = str(path)
		mode = int(mode)
		#log_io("secure_chmod [%s] (%s) within [%s]\n"%(path, mode, base))
		if not within_base(path, base):
			raise IOError(
				"cannot chmod [%s] (%s) outside of [%s]"%(path, mode, base)
			)
		return __chmod(path, mode)
	def secure_chown(path, uid, gid, base=env.DEFAULT_BASE):
		path = str(path)
		uid = int(uid)
		gid = int(gid)
		#log_io("secure_chown [%s] (%s, %s) within [%s]\n"%(path, uid, gid, base))
		if not within_base(path, mode, base):
			raise IOError(
				"cannot chown [%s] (%s, %s) outside of [%s]"%(path, uid, gid, base)
			)
		return __chown(path, uid, gid)
	__chmod = os.chmod
	__chown = os.chown
	os.chmod = secure_chmod
	os.chown = secure_chown
	os.chroot = lambda *args: __raise(IOError("cannot chroot everywhere"))
	os.mkfifo = lambda *args: __raise(IOError("cannot mkfifo everywhere"))

class NullClass: pass

class Log:
	def __init__(self, handle, base_path):
		self.handle = handle
		self.today = get_today()
		self.base_path = base_path
		self.logfile = open(base_path%self.today, "ab", base=env.LOG_DIR)
		self.logtime = True
	def write(self, s):
		try: self._write(s)
		except: self.handle.write("Log.write error: %s"%traceback.format_exc())
	def _write(self, s):
		self.handle.write(s)
		self.handle.flush()
		if self.logtime:
			if self.today != get_today():
				self.today = get_today()
				self.logfile.close()
				self.logfile = open(
					self.base_path%self.today, "ab", base=env.LOG_DIR
				)
			self.logfile.write(time.strftime("[%H:%M:%S]", time.localtime()))
			self.logfile.write(" ")
		self.logfile.write(s.replace("\r\n", "\n").replace("\n", "\r\n"))
		self.logtime = False
		if s.endswith("\n"):
			self.flush()
			self.logtime = True
	def flush(self):
		try: self._flush()
		except: self.handle.write("Log.flush error: %s"%traceback.format_exc())
	def _flush(self):
		self.handle.flush()
		self.logfile.flush()
	def close(self):
		try: self._close()
		except: self.handle.write("Log.close error: %s"%traceback.format_exc())
	def _close(self):
		self.logfile.close()

def use_log():
	if not os.path.exists(env.LOG_DIR):
		os.mkdir(env.LOG_DIR)
	sys.stdout = Log(env.STDOUT, env.STDOUT_LOG)
	sys.stderr = Log(env.STDERR, env.STDERR_LOG)

def get_str(s):
	return s.encode("utf-8") if type(s) == unicode else str(s)
def get_unicode(s):
	try:
		return s if type(s) == unicode else str(s).decode("utf-8")
	except UnicodeDecodeError: #0x80+ bomb
		return unicode(s, "latin-1")
def get_str_log(s):
	return get_unicode(s).encode(env.SYSTEM_ENCODING)

def log(*args):
	sys.stdout.write(" ".join(map(get_str_log, args))+"\n")
def log_line(*args):
	sys.stdout.write(" ".join(map(get_str_log, args)))
def log_error(*args):
	sys.stderr.write(" ".join(map(get_str_log, args))+"\n")
def log_error_line(*args):
	sys.stderr.write(" ".join(map(get_str_log, args)))

def list_to_str(l):
	return ",".join(map(str, l))
def str_to_list(string):
	return list(map(int, filter(None, string.split(","))))

def stringio(string):
	return StringIO(string)
def copy(obj):
	return py_copy.copy(obj)
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
	return copy(pet)
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

def get_config_io(path, base=env.DEFAULT_BASE):
	with open(path, "rb", base=base) as r:
		config = r.read()
	if config.startswith("\xef\xbb\xbf"):
		config = config[3:]
	return StringIO(config.replace("\r\n", "\n"))
def get_config(path=None, base=env.DEFAULT_BASE):
	cfg = ConfigParser.SafeConfigParser()
	if path:
		cfg.readfp(get_config_io(path, base))
	return cfg

def load_dump(path, base=env.DEFAULT_BASE):
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
def save_dump(path, obj, base=env.DEFAULT_BASE):
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

def secure_save_zip(path_src, path_zip,
	src_base=env.DEFAULT_BASE, zip_base=env.DEFAULT_BASE):
	path_src = str(path_src)
	path_zip = str(path_zip)
	src_base = str(src_base)
	zip_base = str(zip_base)
	#log_io("secure_save_zip from [%s] within [%s]\n"%(path_src, src_base))
	#log_io("secure_save_zip to [%s] within [%s]\n"%(path_zip, zip_base))
	if not within_base(path_src, src_base):
		raise IOError("cannot save zip from [%s] outside of [%s]"%(path_src, src_base))
	if not within_base(path_zip, zip_base):
		raise IOError("cannot save zip to [%s] outside of [%s]"%(path_src, zip_base))
	zip_obj = zipfile.ZipFile(path_zip, "w", getattr(zipfile, env.ZIP_MODE))
	for root, dirs, files in os.walk(path_src):
		for dir_name in dirs:
			zip_obj.write(os.path.join(root, dir_name),
				os.path.join(root, dir_name).replace(path_src, ""))
		for file_name in files:
			zip_obj.write(os.path.join(root, file_name),
				os.path.join(root, file_name).replace(path_src, ""))
	zip_obj.close()
save_zip = secure_save_zip

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

def pack_int(i):
	return struct.pack(">i", i)
def pack_short(i):
	return struct.pack(">h", i)
def pack_byte(i):
	return struct.pack(">b", i)
def unpack_int(s):
	return struct.unpack(">i", s)[0]
def unpack_short(s):
	return struct.unpack(">h", s)[0]
def unpack_byte(s):
	return struct.unpack(">b", s)[0]
def pack_unsigned_int(i):
	return struct.pack(">I", i)
def pack_unsigned_short(i):
	return struct.pack(">H", i)
def pack_unsigned_byte(i):
	return struct.pack(">B", i)
def unpack_unsigned_int(s):
	return struct.unpack(">I", s)[0]
def unpack_unsigned_short(s):
	return struct.unpack(">H", s)[0]
def unpack_unsigned_byte(s):
	return struct.unpack(">B", s)[0]
def pack_str(string):
	#65636f -> 04 65636f00
	if not string:
		return "\x01\x00"
	string += "\x00"
	return struct.pack(">B", len(string))+string #unsigned byte + char*
def unpack_str(code):
	string, length = unpack_raw(code)
	while string.endswith("\x00"):
		string = string[:-1]
	return string, length
def unpack_raw(code):
	length_data = code[:1]
	if length_data == "": return ""
	length = struct.unpack(">B", length_data)[0] #unsigned byte
	string = code[1:length+1]
	return string, length+1

def io_unpack_int(io):
	return struct.unpack(">i", io.read(4))[0]
def io_unpack_short(io):
	return struct.unpack(">h", io.read(2))[0]
def io_unpack_byte(io):
	return struct.unpack(">b", io.read(1))[0]
def io_unpack_unsigned_int(io):
	return struct.unpack(">I", io.read(4))[0]
def io_unpack_unsigned_short(io):
	return struct.unpack(">H", io.read(2))[0]
def io_unpack_unsigned_byte(io):
	return struct.unpack(">B", io.read(1))[0]
def io_unpack_str(io):
	string = io_unpack_raw(io)
	while string.endswith("\x00"):
		string = string[:-1]
	return string
def io_unpack_short_str(io):
	string = io_unpack_short_raw(io)
	while string.endswith("\x00"):
		string = string[:-1]
	return string
def io_unpack_raw(io):
	length_data = io.read(1)
	if length_data == "": return ""
	length = struct.unpack(">B", length_data)[0] #unsigned byte
	string = io.read(length)
	return string
def io_unpack_short_raw(io):
	length_data = io.read(2)
	if length_data == "": return ""
	length = struct.unpack(">H", length_data)[0] #unsigned short
	string = io.read(length)
	return string

def int_to_bytes(i, length=0x100):
	hex_code = hex(i)
	if hex_code.startswith("0x"):
		hex_code = hex_code[2:]
	if hex_code.endswith("L"):
		hex_code = hex_code[:-1]
	return "0"*(length-len(hex_code))+hex_code
	#return hex_code+"\x00"*(length-len(hex_code))
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
	return int(hashlib.sha1(str(time.time())).hexdigest(), 16)
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
		log_error("[error] encode error: not string", string)
		return
	#key = "\x00"*16
	string_size = len(string)
	string += "\x00"*(16-len(string)%16)
	code = ""
	with rijndael_obj.lock:
		for i in xrange(len(string)/16):
			code += rijndael_obj.encrypt(string[i*16:i*16+16])
	code_size = len(code)
	return pack_int(code_size)+pack_int(string_size)+code

def decode(code, rijndael_obj):
	if not code:
		log_error("[error] decode error: not code", code)
		return
	#0000000c 6677bcf44144b39e28281ae8777db574
	string_size = unpack_int(code[:4])
	if (len(code)-4) % 16:
		log_error("[error] decode error: (len(code)-4) % 16 != 0", code.encode("hex"))
		return
	#key = "\x00"*16
	string = ""
	with rijndael_obj.lock:
		for i in xrange(len(code)/16):
			string += rijndael_obj.decrypt(code[i*16+4:i*16+20])
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