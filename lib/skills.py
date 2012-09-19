#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import thread
from lib import general
from lib import monsters

def use(pc, target_id, x, y, skill_id, skill_lv):
	mod = name_map.get(str(skill_id))
	if mod is None:
		return None
	thread.start_new_thread(use_thread, (mod, pc, target_id, x, y, skill_id, skill_lv))
	return True

def use_thread(mod, pc, target_id, x, y, skill_id, skill_lv):
	try:
		#with pc.lock: #remove global lock because time.sleep blocking
		mod(pc, target_id, x, y, skill_id, skill_lv)
	except:
		general.log_error("[skill] error", pc, target_id, x, y, skill_id, skill_lv)
		general.log_error(traceback.format_exc())

def do_3054(pc, target_id, x, y, skill_id, skill_lv):
	#ヒーリング 対象のHPを回復する
	cast = 500
	#スキル使用通知
	pc.map_send_map("1389", pc, target_id, x, y, skill_id, skill_lv, 0, cast)
	time.sleep(cast/1000.0)
	#スキル使用結果通知（対象：単体）, HP回復
	pc.map_send_map("1392", pc, (target_id,), skill_id, skill_lv, (-100,), (17,))
	pc.set_battlestatus(1)

def do_3029(pc, target_id, x, y, skill_id, skill_lv):
	#アイスアロー 敵に水の力を持つ魔法攻撃を行う
	monster = monsters.get_monster_from_id(target_id)
	if monster is None:
		#スキル使用 #ターゲットが見つかりません
		pc.map_send("1389", pc , -1, x, y, skill_id, skill_lv, 4, -1)
		#スキル使用通知 #ターゲットが見つかりません
		pc.map_send("138a", pc, 4)
		return
	cast = 500
	damage = 75
	#スキル使用通知
	pc.map_send_map("1389", pc, target_id, x, y, skill_id, skill_lv, 0, cast)
	time.sleep(cast/1000.0)
	pc.set_battlestatus(1)
	monsters.magic_attack_monster(pc, monster, damage, skill_id, skill_lv)

name_map = general.get_name_map(globals(), "do_")

#skill error
#1 MPとSPが不足しています 
#2 使用する触媒が不足しています 
#3 ターゲットが視認できません 
#4 ターゲットが見つかりません 
#5 装備中の武器ではこのスキルを使用できません 
#6 指定不可能な位置が選択されました 
#7 スキルを使用できない状態です 
#8 他のスキルを詠唱している為キャンセルされました 
#9 遠距離攻撃中の為キャンセルされました 
#10 スキルを習得していません 
#11 対象が行動不能状態の為ターゲットできません 
#12 スキル使用条件があっていません 
#13 スキルを使用できません 
#14 スキルを使用できない対象です 
#15 MPが不足しています 
#16 SPが不足しています 
#17 指定した地形は別のスキルの効果中です 
#18 近くにテントが張られています 
#19 アイテム使用中の為キャンセルされました 
#20 攻撃中の為キャンセルされました 
#21 反応がありませんでした 
#エラーコード22はメッセージ無し
#23 憑依しないと使えません 
#24 他の憑依者が効果中です 
#25 憑依中は使えないスキルです 
#26 使用するのに必要なお金が足りません 
#27 宿主が健全でないため使用できません 
#28 宿主が行動不能時のみ使うことができます 
#29 スキルが使えない場所にいます 
#30 前回のスキルのディレイが残っています 
#31 ペットがいないと使えません 
#32 このマップではそのスキルを使うことは出来ません 
#33 指定した場所に敵が侵入しているため使用できませんでした 
#34 矢を装備していないと使用できません 
#35 実包を装備していないと使用できません 
#36 投擲武器を装備していないと使用できません 
#37 使用できるテントを所持していません 
#38 栽培に使用するアイテムを所持していません 
#39 鑑定できるアイテムを所持していません 
#40 開けることのできるアイテムを所持していません 
#41 合成することのできるアイテムを所持していません 
#42 対象が移動したため射程から外れました 
#43 「メタモーバトル」中は使用できません 
#44 これ以上このスキルを設置することは出来ません 
#エラーコード45はGAME_SYNTHE_FULL_ITEM（アイテム欄に空きがありません）で代用中を廃止
#45 アイテム欄に空きがありません 
#46 『騎士団演習』中は使用できません 
#47 ペットが近くにいないと使用できません 
#48 敵に発見された為、失敗しました 
#49 宿主中は使えないスキルです 
#50 再度スキルを使用するには時間を置いてください 
#51 ペットを使役している間は使用できません 
#52 ボスへの使用はできません 
#53 アンデッド状態の対象への使用はできません 
#54 現在の装備ではこのスキルを使用できません 
#55 矢の数が足りません 
#56 実包の数が足りません 
#57 投擲武器の数が足りません 
#58 融合できるマリオネットが違います 
#59 イベント中の為、使用できません 
#60 設定が不許可になっている為、使用できません 
#61 消費アイテムを装備していないと使用できません 
#62 EPが不足しています 
#63 H.E.ART レベルの上限を超えています 
#64 H.E.ART レベルが足りません 
#65 使用できるログハウスを所持していません 
#66 分解できるものがありません 
#67 エンシェントアークでは使用することができません 
#68 餌を装備していないと使用できません 
