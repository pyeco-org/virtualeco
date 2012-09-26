#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib import env
from lib import script
ID = 30

def main(pc):
	script.msg(pc, "-"*30)
	script.msg(pc, "%s %s"%(env.NAME, env.LAST_UPDATE))
	script.msg(pc, "%s"%env.RUNTIME_VERSION_ALL)
	script.msg(pc, "-"*30)