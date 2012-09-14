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
from lib import script
from lib import web
from lib import general

def debugger():
	general.log("[debug] load time %s"%(time.time()-env.LOAD_STARTUP_TIME))
	general.log("[debug] interpreter start")
	while True:
		try:
			input_debug = raw_input()
			general.log(eval(input_debug))
		except SyntaxError:
			try:
				exec input_debug
			except:
				general.log_error("[debug]", traceback.format_exc())
		except KeyboardInterrupt:
			break
		except SystemExit:
			break
		except EOFError:
			break
		except:
			general.log_error("[debug]", traceback.format_exc())

def atexit():
	if env.BACKUP_USER_DATA_EVERY_DAY:
		users.backup_user_data()
	users.save_user_data()

def init():
	general.secure_chdir()
	general.log("-"*30+"\n", env.NAME, env.LAST_UPDATE, "\n"+"-"*30)
	if env.USE_LOGFILE:
		general.use_log()
	server.init()

def load():
	env.LOAD_STARTUP_TIME = time.time()
	db.load()
	script.load()
	users.load()
	server.load()
	web.load()
	if env.BACKUP_USER_DATA_EVERY_DAY:
		users.backup_user_data_every_day()
	users.save_user_data_every_min()

def block():
	if env.USE_DEBUGER:
		debugger()
		return
	while True:
		time.sleep(1)

if __name__ == "__main__":
	init()
	load()
	block()
	atexit()
