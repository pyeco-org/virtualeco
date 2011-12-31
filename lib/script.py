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
				script_id = namespace["ID"]
				if hasattr(script_id,"__iter__"):
					for i in script_id:
						script_list[i] = namespace
				else:
					script_list[script_id] = namespace
			except:
				print "script.load", path, traceback.format_exc()
	print "		%d	script	load."%len(script_list)

def run_script(pc, event_id):
	#print "run script id", event_id
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
			say(pc, "Script id %s not exist."%event_id, "")
			raise ValueError("Script id not exist")
	except:
		print "run_script", event_id, traceback.format_exc()
	with pc.lock and pc.user.lock:
		pc.event_id = 0
		pc.user.map_client.send("05dd") #イベント終了の通知

def run(pc, event_id):
	if pc.event_id:
		print "script.run error: event duplicate", pc, pc.event_id
		return
	thread.start_new_thread(run_script, (pc, event_id))

NAME_WITH_TYPE = {
	"run": (int,), #event_id
	"reloadscript": (),
	"say": (str, str, int, int), #message, npc_name, npc_motion_id, npc_id
	"msg": (str,), #message
	"servermsg": (str,), #message
	"where": (),
	"warp": (int, int, int), #map_id, x, y
	"warpraw": (int, int), #rawx, rawy
	}
def handle_cmd(pc, cmd):
	if not (cmd.startswith("/") or cmd.startswith("~")):
		return
	l = filter(None, cmd[1:].split(" "))
	if not l:
		return
	name, args = l[0], l[1:]
	if name not in NAME_WITH_TYPE:
		return
	try:
		types = NAME_WITH_TYPE[name]
		try:
			for i, arg in enumerate(args):
				if not types[i]: continue
				args[i] = types[i](arg)
		except IndexError:
			pass
		eval(name)(pc, *args)
	except:
		msg(pc, filter(None, traceback.format_exc().split("\n"))[-1])
		print "script.handle_cmd [%s] error:\n"%cmd, traceback.format_exc()
	return True

def reloadscript(pc):
	servermsg(pc, "reloadscript...")
	load()
	servermsg(pc, "reloadscript success")

def say(pc, message, npc_name=None, npc_motion_id=131, npc_id=None):
	if npc_id == None:
		npc_id = pc.event_id
	if npc_name == None:
		npc = db.npc.get(pc.event_id)
		if npc: npc_name = npc.name
		else: npc_name = ""
	with pc.lock and pc.user.lock:
		pc.user.map_client.send("03f8") #NPCメッセージのヘッダー
		message = message.replace("$r", "$R").replace("$p", "$P")
		for message_line in message.split("$R"):
			pc.user.map_client.send("03f7", 
				message_line+"$R", npc_name, npc_motion_id, npc_id) #NPCメッセージ
		pc.user.map_client.send("03f9") #NPCメッセージのフッター

def msg(pc, message):
	with pc.lock and pc.user.lock:
		for line in message.replace("\r\n", "\n").split("\n"):
			pc.user.map_client.send("03e9", -1, line)

def servermsg(pc, message):
	for p in users.get_pc_list():
		with p.lock and p.user.lock:
			if not p.online:
				continue
			for line in message.replace("\r\n", "\n").split("\n"):
				p.user.map_client.send("03e9", 0, line)

def where(pc):
	with pc.lock:
		msg(pc, "[%s] map_id: %d x: %d y: %d rawx: %d rawy: %d"%(
			pc.map_obj.name, pc.map_obj.map_id, pc.x, pc.y, pc.rawx, pc.rawy))

def warp(pc, map_id, x=None, y=None):
	if x != None and y != None:
		if x > 255 or x < 0: raise ValueError("x > 255 or < 0 [%d]"%x)
		if y > 255 or y < 0: raise ValueError("y > 255 or < 0 [%d]"%y)
	with pc.lock and pc.user.lock:
		if map_id != pc.map_obj.map_id:
			if not pc.set_map(map_id):
				raise ValueError("map_id %d not found."%map_id)
			if x != None and y != None: pc.set_coord(x, y)
			else: pc.set_coord(pc.map_obj.centerx, pc.map_obj.centery)
			#pc.unset_pet()
			pc.set_dir(0)
			pc.user.map_client.send_map_without_self("1211", pc) #PC消去
			pc.user.map_client.send("11fd", pc) #マップ変更通知
			pc.user.map_client.send("122a") #モンスターID通知
		else:
			if x != None and y != None: pc.set_coord(x, y)
			else: pc.set_coord(pc.map_obj.centerx, pc.map_obj.centery)
			pc.user.map_client.send("11f9", pc, 14) #キャラ移動アナウンス #ワープ

def warpraw(pc, rawx, rawy):
	if rawx > 32767 or rawx < -32768:
		raise ValueError("rawx > 32767 or < -32768 [%d]"%rawx)
	if rawy > 32767 or rawy < -32768:
		raise ValueError("rawy > 32767 or < -32768 [%d]"%rawy)
	with pc.lock and pc.user.lock:
		pc.set_raw_coord(rawx, rawy)
		pc.user.map_client.send("11f9", pc, 14) #キャラ移動アナウンス #ワープ
