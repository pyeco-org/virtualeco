#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import script

ID = 0x112a887
SCRIPT_PATH = "./script/say.py"

def main(player):
	script.say(player, SCRIPT_PATH)
