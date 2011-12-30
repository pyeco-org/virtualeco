#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

class Pet:
	def __init__ (self, row):
		self.pet_id = row[0] #pet id
		self.name = row[1]
		self.pictid = row[2] #pet pictid
		self.hp = row[19]
		self.maxhp = row[19]
		self.sid = 0 #server id
		self.charid = 0 #=sid
		self.master = None # PC()
		self.map = 0
		self.x = 0
		self.y = 0
		self.dir = 0
		self.rawx = 0
		self.rawy = 0
		self.rawdir = 0
		self.speed = 310 #410
		self.motion = 0
		self.lv_base = 1
		#for CreatePacket.create020e
		self.race = 0
		self.form = 0
		self.gender = 1
		self.hair = 0
		self.haircolor = 0
		self.wig = 0
		self.face = 0
		self.base_lv = 0
		self.ex = 0
		self.wing = 0
		self.wingcolor = 0
		self.wrprank = 0
		self.item = {1: Pet.Item(self.pictid)}
		self.equip = Pet.Equip()
	
	class Item:
		def __init__(self, i):
			self.id = i
			self.type = "HELM"
	
	class Equip:
		def __init__(self):
			self.head = 1
			self.face = 0
			self.chestacce = 0
			self.tops = 0
			self.bottoms = 0
			self.backpack = 0
			self.right = 0
			self.left = 0
			self.shoes = 0
			self.socks = 0
			self.pet = 0
