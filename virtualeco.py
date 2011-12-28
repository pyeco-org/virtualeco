#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import thread
import threading
try:
	# equal python -u
	sys.stdout = os.fdopen(sys.stdout.fileno(), "w", 0)
	sys.stderr = os.fdopen(sys.stderr.fileno(), "w", 0)
	# require python >= 2.6
	sys.dont_write_bytecode = True
except:
	pass
print "-----------------------------------------"
print "|\tvirtualeco\t2011-12-28\t|"
print "-----------------------------------------"
import lib

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

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	
	if USE_LOG:
		sys.stdout = lib.general.Log(STDOUT, STDOUT_LOG)
		sys.stderr = lib.general.Log(STDERR, STDERR_LOG)
	
	lib.db.load(DATA_PATH)
	lib.server.load(SERVER_CONFIG)
	lib.user.load(USER_DIR)
	
	while True:
		for player in lib.user.player_list:
			if player.login_client:
				player.save()
		time.sleep(60)
