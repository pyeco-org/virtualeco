#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

def load(path_dir):
	from lib.obj.player import Player
	global player_list
	player_list = []
	for name in os.listdir(path_dir):
		try:
			player_list.append(Player(os.path.join(path_dir, name), name))
		except:
			print "load error:", name
			raise