#!/usr/bin/env python
#-*- coding: utf-8 -*-
from lib import script

ID = 12001017 #アイテムチケット交換機 アップタウン東可動橋

def main(pc):
	kuji_box = script.script_list["kuji_box"]
	kuji_list = kuji_box["select_kuji_list"](pc)
	if not kuji_list:
		return
	item_list = kuji_box["select_item_list"](pc, kuji_list)
	if not item_list:
		return
	shop_item_list = [i[0] for i in item_list]
	if len(shop_item_list) <= 13:
		script.npcshop_list(pc, shop_item_list)
		return
	r = script.select(pc, ("01~13", "13~", "cancel"), "select shop")
	if r == 1:
		script.npcshop_list(pc, shop_item_list[:13])
	elif r == 2:
		script.npcshop_list(pc, shop_item_list[13:])