#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class Item:
	def __init__(self, d):
		d.update(self.__dict__)
		self.__dict__ = d
		self.count = 1
		self.warehouse = 0
	
	def __str__(self):
		return "%s<%s, %s, %d>"%(repr(self), self.item_id, self.name, self.count)
	
	def check_type(self, item_type):
		if not item_type:
			return True
		elif hasattr(item_type, "__iter__") and self.type in item_type:
			return True
		elif self.type == item_type:
			return True
		else:
			return False
	
	def get_pict_id(self, item_type):
		if self.check_type(item_type):
			return (self.pict_id or self.item_id)
		else:
			return 0
	
	def get_attr(self, attr, item_type, default_value):
		return getattr(self, attr) if self.check_type(item_type) else default_value
	
	def get_int_attr(self, attr, item_type):
		return self.get_attr(attr, item_type, 0)
	
	def get_str_attr(self, attr, item_type):
		return self.get_attr(attr, item_type, "")
	
	def get_bool_attr(self, attr, item_type):
		return self.get_attr(attr, item_type, False)