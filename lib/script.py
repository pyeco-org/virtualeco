#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import thread
import threading
import traceback
from lib import env
from lib import db
from lib import users
from lib import general
server = None
monsters = None
script_list = {}
script_list_lock = threading.RLock()

def load():
	global server, monsters
	if not server or not monsters: #skip search sys.modules
		from lib import server
		from lib import monsters
	with script_list_lock:
		general.log_line("[load ] load %-20s"%("%s ..."%env.SCRIPT_DIR))
		script_list.clear()
		for root, dirs, files in os.walk(env.SCRIPT_DIR):
			for name in files:
				path = os.path.join(root, name)
				if not path.endswith(".py"):
					continue
				#general.log("load script", path)
				try:
					load_single(path)
				except:
					general.log_error("script.load", path, traceback.format_exc())
		general.log("	%d	script	load."%len(script_list))

def load_single(path):
	with script_list_lock:
		obj = general.load_dump(path, env.SCRIPT_DIR)
		if not obj:
			obj = compile(
				open(
					path, "rb", base=env.SCRIPT_DIR
				).read().replace("\r\n", "\n")+"\n",
				path,
				"exec",
			)
			general.save_dump(path, obj, env.SCRIPT_DIR)
		namespace = {}
		exec obj in namespace
		script_id = namespace["ID"]
		if hasattr(script_id, "__iter__"):
			for i in script_id:
				script_list[i] = namespace
		else:
			script_list[script_id] = namespace

def run_script(pc, event_id):
	#general.log("run script id", event_id)
	with pc.lock and pc.user.lock:
		pc.event_id = event_id
		pc.map_send("05dc") #イベント開始の通知
		pc.map_send("05e8", event_id) #EventID通知 Event送信に対する応答
	with script_list_lock:
		event = script_list.get(event_id)
	try:
		if event:
			event["main"](pc)
		else:
			say(pc, "Script id %s not exist."%event_id, "")
			raise ValueError("Script id not exist")
	except:
		general.log_error("run_script", event_id, traceback.format_exc())
	with pc.lock and pc.user.lock:
		pc.event_id = 0
		if pc.online:
			pc.map_send("05dd") #イベント終了の通知

def run(pc, event_id):
	#if pc.event_id:
	#	general.log_error("script.run error: event duplicate", pc, pc.event_id)
	#	return
	thread.start_new_thread(run_script, (pc, event_id))

def send_map(map_id, *args):
	map_obj = general.get_map(map_id)
	if not map_obj:
		error = "send_map: map_id %s not exist."%map_id
		general.log_error(error)
		return error
	send_map_obj(map_id, *args)

def send_map_obj(map_obj, without_list, *args):
	#don't lock pc and pc.user, easy to cause deadlock
	with map_obj.lock:
		for p in map_obj.pc_list:
			try:
				if not p.online:
					continue
				if p in without_list:
					continue
				p.map_send(*args)
			except:
				general.log_error("send_map error: %s"%traceback.format_exc())

def send_server(*args):
	with users.user_list_lock:
		for p in users.get_pc_list():
			try:
				if not p.online:
					continue
				p.map_send(*args)
			except:
				general.log_error("send_server error: %s"%traceback.format_exc())

NAME_WITH_TYPE = {
	"run": (int,), #event_id
	"help": (),
	"reloadscript": (),
	"reloadsinglescript": (str,),
	"user": (),
	"say": (str, str, int, int), #message, npc_name, npc_motion_id, npc_id
	"msg": (str,), #message
	"servermsg": (str,), #message
	"where": (),
	"warp": (int, float, float), #map_id, x, y
	"warpraw": (int, int), #rawx, rawy
	"update": (),
	"hair": (int,), #hair_id
	"haircolor": (int,), #haircolor_id
	"face": (int,), #face_id
	"wig": (int,), #wig_id
	"ex": (int,), #ex_id
	"wing": (int,), #wing_id
	"wingcolor": (int,), #wingcolor_id
	"motion": (int, int), #motion_id, motion_loop
	"motion_loop": (int,), #motion_id
	"item": (int, int), #item_id, item_count
	"printitem": (),
	"takeitem": (int, int), #item_id, item_count
	"dustbox": (),
	"warehouse": (int,), #warehouse_id
	"playbgm": (int, int, int), #sound_id, loop, volume
	"playse": (int, int, int, int), #sound_id, loop, volume, balance
	"playjin": (int, int, int, int), #sound_id, loop, volume, balance
	"effect": (int, int, int, int, int), #effect_id, id, x, y, dir
	"speed": (int,), #speed
	"setgold": (int,), #gold
	"takegold": (int,), #gold_take
	"gold": (int,), #gold_give
	"npcmotion": (int, int, int), #npc_id, motion_id, motion_loop
	"npcmotion_loop": (int, int), #npc_id, motion_id
	"npcshop": (int,), #shop_id
	"npcsell": (),
	"spawn": (int,), #monster_id
	"killall": (),
	"emotion": (int,),
	"emotion_ex": (int,),
	"shownpc": (int,),
	"hidenpc": (int,),
	"blackout": (int,),
	"whiteout": (int,),
	"size": (int,),
	"petstandby_on": (),
	"petstandby_off": (),
	"petmotion": (int, int), #motion_id, motion_loop
	"petmotion_loop": (int,), #motion_id
	"unsetallequip": (),
	"printallequip": (),
}

def help(pc):
	msg(pc, """
/run event_id
/help
/reloadscript
/reloadsinglescript path
/user
/say message npc_name npc_motion_id npc_id
/msg message
/servermsg message
/where (~where)
/warp map_id x y
/warpraw rawx rawy
/update
/hair hair_id
/haircolor haircolor_id
/face face_id
/wig ex_id
/ex ex_id
/wing wing_id
/wingcolor wingcolor_id
/motion motion_id motion_loop
/motion_loop motion_id
/item item_id item_count
/printitem
/takeitem item_id item_count
/dustbox
/warehouse warehouse_id
/playbgm sound_id loop volume
/playse sound_id loop volume balance
/playjin sound_id loop volume balance
/effect effect_id id x y dir
/speed speed
/setgold gold
/takegold gold_take
/gold gold_give
/npcmotion npc_id motion_id motion_loop
/npcmotion_loop npc_id motion_id
/npcshop shop_id
/npcsell
/spawn monster_id
/killall
/emotion emotion_id
/emotion_ex emotion_ex_id
/shownpc npc_id
/hidenpc npc_id
/blackout time_ms
/whiteout time_ms
/size pc_size
/petstandby_on
/petstandby_off
/petmotion motion_id motion_loop
/petmotion_loop motion_id
/unsetallequip
/printallequip
""")

def handle_cmd(pc, cmd):
	if not (cmd.startswith("/") or cmd.startswith("~")):
		return
	l = filter(None, cmd[1:].split(" "))
	if not l:
		return
	name, args = l[0], l[1:]
	types = NAME_WITH_TYPE.get(name)
	if types is None:
		return
	try:
		request_gmlevel = server.config.gmlevel.get(name)
		if request_gmlevel is None:
			raise Exception("server.config.gmlevel[%s] not exist"%name)
		if pc.gmlevel < request_gmlevel:
			raise Exception("pc.gmlevel < request_gmlevel")
		try:
			for i, arg in enumerate(args):
				if not types[i]: continue
				args[i] = types[i](arg)
		except IndexError:
			pass
		name_map.get(name)(pc, *args)
	except:
		exc_info = traceback.format_exc()
		msg(pc, filter(None, exc_info.split("\n"))[-1])
		general.log_error("script.handle_cmd [%s] error:\n"%cmd, exc_info)
	return True

def reloadscript(pc):
	servermsg(pc, "reloadscript ...")
	load()
	servermsg(pc, "reloadscript success")

def reloadsinglescript(pc, path):
	if path.find("..") != -1:
		raise ValueError("path include ..")
	if not path.endswith(".py"):
		path += ".py"
	servermsg(pc, "reloadsinglescript %s ..."%path)
	try:
		load_single(env.SCRIPT_DIR+"/"+path)
	except:
		servermsg(pc, "reloadsinglescript failed")
		raise
	else:
		servermsg(pc, "reloadsinglescript success")

def user(pc):
	message = ""
	online_count = 0
	for p in users.get_pc_list():
		with p.lock:
			if not p.online:
				continue
			if not p.visible:
				continue
			message += "[%s] %s\n"%(p.map_obj.name, p.name)
			online_count += 1
	message += "online count: %d"%online_count
	msg(pc, message)

def say(pc, message, npc_name=None, npc_motion_id=131, npc_id=None):
	if npc_id is None:
		npc_id = pc.event_id
	general.assert_value_range("npc_id", npc_id, general.RANGE_UNSIGNED_INT)
	if npc_name is None:
		npc = db.npc.get(pc.event_id)
		if npc: npc_name = npc.name
		else: npc_name = ""
	with pc.lock and pc.user.lock:
		pc.map_send("03f8") #NPCメッセージのヘッダー
		message = message.replace("$r", "$R").replace("$p", "$P")
		for message_line in message.split("$R"):
			pc.map_send("03f7", 
				message_line+"$R", npc_name, npc_motion_id, npc_id) #NPCメッセージ
		pc.map_send("03f9") #NPCメッセージのフッター

def msg(pc, message):
	with pc.lock and pc.user.lock:
		for line in message.replace("\r\n", "\n").split("\n"):
			pc.map_send("03e9", -1, line)

def servermsg(pc, message):
	with pc.lock and pc.user.lock:
		for line in message.replace("\r\n", "\n").split("\n"):
			pc.map_send_server("03e9", 0, line)

def where(pc):
	with pc.lock:
		msg(pc, "[%s] map_id: %s x: %s y: %s dir: %s rawx: %s rawy: %d rawdir: %s"%(
			pc.map_obj.name, pc.map_obj.map_id, pc.x, pc.y, pc.dir,
			pc.rawx, pc.rawy, pc.rawdir))

def warp(pc, map_id, x=None, y=None):
	if x != None and y != None:
		general.assert_value_range("x", x, general.RANGE_UNSIGNED_BYTE)
		general.assert_value_range("y", y, general.RANGE_UNSIGNED_BYTE)
	with pc.lock and pc.user.lock:
		if map_id != pc.map_obj.map_id:
			if not pc.set_map(map_id):
				raise ValueError("map_id %d not found."%map_id)
			if x != None and y != None: pc.set_coord(x, y)
			else: pc.set_coord(pc.map_obj.centerx, pc.map_obj.centery)
			pc.set_dir(0)
			pc.map_send("11fd", pc) #マップ変更通知
			pc.map_send("122a") #モンスターID通知
		else:
			if x != None and y != None: pc.set_coord(x, y)
			else: pc.set_coord(pc.map_obj.centerx, pc.map_obj.centery)
			pc.unset_pet()
			pc.map_send_map("11f9", pc, 14) #キャラ移動アナウンス #ワープ
			pc.set_pet()

def warpraw(pc, rawx, rawy):
	general.assert_value_range("rawx", rawx, general.RANGE_SHORT)
	general.assert_value_range("rawy", rawy, general.RANGE_SHORT)
	with pc.lock and pc.user.lock:
		pc.set_raw_coord(rawx, rawy)
		pc.unset_pet()
		pc.map_send_map("11f9", pc, 14) #キャラ移動アナウンス #ワープ
		pc.set_pet()

def update(pc):
	with pc.lock and pc.user.lock:
		pc.map_send_map("020e", pc) #キャラ情報

def hair(pc, hair_id):
	general.assert_value_range("hair_id", hair_id, general.RANGE_SHORT)
	with pc.lock:
		pc.hair = hair_id
	update(pc)

def haircolor(pc, haircolor_id):
	general.assert_value_range("haircolor_id", haircolor_id, general.RANGE_BYTE)
	with pc.lock:
		pc.haircolor = haircolor_id
	update(pc)

def face(pc, face_id):
	general.assert_value_range("face_id", face_id, general.RANGE_SHORT)
	with pc.lock:
		pc.face = face_id
	update(pc)

def wig(pc, wig_id):
	general.assert_value_range("wig_id", wig_id, general.RANGE_SHORT)
	with pc.lock:
		pc.wig = wig_id
	update(pc)

def ex(pc, ex_id):
	general.assert_value_range("ex_id", ex_id, general.RANGE_BYTE)
	with pc.lock:
		pc.ex = ex_id
	update(pc)

def wing(pc, wing_id):
	general.assert_value_range("wing_id", wing_id, general.RANGE_BYTE)
	with pc.lock:
		pc.ex = wing_id
	update(pc)

def wingcolor(pc, wingcolor_id):
	general.assert_value_range("wingcolor_id", wingcolor_id, general.RANGE_BYTE)
	with pc.lock:
		pc.wingcolor = wingcolor_id
	update(pc)

def motion(pc, motion_id, motion_loop=False):
	general.assert_value_range("motion_id", motion_id, general.RANGE_UNSIGNED_SHORT)
	pc.set_motion(motion_id, motion_loop)
	with pc.lock and pc.user.lock:
		pc.map_send_map("121c", pc) #モーション通知

def motion_loop(pc, motion_id):
	motion(pc, motion_id, True)

def item(pc, item_id, item_count=1):
	with pc.lock and pc.user.lock:
		return _item(pc, item_id, item_count)
def _item(pc, item_id, item_count):
	general.assert_value_range("item_count", item_count, general.RANGE_UNSIGNED_SHORT)
	general.assert_value_range("item_id", item_id, general.RANGE_UNSIGNED_INT)
	while item_count:
		item = general.get_item(item_id)
		item_stock_exist = False
		if item.stock:
			for iid in pc.sort.item:
				item_exist = pc.item[iid]
				if item_exist.count >= 999:
					continue
				if item_exist.item_id != item_id:
					continue
				if item_exist.count+item_count > 999:
					item_count_add = 999-item_exist.count
					item_count -= item_count_add
					item_exist.count += item_count_add
				else:
					item_count_add = item_count
					item_count = 0
					item_exist.count += item_count_add
				pc.map_send("09cf", item_exist, iid) #アイテム個数変化
				msg(pc, "%sを%s個入手しました"%(
					item_exist.name, item_count_add
				))
				item_stock_exist = True
				break
		if item_stock_exist:
			continue
		if item_count > 999:
			item.count = 999
			item_count -= 999
		else:
			item.count = item_count
			item_count = 0
		pc.item_append(item)
	pc.update_item_status()

def printitem(pc):
	with pc.lock:
		for iid in pc.sort.item:
			item = pc.item[iid]
			msg(pc, "%s iid: %d item_id: %d count: %d"%(
				item.name, iid, item.item_id, item.count))

def countitem(pc, item_id): #not for command
	general.assert_value_range("item_id", item_id, general.RANGE_UNSIGNED_INT)
	item_count = 0
	with pc.lock and pc.user.lock:
		for iid, item in pc.item.iteritems():
			if pc.in_equip(iid):
				continue
			if item.item_id != item_id:
				continue
			item_count += item.count
	return item_count

def takeitem(pc, item_id, item_count=1):
	with pc.lock and pc.user.lock:
		return _takeitem(pc, item_id, item_count)
def _takeitem(pc, item_id, item_count):
	general.assert_value_range("item_count", item_count, general.RANGE_UNSIGNED_SHORT)
	general.assert_value_range("item_id", item_id, general.RANGE_UNSIGNED_INT)
	if countitem(pc, item_id) < item_count:
		return False
	while item_count:
		for iid in pc.sort.item:
			if pc.in_equip(iid):
				continue
			item_exist = pc.item[iid]
			if item_exist.item_id != item_id:
				continue
			#general.log(item_count, item_exist.count)
			if item_exist.count > item_count:
				item_exist.count -= item_count
				pc.map_send("09cf", item_exist, iid) #アイテム個数変化
				msg(pc, "%sを%s個失いました"%(item.name, item_count))
			else:
				pc.item_pop(iid)
			break
		else:
			return item_count
	pc.update_item_status()
	return True

def takeitem_byiid(pc, item_iid, item_count):
	general.assert_value_range("item_iid", item_iid, general.RANGE_UNSIGNED_INT)
	general.assert_value_range("item_count", item_count, general.RANGE_UNSIGNED_SHORT)
	with pc.lock and pc.user.lock:
		item_exist = pc.item.get(item_iid)
		item_return = None
		error = 0
		if not item_exist:
			error = -2 #存在しないアイテムです
			general.log_error("takeitem byiid: iid not exist", item_iid)
		elif pc.in_equip(item_iid):
			error = -11 #装備中のアイテムは捨てることが出来ません
			general.log_error("takeitem byiid: iid not exist", item_iid)
		elif item_exist.count < item_count:
			error = -22 #ロックアイテムは捨てることが出来ません
			general.log_error("takeitem byiid: item.count < item_count", item_count)
		elif item_exist.count > item_count:
			item_exist.count -= item_count
			item_return = general.copy(item_exist)
			item_return.count = item_count
			pc.map_send("09cf", item_exist, item_iid) #アイテム個数変化
			msg(pc, "%sを%s個失いました"%(item_exist.name, item_count))
		elif item_exist.count == item_count:
			item_return = pc.item_pop(item_iid)
	return item_return, error

def dustbox(pc):
	run(pc, 12000170) #携帯ゴミ箱

def update_item(pc): #not for command
	with pc.lock and pc.user.lock:
		for iid, item in pc.item.iteritems():
			if pc.in_equip(iid):
				continue
			pc.map_send("09cf", item, iid) #アイテム個数変化

def npctrade(pc): #not for command
	pc.reset_trade()
	with pc.lock:
		pc.trade = True
		event_id = pc.event_id
	npc = db.npc.get(event_id)
	if npc: npc_name = npc.name
	else: npc_name = ""
	with pc.lock and pc.user.lock:
		pc.map_send("0a0f", npc_name, True) #トレードウィンドウ表示
	while True:
		with pc.lock:
			if not pc.online:
				return ()
			if not pc.trade:
				break
		time.sleep(0.1)
	#update_item(pc)
	return pc.trade_return_list

def warehouse(pc, warehouse_id):
	general.assert_value_range("warehouse_id", warehouse_id, general.RANGE_BYTE)
	num_max = 300
	num_here = 0
	num_all = 0
	with pc.lock:
		for item in pc.warehouse.itervalues():
			num_all += 1
			if item.warehouse == warehouse_id:
				num_here += 1
	with pc.lock and pc.user.lock:
		#倉庫インベントリーヘッダ
		pc.map_send("09f6", warehouse_id, num_here, num_all, num_max)
		for iid, item in pc.warehouse.iteritems():
			if item.warehouse == warehouse_id:
				part = 30 #倉庫
			else:
				part = item.warehouse
			#倉庫インベントリーデータ
			pc.map_send("09f9", item, iid, part)
		pc.warehouse_open = warehouse_id
		pc.map_send("09fa") #倉庫インベントリーフッタ

def select(pc, option_list, title=""): #not for command
	option_list = filter(None, option_list)
	general.assert_value_range("len(option_list)", len(option_list), (0, 65))
	with pc.lock and pc.user.lock:
		pc.select_result = None
		#NPCのメッセージのうち、選択肢から選ぶもの
		pc.map_send("0604", option_list, title)
	while True:
		with pc.lock:
			if not pc.online:
				return
			if pc.select_result != None:
				return pc.select_result
		time.sleep(0.1)

def wait(pc, time_ms): #not for command
	general.assert_value_range("time_ms", time_ms, general.RANGE_UNSIGNED_INT)
	with pc.lock and pc.user.lock:
		pc.map_send("05eb", time_ms) #イベント関連のウェイト
	time.sleep(time_ms/1000.0)

def playbgm(pc, sound_id, loop=1, volume=100):
	general.assert_value_range("sound_id", sound_id, general.RANGE_UNSIGNED_INT)
	general.assert_value_range("volume", volume, (0, 100))
	with pc.lock and pc.user.lock:
		#音楽を再生する
		pc.map_send("05f0", sound_id, (1 if loop else 0), volume)

def playse(pc, sound_id, loop=0, volume=100, balance=50):
	general.assert_value_range("sound_id", sound_id, general.RANGE_UNSIGNED_INT)
	general.assert_value_range("volume", volume, (0, 100))
	general.assert_value_range("balance", balance, (0, 100))
	with pc.lock and pc.user.lock:
		#効果音を再生する
		pc.map_send("05f5", sound_id, (1 if loop else 0), volume, balance)

def playjin(pc, sound_id, loop=0, volume=100, balance=50):
	general.assert_value_range("sound_id", sound_id, general.RANGE_UNSIGNED_INT)
	general.assert_value_range("volume", volume, (0, 100))
	general.assert_value_range("balance", balance, (0, 100))
	with pc.lock and pc.user.lock:
		#ジングルを再生する
		pc.map_send("05fa", sound_id, (1 if loop else 0), volume, balance)

def effect(pc, effect_id, id=None, x=None, y=None, dir=None):
	general.assert_value_range("effect_id", effect_id, general.RANGE_UNSIGNED_INT)
	general.assert_value_range("id", id, general.RANGE_INT)
	general.assert_value_range("x", x, general.RANGE_UNSIGNED_BYTE)
	general.assert_value_range("y", y, general.RANGE_UNSIGNED_BYTE)
	general.assert_value_range("dir", dir, general.RANGE_BYTE)
	with pc.lock and pc.user.lock:
		#エフェクト受信
		pc.map_send_map("060e", pc, effect_id, id, x, y, dir)

def speed(pc, speed):
	general.assert_value_range("speed", speed, general.RANGE_SHORT)
	with pc.lock and pc.user.lock:
		pc.status.speed = speed
		pc.map_send_map("1239", pc) #キャラ速度通知・変更

def setgold(pc, gold):
	general.assert_value_range("gold", gold, general.RANGE_INT)
	with pc.lock and pc.user.lock:
		if gold < 0 or gold > 100000000:
			msg(pc, "setgold error: gold < 0 or gold > 100000000 [%s]"%gold)
			return False
		else:
			pc.gold = gold
			pc.map_send("09ec", pc) #ゴールドを更新する、値は更新後の値
			return True

def takegold(pc, gold_take):
	#general.log("takegold", gold_take)
	with pc.lock and pc.user.lock:
		return setgold(pc, pc.gold-gold_take)

def gold(pc, gold_give):
	#general.log("gold", gold_give)
	with pc.lock and pc.user.lock:
		return setgold(pc, pc.gold+gold_give)

def npcmotion(pc, npc_id, motion_id, motion_loop=False):
	general.assert_value_range("npc_id", npc_id, general.RANGE_UNSIGNED_INT)
	general.assert_value_range("motion_id", motion_id, general.RANGE_UNSIGNED_SHORT)
	with pc.lock and pc.user.lock:
		#モーション通知
		pc.map_send("121c", pc, npc_id, motion_id, motion_loop) 

def npcmotion_loop(pc, npc_id, motion_id):
	npcmotion(pc, npc_id, motion_id, True)

def npcshop(pc, shop_id):
	shop = db.shop.get(shop_id)
	if not shop:
		general.log_error("npc shop id %s not exist"%shop_id)
		return
	with pc.lock and pc.user.lock:
		pc.shop_open = shop_id
		pc.map_send("0613", pc, shop.item) #NPCのショップウィンドウ

def npcsell(pc):
	with pc.lock and pc.user.lock:
		pc.shop_open = 65535 #sell
		pc.map_send("0615") #NPCショップウィンドウ（売却）

def spawn(pc, monster_id):
	with pc.lock:
		error = monsters.spawn(monster_id, pc.map_id, pc.x, pc.y)
		if error: msg(pc, error)

def killall(pc):
	with pc.lock and pc.map_obj.lock:
		while pc.map_obj.monster_list:
			monsters.delete(pc.map_obj.monster_list.pop())

def emotion(pc, emotion_id):
	general.assert_value_range("emotion_id", emotion_id, general.RANGE_UNSIGNED_SHORT)
	with pc.lock and pc.user.lock:
		pc.map_send_map("1217", pc, emotion_id) #emotion

def emotion_ex(pc, emotion_ex_id):
	general.assert_value_range(
		"emotion_ex_id", emotion_ex_id, general.RANGE_UNSIGNED_BYTE
	)
	with pc.lock and pc.user.lock:
		pc.map_send_map("1d0c", pc, emotion_ex_id) #emotion_ex

def shownpc(pc, npc_id):
	general.assert_value_range("npc_id", npc_id, general.RANGE_UNSIGNED_INT)
	with pc.lock and pc.user.lock:
		pc.map_send("05e2", npc_id) #show npc

def hidenpc(pc, npc_id):
	general.assert_value_range("npc_id", npc_id, general.RANGE_UNSIGNED_INT)
	with pc.lock and pc.user.lock:
		pc.map_send("05e3", npc_id) #hide npc

def blackout(pc, time_ms):
	general.assert_value_range("time_ms", time_ms, general.RANGE_UNSIGNED_INT)
	with pc.lock and pc.user.lock:
		pc.map_send("0609", 1, 0) #blackout on
	wait(pc, time_ms)
	with pc.lock and pc.user.lock:
		pc.map_send("0609", 0, 0) #blackout off

def whiteout(pc, time_ms):
	general.assert_value_range("time_ms", time_ms, general.RANGE_UNSIGNED_INT)
	with pc.lock and pc.user.lock:
		pc.map_send("0609", 1, 1) #whiteout on
	wait(pc, time_ms)
	with pc.lock and pc.user.lock:
		pc.map_send("0609", 0, 1) #whiteout off

def size(pc, pc_size):
	general.assert_value_range("pc_size", pc_size, general.RANGE_UNSIGNED_INT)
	with pc.lock:
		#default: 1000
		pc.size = pc_size
	with pc.lock and pc.user.lock:
		pc.map_send_map("020f", pc, pc_size) #size
	#update(pc)

def petstandby_on(pc):
	with pc.lock:
		if not pc.pet:
			return
		with pc.pet.lock:
			pc.pet.standby = True

def petstandby_off(pc):
	with pc.lock:
		if not pc.pet:
			return
		with pc.pet.lock:
			pc.pet.standby = False

def petmotion(pc, motion_id, motion_loop=False):
	general.assert_value_range("motion_id", motion_id, general.RANGE_UNSIGNED_SHORT)
	with pc.lock and pc.user.lock:
		if not pc.pet:
			return
		pc.pet.set_motion(motion_id, motion_loop)
		#モーション通知
		pc.map_send_map("121c", pc, pc.pet.id, motion_id, motion_loop)

def petmotion_loop(pc, motion_id):
	petmotion(pc, motion_id, True)

def unsetallequip(pc):
	pc.unset_all_equip()

def printallequip(pc):
	for attr in general.EQUIP_ATTR_LIST:
		msg(pc, "%s %s"%(attr, pc.item.get(getattr(pc.equip, attr))))

name_map = general.get_name_map(globals(), "")