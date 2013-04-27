#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
#static
NAME = "virtualeco"
LAST_UPDATE = "2013-04-26"
DATABASE_FORMAT_VERSION = "1.1.3"
USERDATA_FORMAT_VERSION = "1.1.0"

#runtime
STARTUP_TIME = time.time()
LOAD_STARTUP_TIME = 0
SYSTEM = os.name
RUNTIME_VERSION = sys.version_info
RUNTIME_VERSION_ALL = sys.version
STDOUT = sys.stdout
STDERR = sys.stderr
SYSTEM_ENCODING = sys.getfilesystemencoding()

#config
USE_LOGFILE = False
USE_DEBUGER = True
BACKUP_USER_DATA_EVERY_DAY = False
MAX_CONNECTION_FROM_ONE_IP = 3
DUMP_WITH_ZLIB = False
ZIP_COMPRESS = False

#server config
LOGIN_SERVER_PORT = 13000
MAP_SERVER_PORT = 13001
WEB_SERVER_PORT = 13100
SERVER_BIND_ADDR = "0.0.0.0"
SERVER_BROADCAST_ADDR = "localhost"
DEFAULT_GMLEVEL = 255
LOGIN_EVENT_ID = 30
SEND_LOGIN_EVENT = True
MAX_ITEM_STOCK = 100
MAX_WAREHOURSE_STOCK = 500
SHUTDOWN_CONFIRM_WORD = "-y"
GMLEVEL_MAP = {
	"run": 100,
	"help": 0,
	"reloadscript": 255,
	"reloadsinglescript": 255,
	"shutdown_server": 255,
	"user": 0,
	"say": 0,
	"msg": 0,
	"warning": 0,
	"servermsg": 150,
	"where": 0,
	"warp": 100,
	"warpraw": 100,
	"update": 0,
	"hair": 50,
	"haircolor": 50,
	"face": 50,
	"wig": 50,
	"ex": 50,
	"wing": 50,
	"wingcolor": 50,
	"motion": 0,
	"motion_loop": 0,
	"item": 150,
	"printitem": 0,
	"takeitem": 150,
	"dustbox": 0,
	"warehouse": 100,
	"playbgm": 0,
	"playse": 0,
	"playjin": 0,
	"effect": 0,
	"speed": 100,
	"setgold": 150,
	"takegold": 150,
	"gold": 150,
	"npcmotion": 100,
	"npcmotion_loop": 100,
	"npcshop": 100,
	"npcsell": 100,
	"spawn": 150,
	"killall": 150,
	"emotion": 0,
	"emotion_ex": 0,
	"shownpc": 0,
	"hidenpc": 0,
	"blackout": 0,
	"whiteout": 0,
	"size": 0,
	"petstandby_on": 0,
	"petstandby_off": 0,
	"petmotion": 0,
	"petmotion_loop": 0,
	"unsetallequip": 0,
	"printallequip": 0,
	"printallskill": 0,
	"skill_add": 50,
	"skill_del": 50,
	"skill_clear": 50,
}

#path config
DEFAULT_BASE = "."
LOG_DIR = "./log"
STDOUT_LOG = "./log/%s.log"
STDERR_LOG = "./log/%s_error.log"
SERVER_CONFIG_PATH = "./server.ini"
DATABASE_DIR = "./data"
SCRIPT_DIR = "./script"
USER_DIR = "./user"
USER_BAK_DIR = "./user_bak"
USER_CONFIG_NAME = "user.ini"
PC_CONIG_NAME = "%d.ini"
WEB_DIR = "./web"
REG_USER_PAGE_PATH = "/index.html"
DEL_USER_PAGE_PATH = "/delete.html"
MODIFY_PASSWORD_PAGE_PATH = "/modify_password.html"