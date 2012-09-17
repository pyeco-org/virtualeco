#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script

ID = 18000007
SCRIPT_PATH = "./script/say.py"

def main(pc):
	script.wait(pc, 1000)
	pc.var["test"] = ["☆★☆★☆", []]
	script.say(pc, SCRIPT_PATH)