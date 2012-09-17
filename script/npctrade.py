#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script
from lib import general
ID = 12000170 #携帯ゴミ箱

def main(pc):
	for item in script.npctrade(pc):
		general.log("[npctrade]", item)
