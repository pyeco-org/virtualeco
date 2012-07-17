#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback
#try:
	#equal python -u
	#sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)
	#sys.stderr = os.fdopen(sys.stderr.fileno(), "wb", 0)
	#sys.dont_write_bytecode = True #require python >= 2.6
	#thread.stack_size(256*1024)
#except:
#	print traceback.format_exc()
print "-----------------------------------------"
print " virtualeco	2012-07-17"
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
BACKUP_USER_DATA_EVERY_DAY = False

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
				general.log_error("[debug]", traceback.format_exc())
		except KeyboardInterrupt:
			break
		except SystemExit:
			break
		except EOFError:
			break
		except:
			general.log_error("[debug]", traceback.format_exc())
	if BACKUP_USER_DATA_EVERY_DAY:
		users.backup_user_data()
	users.save_user_data()

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	if USE_LOG:
		general.use_log()
	
	db.load()
	script.load()
	users.load()
	server.load()
	web.load()
	
	if BACKUP_USER_DATA_EVERY_DAY:
		users.backup_user_data_every_day()
	users.save_user_data_every_min()
	debugger()