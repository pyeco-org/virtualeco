#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import traceback
import socket
import urllib
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT_LOGIN = 13000
#SERVER_PORT_MAP = 13001
SERVER_PORT_WEB = 13100
USER_NAME = "unittestuser"
USER_PASSWORD_REG = "password_reg"
USER_DELPASSWORD_REG = "delpassword_reg"
USER_PASSWORD = "password"
USER_DELPASSWORD = "delpassword"
PATH_REG_PAGE = "index.html"
PATH_DEL_PAGE = "delete.html"
PATH_MODIFYPASSWORD_PAGE = "modify_password.html"
PACKET_INIT = "\x00\x00\x00\x00\x00\x00\x00\x10"

def exit():
	sys.exit()

def failed(error):
	general.log_error("[failed][%s]"%error)
	exit()

def success():
	general.log("[success]")

class Main():
	def __init__(self):
		self.buf = ""
	
	def send_login(self, *args):
		self.socket_login.sendall(
			general.encode(packet.make(*args), self.rijndael_key))
	
	def make_user(self):
		general.log_line("make_user ...")
		result = urllib.urlopen("http://%s:%s/%s"%(
			SERVER_ADDRESS, SERVER_PORT_WEB, PATH_REG_PAGE),
			urllib.urlencode({
				"user_name": USER_NAME,
				"password": USER_PASSWORD_REG,
				"password_confirm": USER_PASSWORD_REG,
				"delete_password": USER_DELPASSWORD_REG,
				"delete_password_confirm": USER_DELPASSWORD_REG,
				})).read()
		if result != "reg success":
			raise ValueError(result)
	
	def modify_password(self):
		general.log_line("modify_password ...")
		result = urllib.urlopen("http://%s:%s/%s"%(
			SERVER_ADDRESS, SERVER_PORT_WEB, PATH_MODIFYPASSWORD_PAGE),
			urllib.urlencode({
				"user_name": USER_NAME,
				"old_password": USER_PASSWORD_REG,
				"old_delete_password": USER_DELPASSWORD_REG,
				"password": USER_PASSWORD,
				"password_confirm": USER_PASSWORD,
				"delete_password": USER_DELPASSWORD,
				"delete_password_confirm": USER_DELPASSWORD,
				})).read()
		if result != "modify password success":
			raise ValueError(result)
	
	def login(self):
		general.log("login ...")
		self.socket_login = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket_login.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		self.socket_login.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.socket_login.connect((SERVER_ADDRESS, SERVER_PORT_LOGIN))
		self.socket_login.send(PACKET_INIT)
		head = general.unpack_int(self.socket_login.recv(4))
		if head != 0:
			raise ValueError("head != 0")
		generator_length = general.unpack_int(self.socket_login.recv(4))
		generator = self.socket_login.recv(generator_length)
		prime_length = general.unpack_int(self.socket_login.recv(4))
		prime = self.socket_login.recv(prime_length)
		server_key_length = general.unpack_int(self.socket_login.recv(4))
		server_key = self.socket_login.recv(server_key_length)
		#general.log("generator", generator)
		#general.log("prime", prime)
		#general.log("server_key", server_key)
		private_key = general.get_private_key()
		public_key = general.get_public_key(
			general.bytes_to_int(generator),
			private_key,
			general.bytes_to_int(prime))
		share_key = general.get_share_key_bytes(
			general.bytes_to_int(server_key),
			private_key,
			general.bytes_to_int(prime)
			)
		public_key_bytes = general.int_to_bytes(public_key)
		self.socket_login.send(general.pack_int(len(public_key_bytes)))
		self.socket_login.send(public_key_bytes)
		self.rijndael_key = general.get_rijndael_key(share_key)
		general.log("share_key", share_key)
		general.log("rijndael_key", self.rijndael_key.encode("hex"))
		self.send_login("0001", 1100) #version info
	
	def logout(self):
		general.log_line("logout ...")
		self.socket_login.close()
	
	def delete_user(self):
		general.log_line("delete_user ...")
		result = urllib.urlopen("http://%s:%s/%s"%(
			SERVER_ADDRESS, SERVER_PORT_WEB, PATH_DEL_PAGE),
			urllib.urlencode({
				"user_name": USER_NAME,
				"password": USER_PASSWORD,
				"delete_password": USER_DELPASSWORD,
				})).read()
		if result != "del success":
			raise ValueError(result)
	
	def start(self):
		general.log("virtualeco unit test start ...")
		for unit in (
			self.make_user,
			self.modify_password,
			self.login,
			self.logout,
			self.delete_user,
			):
			try:
				unit()
			except:
				try: self.delete_user()
				except: pass
				failed(traceback.format_exc())
			else:
				success()
		general.log("all success.")

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	import general
	import packet
	main = Main()
	main.start()