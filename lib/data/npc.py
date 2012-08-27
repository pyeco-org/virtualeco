#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class Npc:
	def __init__(self, d):
		d.update(self.__dict__)
		self.__dict__ = d
	
	def __str__(self):
		return "%s<%s, %s>"%(repr(self), self.npc_id, self.name)