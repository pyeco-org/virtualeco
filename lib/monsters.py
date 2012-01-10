#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import threading
import thread
import traceback
from lib.packet import packet
from lib import general
from lib import script
from lib import db
MONSTER_ID_START_FROM = 10000
MONSTER_DEL_DELAY = 5000
monster_id_list = []
monster_list = []
monster_list_lock = threading.RLock()

def send_map(map_id, *args):
	map_obj = general.get_map(map_id)
	if not map_obj:
		error = "send_map: map_id %s not exist."%map_id
		general.log_error(error)
		return error
	with map_obj.lock:
		for pc in map_obj.pc_list:
			if not pc.online:
				continue
			try:
				with pc.lock and pc.user.lock:
					pc.user.map_client.send(*args)
			except:
				general.log_error("send_map error: %s"%traceback.format_exc())

def spawn(monster_id, map_id, x, y):
	monster = general.get_monster(monster_id)
	if not monster:
		error = "spawn: monster_id %s not exist."%monster_id
		general.log_error(error)
		return error
	monster.reset()
	with monster_list_lock and monster.lock:
		monster.id = get_new_monster_id()
		monster.set_map(map_id)
		monster.set_coord(x, y)
		monster_list.append(monster)
		monster_id_list.append(monster.id)
	error = send_map(map_id, "122a", (monster.id,)) #モンスターID通知
	if error:
		delete(monster)
		return error
	general.log("[monster] spawn monster id %s"%(monster.id))
	send_map(map_id, "1220", monster) #モンスター情報
	send_map(map_id, "157c", monster) #キャラの状態

def delete(monster):
	with monster_list_lock and monster.lock:
		monster_list.remove(monster)
		monster_id_list.remove(monster.id)
		send_map(monster.map_id, "1225", monster) #モンスター消去
		general.log("[monster] delete monster id %s"%(monster.id))
		monster.reset()
	del monster

def delete_monster_thread(monster):
	time.sleep(MONSTER_DEL_DELAY/1000.0)
	delete(monster)

def attack_monster(pc, monster):
	with pc.lock and pc.user.lock and monster.lock:
		if monster.status.hp <= 0:
			general.log_error("[monster] monster.hp <= 0")
			pc.reset_attack()
			return
		damage = 10
		state01 = 0
		flag = 1 #HPダメージ
		monster.status.hp -= damage
		if monster.status.hp <= 0:
			monster.status.hp = 0
			state01 = 0x200 #行動不能
			flag = 0x4001 #HPダメージ + 消滅モーション
			pc.reset_attack()
			thread.start_new_thread(delete_monster_thread, (monster,))
			script.msg(pc, "基本経験値 0、職業経験値 0を取得しました")
		pc.user.map_client.send_map("0fa1", pc, monster, 0, damage, flag) #攻撃結果
		pc.user.map_client.send_map("021c", monster) #現在のHP/MP/SP/EP
		pc.user.map_client.send_map("157c", monster, state01) #キャラの状態

def get_monster_list():
	l = []
	with monster_list_lock:
		for monster in monster_list:
			l.append(monster)
	return l

def get_monster_from_id(i):
	for monster in get_monster_list():
		with monster.lock:
			if monster.id == i:
				return monster

def get_new_monster_id():
	last_id = MONSTER_ID_START_FROM
	with monster_list_lock:
		for i in sorted(monster_id_list):
			if i > last_id+1:
				return last_id+1
			else:
				last_id = i
	return last_id+1