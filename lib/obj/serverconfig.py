#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from lib import general

class ServerConfig:
	def __init__(self, path):
		self.path = path
		self.lock = threading.RLock()
		self.gmlevel = {}
		self.load()
	def load(self):
		with self.lock:
			self._load()
	def _load(self):
		cfg = general.get_config(self.path)
		self.loginserverport = cfg.getint("main", "loginserverport")
		self.mapserverport = cfg.getint("main", "mapserverport")
		self.webserverport = cfg.getint("main", "webserverport")
		self.serveraddress = cfg.get("main", "serveraddress")
		self.defaultgmlevel = cfg.getint("player", "defaultgmlevel")
		self.loginevent = cfg.getint("player", "loginevent")
		for cmd in cfg.options("gmlevel"):
			self.gmlevel[cmd] = cfg.getint("gmlevel", cmd)
	def save(self):
		with self.lock:
			self._save()
	def _save(self):
		cfg = general.get_config()
		cfg.add_section("main")
		cfg.add_section("player")
		cfg.add_section("gmlevel")
		cfg.set("main","loginserverport", str(self.loginserverport))
		cfg.set("main","mapserverport", str(self.mapserverport))
		cfg.set("main","webserverport", str(self.webserverport))
		cfg.set("main","serveraddress", str(self.serveraddress))
		cfg.set("player","defaultgmlevel", str(self.defaultgmlevel))
		cfg.set("player","loginevent", str(self.loginevent))
		for cmd, gmlevel in self.gmlevel.iteritems():
			cfg.set("gmlevel", str(cmd), str(gmlevel))
		cfg.write(open(self.path, "wb"))