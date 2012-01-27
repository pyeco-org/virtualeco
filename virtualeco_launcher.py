#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

#build with pyinstaller
#Makespec.py -FX virtualeco_launcher.py
#Build.py ./virtualeco_launcher/virtualeco_launcher.spec