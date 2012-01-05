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
PACKET_NULL_KEY = "\x00\x00\x00\x01\x30"

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
	def run(self):
		while self.running:
			try:
				packet = self.socket.recv(1024)
				#general.log("[ srv ] recv", packet.encode("hex"))
				if not self.running:
					break
				if not packet:
					raise Exception
				try:
					self.buf += packet
					with self.lock:
						self.handle_packet()
				except:
					general.log_error(traceback.format_exc())
			except:
				self.stop()
		general.log("quit", self)
	def send_packet(self, packet):
		with self.lock:
			#general.log("[ srv ] send", packet.encode("hex"))
			self.socket.sendall(packet)
	def handle_packet(self):
		if not self.recv_init:
			if self.buf.startswith(PACKET_INIT):
				self.recv_init = True
				self.buf = self.buf[len(PACKET_INIT):]
				self.send_packet(PACKET_KEY_EXCHANGE)
			else:
				self.stop()
		elif not self.recv_key:
			if USE_NULL_KEY:
				if self.buf.startswith(PACKET_NULL_KEY):
					self.recv_key = True
					self.buf = self.buf[len(PACKET_NULL_KEY):]
					self.rijndael_key = "\x00"*0x10
				else:
					self.stop()
			else:
				#get client public key
				client_public_key_length = general.unpack_int(self.buf[:4])
				if len(self.buf) < client_public_key_length+4:
					general.log_error(
						"[ srv ] error: len(self.buf) < client_public_key_length+4",
						self.buf.encode("hex"))
					return
				client_public_key_bytes = self.buf[4:client_public_key_length+4]
				client_public_key = general.bytes_to_int(client_public_key_bytes)
				self.buf = self.buf[client_public_key_length+4:]
				self.recv_key = True
				#general.log("[ srv ] client key:", client_public_key_bytes)
				#general.log("[ srv ] length:", len(client_public_key_bytes))
				#get share key
				share_key_bytes = general.get_share_key_bytes(
					client_public_key, PRIVATE_KEY, PRIME)
				general.log("[ srv ] share key:", share_key_bytes)
				#general.log("[ srv ] length:", len(share_key_bytes))
				#get rijndael key (str)
				self.rijndael_key = general.get_rijndael_key(share_key_bytes)
			general.log("[ srv ] rijndael key:", self.rijndael_key.encode("hex"))
		else:
			#00000010 0000000c 6677bcf44144b39e28281ae8777db574
			packet_length = general.unpack_int(self.buf[:4])+8
			if packet_length <= len(self.buf):
				packet = self.buf[:packet_length]
				self.buf = self.buf[packet_length:]
			else:
				general.log_error("packet decode error:", self.buf.encode("hex"))
				#self.stop()
				return
			#general.log(general.decode(packet).encode("hex"))
			self.handle_data(general.decode(packet, self.rijndael_key))
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
		StandardClient.__init__(self, *args)
		LoginDataHandler.__init__(self)
class MapClient(StandardClient, MapDataHandler):
	def __init__(self, *args):
		general.log("new map client", args)
		StandardClient.__init__(self, *args)
		MapDataHandler.__init__(self)

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