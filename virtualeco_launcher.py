#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pyinstaller.py --onefile --noupx --console virtualeco_launcher.py
import sys
import os
import time
import traceback
import csv
import struct
import marshal
import zipfile
import thread
import hashlib
import random
import copy
import threading
import socket
import math
import imp
import contextlib
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import ConfigParser
import __builtin__
try: import cStringIO
except: import StringIO

if __name__ == "__main__":
	basedir = os.path.dirname(os.path.abspath(sys.argv[0])) 
	os.chdir(basedir)
	sys.path.append(basedir)
	exec open("virtualeco.py", "rb").read().replace("\r\n", "\n")+"\n"