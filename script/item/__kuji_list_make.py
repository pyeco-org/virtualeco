#-*- coding: utf-8 -*-
import sys
import os

item = {}
for line in open("/media/truecrypt3/server/pyecotools/item.csv"):
	if line.startswith("#"):
		continue
	row = line.split(",", 5)
	if len(row) < 5:
		continue
	item[row[3]] = row[0]

a = open("2012_", "rb")
i = open("2012", "wb")
while True:
	name = a.readline()
	if not name:
		break
	name = name.strip()
	i.write("(\"%s\", (\n"%name)
	while True:
		j = a.readline().strip()
		if not j:
			break
		if j.startswith("「"):
			continue
		if j.startswith("※"):
			continue
		row = j.split()
		try:
			i.write("\t(%s, %s, \"%s\"),\n"%(item[row[1]], 1, row[1]))
		except:
			print "error", j
			i.write("\t#(None, None, \"%s\"),\n"%row[1])
			continue
	i.write(")),\n")