#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import thread
import threading
import traceback
from lib import db
from lib import users
from lib import general
SCRIPT_DIR = "./script"
script_list = {}
script_list_lock = threading.RLock()

def load():
	with script_list_lock:
		_load()
def _load():
	print "Load", SCRIPT_DIR, "...",
	script_list.clear()
	for root, dirs, files in os.walk(SCRIPT_DIR):
		for name in files:
			path = os.path.join(root, name)
			if not path.endswith(".py"):
				continue
			#print "load script", path
			obj = general.load_dump(path)
			try:
				if not obj:
					obj = compile(open(path, "rb").read(), path, "exec")
					general.save_dump(path, obj)
				namespace = {}
				exec obj in namespace
				script_list[namespace["ID"]] = namespace
			except:
				print "script.load", path, traceback.format_exc()
	print "		%d	script	load."%len(script_list)

def run_script(pc, event_id):
	#print "run script id", hex(event_id)
	with pc.lock and pc.user.lock:
		pc.event_id = event_id
		pc.user.map_client.send("05dc") #イベント開始の通知
		pc.user.map_client.send("05e8", event_id) #EventID通知 Event送信に対する応答
	with script_list_lock:
		event = script_list.get(event_id)
	try:
		if event:
			event["main"](pc)
		else:
			say(pc, "Script id %s not exist."%hex(event_id), "")
			raise ValueError("Script id not exist")
	except:
		print "run_script", hex(event_id), traceback.format_exc()
	with pc.lock and pc.user.lock:
		pc.event_id = 0
		pc.user.map_client.send("05dd") #イベント終了の通知

def run(*args):
	thread.start_new_thread(run_script, args)

def say(pc, message, npc_name=None, npc_motion_id=131, npc_id=None):
	if npc_id == None:
		npc_id = pc.event_id
	if npc_name == None:
		npc = db.npc.get(pc.event_id)
		if npc: npc_name = npc.name
		else: npc_name = ""
	pc.user.map_client.send("03f8") #NPCメッセージのヘッダー
	message = message.replace("$r", "$R").replace("$p", "$P")
	for message_line in message.split("$R"):
		pc.user.map_client.send("03f7", 
			message_line+"$R", npc_name, npc_motion_id, npc_id) #NPCメッセージ
	pc.user.map_client.send("03f9") #NPCメッセージのフッター
