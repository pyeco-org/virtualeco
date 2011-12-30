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
print " virtualeco	2011-12-31"
print "-----------------------------------------"
from lib import db
from lib import server
from lib import users
from lib import script

USE_LOG = False
STDOUT = sys.stdout
STDERR = sys.stderr
STDOUT_LOG = "./stdout.log"
STDERR_LOG = "./stderr.log"

def save_user_data():
		try:
			for player in users.get_player_list():
				if player.online:
					player.save()
		except:
			print "save_user_data", traceback.format_exc()
def save_user_data_every_min():
	while True:
		save_user_data()
		time.sleep(60)
def debugger():
	print "debugger: you can input something and press return"
	while True:
		try:
			exec raw_input()
		except KeyboardInterrupt:
			break
		except SystemExit:
			break
		except:
			print "debugger", traceback.format_exc()
	save_user_data()

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	if USE_LOG:
		sys.stdout = lib.general.Log(STDOUT, STDOUT_LOG)
		sys.stderr = lib.general.Log(STDERR, STDERR_LOG)
	db.load()
	script.load()
	server.load()
	users.load()
	
	thread.start_new_thread(save_user_data_every_min, ())
	debugger()