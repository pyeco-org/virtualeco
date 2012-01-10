#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import random
import struct
import traceback
import hashlib
import copy as py_copy
try: from cStringIO import StringIO
except: from StringIO import StringIO
sys.path.append("../site_packages")
import rijndael

def log(*args):
	sys.stdout.write("".join(map(lambda s: str(s)+" ", args))[:-1]+"\n")
def log_line(*args):
	sys.stdout.write("".join(map(lambda s: str(s)+" ", args)))
def log_error(*args):
	sys.stderr.write("".join(map(lambda s: str(s)+" ", args))[:-1]+"\n")
def log_error_line(*args):
	sys.stderr.write("".join(map(lambda s: str(s)+" ", args)))

def stringio(string):
	return StringIO(string)
def copy(obj):
	return py_copy.copy(obj)
def get_today():
	return time.strftime("%Y-%m-%d", time.localtime())
def randint(*args):
	return random.randint(*args)

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
def get_private_key():
	#server private key
	return int(hashlib.sha1(str(time.time())).hexdigest(), 16)
def get_public_key(generator, private_key, prime):
	#server public key
	return pow(generator, private_key, prime)
def get_share_key_bytes(server_public_key, client_private_key, prime):
	#for get_rijndael_key
	return int_to_bytes(pow(server_public_key, client_private_key, prime))
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

def encode(string, key):
	if not string:
		log_error("encode error: not string", string)
		return
	#key = "\x00"*16
	string_size = len(string)
	string += "\x00"*(16-len(string)%16)
	r = rijndael.rijndael(key, block_size=16)
	code = ""
	for i in xrange(len(string)/16):
		code += r.encrypt(string[i*16:i*16+16])
	code_size = len(code)
	return pack_int(code_size)+pack_int(string_size)+code
def decode(code, key):
	if not code:
		log_error("decode error: not code", code)
		return
	#00000010 0000000c 6677bcf44144b39e28281ae8777db574
	string_size = unpack_int(code[4:8])
	#code = code[8:]
	if (len(code)-8) % 16:
		log_error("decode error: (len(code)-8) % 16 != 0", code.encode("hex"))
		return
	#key = "\x00"*16
	r = rijndael.rijndael(key, block_size=16)
	string = ""
	for i in xrange(len(code)/16):
		string += r.decrypt(code[i*16+8:i*16+24])
	return string[:string_size]