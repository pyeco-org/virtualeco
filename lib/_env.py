#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
#static
NAME = "virtualeco"
LAST_UPDATE = "2012-09-26"
DATABASE_FORMAT_VERSION = "1.1.0"
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
ZIP_MODE = "ZIP_STORED" #ZIP_DEFLATED, ZIP_STORED

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