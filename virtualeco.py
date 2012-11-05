#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import threading
#reduce memory usage
threading.stack_size(256*1024)
from lib import env
from lib import db
from lib import server
from lib import users
from lib import pets
from lib import monsters
from lib import usermaps
from lib import script
from lib import web
from lib import general

def debugger():
	general.log("[debug] load time %s"%(time.time()-env.LOAD_STARTUP_TIME))
	general.log("[debug] interpreter start")
	while True:
		try:
			input_debug = raw_input()
			if input_debug in ("exit", "halt", "quit", "q"):
				raise SystemExit()
		except (SystemExit, EOFError, IOError, KeyboardInterrupt):
			if raw_input("Are you sure to exit? [y/N]: ").strip().lower() == "y":
				return
			continue
		except:
			general.log_error("[debug]", traceback.format_exc())
		try:
			try:
				general.log(eval(input_debug))
			except SyntaxError:
				exec input_debug
		except:
			general.log_error("[debug]", traceback.format_exc())

def atexit():
	server.mapserver._shutdown()
	server.loginserver._shutdown()
	if env.BACKUP_USER_DATA_EVERY_DAY:
		users.backup_user_data()
	users.save_user_data_atexit()
	os._exit(0)

def init():
	general.init()
	general.log("-"*30+"\n", env.NAME, env.LAST_UPDATE, "\n"+"-"*30)
	server.init()
	pets.init()
	monsters.init()
	usermaps.init()

def load():
	env.LOAD_STARTUP_TIME = time.time()
	db.load()
	script.load()
	users.load()
	server.load()
	web.load()

def block():
	if env.USE_DEBUGER:
		debugger()
		return
	try:
		while time.sleep(1) or 1: pass
	except:
		return

if __name__ == "__main__":
	init()
	load()
	block()
	atexit()