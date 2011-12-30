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
print "|\tvirtualeco\t2011-12-30\t|"
print "-----------------------------------------"
from lib import db
from lib import server
from lib import users

USE_LOG = False
STDOUT = sys.stdout
STDERR = sys.stderr
STDOUT_LOG = "./stdout.log"
STDERR_LOG = "./stderr.log"
SERVER_CONFIG = "./server.ini"
USER_DIR = "./user"
DATA_PATH = {	"item": "./data/item.csv",
			"map": "./data/map.csv",
			"monster": "./data/monster.csv",
			"npc": "./data/npc.csv",
			"pet": "./data/pet.csv",
			"shop": "./data/shop.csv",
			"skill": "./data/skill.csv",
			}

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
			string = raw_input()
			if (not string.startswith("print ") and
				not string.startswith("for ") and
				not string.startswith("while ") and
				not string.startswith("if ") and
				not string.startswith("elif ") and 
				not string.startswith("else ") and
				not string.startswith("import ")):
				string = "print %s"%string
			exec string
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
	db.load(DATA_PATH)
	server.load(SERVER_CONFIG)
	users.load(USER_DIR)

	thread.start_new_thread(save_user_data_every_min, ())
	debugger()
