#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import thread
import traceback
try:
	#equal python -u
	sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)
	sys.stderr = os.fdopen(sys.stderr.fileno(), "wb", 0)
	sys.dont_write_bytecode = True #require python >= 2.6
	#thread.stack_size(256*1024)
except:
	pass
print "-----------------------------------------"
print " virtualeco	2012-01-02"
print "-----------------------------------------"
from lib import db
from lib import server
from lib import users
from lib import pets
from lib import script
from lib import web
from lib import general
STARTUP_TIME = time.time()
USE_LOG = False
STDOUT = sys.stdout
STDERR = sys.stderr
STDOUT_LOG = "./stdout.log"
STDERR_LOG = "./stderr.log"

def save_user_data():
		try:
			for pc in users.get_pc_list():
				if pc.online:
					pc.save()
		except:
			general.log_error("save_user_data", traceback.format_exc())
def save_user_data_every_min():
	while True:
		save_user_data()
		time.sleep(60)
def debugger():
	general.log("[debug] startup expend %s sec"%(time.time()-STARTUP_TIME))
	general.log("[debug] you can input something and press return")
	while True:
		try:
			input_debug = raw_input()
			general.log(eval(input_debug))
		except SyntaxError:
			try:
				exec input_debug
			except:
				general.log_error("debugger", traceback.format_exc())
		except KeyboardInterrupt:
			break
		except SystemExit:
			break
	save_user_data()

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	
	if USE_LOG:
		sys.stdout = general.Log(STDOUT, STDOUT_LOG)
		sys.stderr = general.Log(STDERR, STDERR_LOG)
	db.load()
	script.load()
	users.load()
	server.load()
	web.load()
	
	thread.start_new_thread(save_user_data_every_min, ())
	debugger()