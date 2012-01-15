#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import thread
import threading
import traceback
import struct
from lib import general
from lib.packet.login_data_handler import LoginDataHandler
from lib.packet.map_data_handler import MapDataHandler
SERVER_CONFIG = "./server.ini"
BIND_ADDRESS = "0.0.0.0"
MAX_CONNECTION_FROM_ONE_IP = 3
USE_NULL_KEY = False #emergency option
if USE_NULL_KEY:
	GENERATOR = 1
	PRIME = 0
	PRIVATE_KEY = 0
	PUBLIC_KEY = 0
	PRIME_BYTES = "\x00"*0x100
	PUBLIC_KEY_BYTES = "\x00"*0x100
else:
	#get key info (server private key / public key)
	GENERATOR = 2
	PRIME = general.get_prime()
	PRIVATE_KEY = general.get_private_key()
	PUBLIC_KEY = general.get_public_key(GENERATOR, PRIVATE_KEY, PRIME)
	#get bytes
	PRIME_BYTES = general.int_to_bytes(PRIME)
	PUBLIC_KEY_BYTES = general.int_to_bytes(PUBLIC_KEY)
	#general.log("prime:", PRIME_BYTES, "\nlength:", len(PRIME_BYTES))
	#general.log("public key:", PUBLIC_KEY_BYTES, "\nlength:", len(PUBLIC_KEY_BYTES))
	#get key exchange packet
PACKET_KEY_EXCHANGE = "".join((
	general.pack_int(0), #head
	general.pack_int(1)+str(GENERATOR), #generator
	general.pack_int(0x100)+PRIME_BYTES, #prime
	general.pack_int(0x100)+PUBLIC_KEY_BYTES #server public key
	))
PACKET_INIT = "\x00\x00\x00\x00\x00\x00\x00\x10"
PACKET_INIT_LENGTH = len(PACKET_INIT)
PACKET_NULL_KEY = "\x00\x00\x00\x01\x30"
VALUE_NULL_KEY = 0

class StandardServer(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.port = port
		self.client_list = []
		self.lock = threading.RLock()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((BIND_ADDRESS, port))
		self.socket.listen(10)
		self.start()
	def ip_count_check(self, src):
		with self.lock:
			ip = src[0]
			ip_count = 1
			for client in self.client_list:
				if ip == client.src_address[0]:
					ip_count += 1
			general.log("[ srv ] src: %s ip_count: %s"%(src, ip_count))
			if ip_count > MAX_CONNECTION_FROM_ONE_IP:
				return False
			else:
				return True
	def run(self):
		while True:
			try:
				s, src = self.socket.accept()
				if not self.ip_count_check(src):
					s.close()
					continue
				with self.lock:
					self.handle_client(s, src)
			except:
				general.log_error(traceback.format_exc())
class StandardClient(threading.Thread):
	def __init__(self, master, s, src):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.lock = threading.RLock()
		self.master = master
		self.socket = s
		self.src_address = src
		self.buf = ""
		self.running = True
		self.recv_init = False
		self.recv_key = False
		self.rijndael_key = None
		self.start()
	def __str__(self):
		return "%s<%s:%s>"%(repr(self), self.src_address[0], self.src_address[1])
	def recv_packet(self, length):
		data = self.socket.recv(length)
		if not self.running:
			raise IOError("not self.running")
		if not data:
			raise EOFError("not data")
		return data
	def recv_key_packet(self):
		return self.recv_packet(general.unpack_int(self.recv_packet(4)))
	def recv_enc_packet(self):
		return self.recv_packet(general.unpack_int(self.recv_packet(4))+4)
	def run(self):
		while self.running:
			try:
				self.handle_packet()
			except:
				self.stop()
		general.log("quit", self)
	def send_packet(self, packet):
		with self.lock:
			#general.log("[ srv ] send", packet.encode("hex"))
			self.socket.sendall(packet)
	def handle_packet(self):
		if not self.recv_init:
			packet = self.recv_packet(PACKET_INIT_LENGTH)
			if packet != PACKET_INIT:
				raise ValueError("packet != PACKET_INIT")
			self.recv_init = True
			self.send_packet(PACKET_KEY_EXCHANGE)
		elif not self.recv_key:
			#get client public key
			client_public_key_bytes = self.recv_key_packet()
			client_public_key = general.bytes_to_int(client_public_key_bytes)
			#general.log("[ srv ] client key:", client_public_key_bytes)
			#general.log("[ srv ] length:", len(client_public_key_bytes))
			self.recv_key = True
			if USE_NULL_KEY:
				if client_public_key != VALUE_NULL_KEY:
					raise ValueError("client_public_key != VALUE_NULL_KEY")
				self.rijndael_key = "\x00"*0x10
			else:
				#get share key
				share_key_bytes = general.get_share_key_bytes(
					client_public_key, PRIVATE_KEY, PRIME)
				general.log("[ srv ] share key:", share_key_bytes)
				#general.log("[ srv ] length:", len(share_key_bytes))
				#get rijndael key (str)
				self.rijndael_key = general.get_rijndael_key(share_key_bytes)
			general.log("[ srv ] rijndael key:", self.rijndael_key.encode("hex"))
		else:
			packet = self.recv_enc_packet()
			with self.lock:
				try:
					self.handle_data(general.decode(packet, self.rijndael_key))
				except:
					general.log_error(traceback.format_exc())
	def _stop(self):
		if not self.running:
			return
		with self.lock:
			self.socket.close()
			self.running = False
			with self.master.lock:
				self.master.client_list.remove(self)

class LoginServer(StandardServer):
	def handle_client(self, s, src):
		self.client_list.append(LoginClient(self, s, src))
class MapServer(StandardServer):
	def handle_client(self, s, src):
		self.client_list.append(MapClient(self, s, src))
class LoginClient(StandardClient, LoginDataHandler):
	def __init__(self, *args):
		general.log("new login client", args)
		LoginDataHandler.__init__(self)
		StandardClient.__init__(self, *args)
class MapClient(StandardClient, MapDataHandler):
	def __init__(self, *args):
		general.log("new map client", args)
		MapDataHandler.__init__(self)
		StandardClient.__init__(self, *args)

def load():
	from lib.obj import serverconfig
	global config
	config = serverconfig.ServerConfig(SERVER_CONFIG)
	global loginserver
	loginserver = LoginServer(config.loginserverport)
	general.log("Start login server with\t%s:%d"%(BIND_ADDRESS, config.loginserverport))
	global mapserver
	mapserver = MapServer(config.mapserverport)
	general.log("Start map server with\t%s:%d"%(BIND_ADDRESS, config.mapserverport))