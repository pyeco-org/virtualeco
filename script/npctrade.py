#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
ID = 12000170 #携帯ゴミ箱

def main(pc):
	for item in script.npctrade(pc):
		print "[npctrade] %s"%item
