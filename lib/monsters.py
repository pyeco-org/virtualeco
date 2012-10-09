#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import threading
#import thread
import traceback
from lib.packet import packet
from lib import general
from lib import script
from lib import db
MIN_MONSTER_ID = 10000
MAX_MONSTER_ID = 20000
MONSTER_DEL_DELAY = 5000
monster_id_list = []
monster_list = []
monster_list_lock = threading.RLock()

def spawn(monster_id, map_id, x, y):
	error = None
	monster = general.get_monster(monster_id)
	if not monster:
		error = "spawn: monster_id %s not exist."%monster_id
		general.log_error(error)
		return error
	map_obj = general.get_map(map_id)
	if not map_obj:
		error = "spawn: map_id %s not exist."%map_id
		general.log_error(error)
		return error
	monster.reset()
	with monster_list_lock and monster.lock:
		monster_id = general.make_id(monster_id_list, MIN_MONSTER_ID)
		if monster_id >= MAX_MONSTER_ID:
			error = "[monster] ERROR: monster_id [%s] >= MAX_MONSTER_ID"%monster_id
			general.log_error(error)
			return error
		monster.id = monster_id
		monster.set_map(map_id)
		monster.set_coord(x, y)
		monster_list.append(monster)
		monster_id_list.append(monster.id)
	script.send_map_obj(map_obj, (), "122a", (monster.id,)) #モンスターID通知
	if error:
		delete(monster)
		return error
	general.log("[monster] spawn monster id %s"%(monster.id))
	script.send_map_obj(map_obj, (), "1220", monster) #モンスター情報
	script.send_map_obj(map_obj, (), "157c", monster) #キャラの状態

def delete(monster):
	with monster_list_lock and monster.lock:
		monster_list.remove(monster)
		monster_id_list.remove(monster.id)
		if monster.map_obj:
			script.send_map_obj(monster.map_obj, (), "1225", monster) #モンスター消去
		general.log("[monster] delete monster id %s"%(monster.id))
		monster.reset()
	del monster

def delete_monster_thread(monster):
	time.sleep(MONSTER_DEL_DELAY/1000.0)
	delete(monster)

def attack_monster(pc, monster):
	damage = 30
	color = 1 #HPダメージ
	monster_hp = monster.damage(damage)
	if monster_hp <= 0:
		color = 0x4001 #HPダメージ+消滅モーション
		pc.exp_add(0, 0)
	pc.map_send_map("0fa1", pc, monster, 0, damage, color) #攻撃結果

def magic_attack_monster(pc, monster, damage, skill_id, skill_lv):
	color = 1 #HPダメージ
	if monster.damage(damage) <= 0:
		color = 0x4001 #HPダメージ+消滅モーション
		pc.exp_add(0, 0)
	#スキル使用結果通知（対象：単体）
	pc.map_send_map(
		"1392", pc, (monster.id,), skill_id, skill_lv, (damage,), (color,)
	)

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

def init():
	global obj_monster
	from lib.obj import monster as obj_monster
	obj_monster.init()

#color
#0x01 hp damage
#0x02 mp damage
#0x04 sp damage
#0x11 hp heal
#0x22 mp heal
#0x44 sp heal
#0x100 critical
#0x200 miss
#0x400 avoid
#0x800 avoid
#0x1000 guard
#0x2000 
#0x4000 dead
#0x10000 barrier 