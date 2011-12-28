#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import hashlib
from lib import general
from lib.packet import packet
from lib import user
WORD_FRONT = "0000"
WORD_BACK = "0000"

class LoginDataHandle:
	def __init__(self):
		self.player = None
	
	def send_data(self, *args):
		self.send(packet.make(*args))
	
	def handle_data(self, data):
		#000a 0001 000003f91e07e221
		data = data[:general.unpack_short(data[:2])]
		data_type = data[2:4].encode("hex")
		try:
			handler = getattr(self, "do_%s"%data_type)
		except AttributeError:
			print "[login] unknow packet type", data_type, data.encode("hex")
			return
		try:
			handler(data[4:])
		except:
			print "[login] handle_data error:", data.encode("hex")
			print traceback.format_exc()
	
	def do_0001(self, data):
		print "[login] eco version", data[2:].encode("hex")
		self.send_data("0002", data)
		self.send_data("001e", WORD_FRONT+WORD_BACK)
	
	def do_001f(self, data):
		print "[login]", "login",
		username, username_length = general.unpack_str(data)
		password_sha1 = general.unpack_str(data[username_length:])[0]
		print username, password_sha1
		for player in user.player_list:
			with player.lock:
				if not player.username == username:
					continue
				player_password_sha1 = hashlib.sha1(
					"".join((str(general.unpack_int(WORD_FRONT)),
							player.password,
							str(general.unpack_int(WORD_BACK)),
							))).hexdigest()
				if player_password_sha1 != password_sha1:
					self.send("0020", "loginfaild")
					return
				if player.login_client:
					player.reset_login()
					self.send_data("0020", "isonline")
					return
				player.reset_login()
				player.login_client = self
				self.send_data("0020", "loginsucess")
				#4キャラクターの基本属性
				self.send_data("0028", player)
				#4キャラクターの装備
				self.send_data("0029", player)
				break
		else:
			self.send_data("0020", "loginfaild")
	
	def do_000a(self, data):
		#接続確認
		self.send_data("000b", data)
