#!/bin/python
# -*- coding: utf-8 -*-
from Object.eventobj import *

class Script:
	def get_id(self):
		event_id = []
		event_id.append(90000074)
		return event_id
	
	def command_info(self, pc):
		option =	["システム",
				"アイテム",
				"プレイヤー属性",
				"モンスター",
				"閉じる",
				]
		while True:
			r = int(select(pc, option, "コマンド説明"))
			if r == 1:
				say(pc, "".join((
					"!help と !commandlist$R",
					"コマンド一覧$R$R",
					"!user と /user$R",
					"オンラインプレイヤーの名前と場所一覧$R$R",
					"/dustbox$R",
					"携帯ごみ箱",
					"$P",
					"!reloadscript$R",
					"スクリプト再読み込み$R$R",
					"!servermessage servermessage$R",
					"!sm servermessage$R",
					"サーバメッセージを送る",
					"$P",
					"!event event_id$R",
					"イベントを発生させる$R$R",
					"!warp map_id ( x y )$R",
					"指定されたマップにワープする$R座標を指定しない場合はマップの中央座標にする"
					"$P",
					"!warpraw map_id ( x y )$R",
					"warpと同じ、ただしraw座標を使う$Rraw座標は!whereから見れる"
					)), "システムコマンド説明")
			elif r == 2:
				say(pc, "".join((
					"!printitem$R",
					"アイテムリスト一覧$R$R",
					"!shop shop_id$R"
					"商店を開く$R",
					"./Database/shop.csvから読み込んたデータを使う"
					"$P",
					"!wh warehouse_id$R"
					"倉庫を開く$R",
					"id 0はアクロポリスシティ$R$R"
					"!item item_id <count>$R",
					"!giveitem item_id <count>$R",
					"アイテムを入手する$R数を指定しない場合は１にする$R",
					"./Database/item.csvから読み込んたデータを使う",
					"$P",
					"!takeitem item_id <count>$R",
					"アイテムを取らせる$R",
					"数を指定しない場合は１にする$R$R"
					"!countitem item_id <count>$R",
					"アイテムの数を求む",
					"$P",
					"!sell$R",
					"アイテム売却のウィンドウを開く",
					)), "アイテムコマンド説明")
			elif r == 3:
				say(pc, "".join((
					"!gold num$R",
					"!updategold num$R",
					"持ち金の数を指定する$R$R",
					"!hair hair_id$R",
					"プレーヤーの髪型を変える$R$R",
					"!haircolor haircolor_id$R",
					"!hc haircolor_id$R",
					"プレーヤーの髪色を変える",
					"$P",
					"!face face_id$R",
					"---$R$R",
					"!wig wig_id$R",
					"プレーヤーのウィッグを変える$R$R",
					"!ex ex_id$R",
					"プレーヤーの転生特典を変える$R$R",
					"$P",
					"!wing wing_id$R",
					"プレーヤーの羽を変える$R$R",
					"!wingcolor wingcolor_id$R",
					"!wc wingcolor_id$R",
					"プレーヤーの羽色を変える$R$R",
					"!motion motion_id$R",
					"プレーヤーのモーションを変える",
					"$P",
					"!effect effect_id$R",
					"エフェクトを出す$R$R",
					"!speed num$R",
					"プレーヤーの移動速度を変える$R$R",
					)), "プレイヤー属性コマンド説明")
			elif r == 4:
				say(pc, "".join((
					"!mob mobid$R",
					"モンスターを沸かす$R",
					"./Database/mob.csvから読み込んたデータを使う$R$R",
					"!killallmob$R",
					"プレーヤーの所在マップのモンスターを$R全部消す",
					)), "モンスターコマンド説明")
			else:
				break

	def main(self, pc):
		option =	["コマンド説明",
				"ごみ箱",
				"倉庫(id-0)",
				"ワープ(フシギ団本部)",
				"閉じる",
				]
		r = int(select(pc, option, "初心者の箱"))
		if r == 1:
			self.command_info(pc)
		elif r == 2:
			npctrade(pc)
		elif r == 3:
			warehouse(pc, 0)
		elif r == 4:
			warp(pc, 30131001, 5, 6)
		else:
			pass