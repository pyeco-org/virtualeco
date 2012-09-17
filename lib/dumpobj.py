#!/usr/bin/env python
# -*- coding: utf-8 -*-
#why not json or yaml: they dont support dump and load binary data
#why not struct: difficult to edit with text editor
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

class LoadError(Exception): pass
class DumpError(Exception): pass

def _read_block(s):
	buf = []
	while True:
		j = s.read(1)
		if not j:
			break
		if j in (",", ":", "]", "}", ")", " "):
			s.seek(s.tell()-1)
			break
		buf.append(j)
	return "".join(buf)
def _seek_block(s, mask):
	while True:
		j = s.read(1)
		if not j:
			raise LoadError("data corrupt: seek block %s failed, index %s"%(
				mask, s.tell()
			))
		elif j == mask:
			return True
		elif j in _load_map:
			s.seek(s.tell()-1)
			return False
def _seek_comma(s, mask):
	while True:
		j = s.read(1)
		if not j:
			raise LoadError("data corrupt: seek comma before %s failed, index %s"%(
				mask, s.tell()
			))
		elif j == mask:
			return False
		elif j == ",":
			return True
		elif j in _load_map:
			raise LoadError("data corrupt: %s not found, index %s"%(mask, s.tell()))
def _load_int(s):
	return int(_read_block(s))
def _load_long(s):
	return long(_read_block(s))
def _load_bool(s):
	return bool(_read_block(s))
def _load_float(s):
	return float(_read_block(s))
def _load_string(s):
	l = _load_int(s)
	s.read(1) #" "
	return s.read(l)
def _load_unicode(s):
	l = _load_int(s)
	s.read(1) #" "
	r = s.read(l)
	try:
		return r.decode("utf-8")
	except UnicodeDecodeError:
		return unicode(r, "latin-1")
def _load_dict(s):
	r = {}
	while True:
		if _seek_block(s, "}"):
			break
		key = _load_obj(s)
		if not _seek_block(s, ":"):
			raise LoadError("data corrupt: value not found, index %s"%s.tell())
		value = _load_obj(s)
		r[key] = value
		if not _seek_comma(s, "}"):
			break
	return r
def _load_list(s):
	r = []
	while True:
		if _seek_block(s, "]"):
			break
		r.append(_load_obj(s))
		j = s.tell()
		if not _seek_comma(s, "]"):
			break
	return r
def _load_tuple(s):
	r = []
	while True:
		if _seek_block(s, ")"):
			break
		r.append(_load_obj(s))
		j = s.tell()
		if not _seek_comma(s, ")"):
			break
	return tuple(r)
def _load_none(s):
	return None
_load_map = {
	"i": _load_int,
	"l": _load_long,
	"b": _load_bool,
	"f": _load_float,
	"s": _load_string,
	"u": _load_unicode,
	"[": _load_list,
	"{": _load_dict,
	"(": _load_tuple,
	"n": _load_none,
}
def _load_obj(s):
	while True:
		j = s.read(1)
		if not j:
			raise LoadError("data corrupt, index %s"%s.tell())
		elif j in (",", ":", " "):
			continue
		elif j in ("]", "}", ")"):
			raise LoadError("data corrupt, index %s"%s.tell())
		else:
			mod = _load_map[j]
			if mod is None:
				raise LoadError("unknow data type %s, index %s"%(j, s.tell()))
			return mod(s)
def loads(s):
	#syntax checking are weak
	io = StringIO(s)
	r = _load_obj(io)
	extra = io.read().strip()
	if extra and not extra.startswith("#"):
		raise LoadError("extra data found: %s"%extra)
	return r

def _dump_int(i):
	return "i%s"%i
def _dump_long(i):
	return "l%s"%i
def _dump_bool(i):
	return "b%s"%int(i)
def _dump_float(i):
	return "f%s"%i
def _dump_string(i):
	return "s%s %s"%(len(i), i)
def _dump_unicode(i):
	i = i.encode("utf-8")
	return "u%s %s"%(len(i), i)
def _dump_list(i):
	if not i:
		return "[]"
	l = ["["]
	for j in i:
		l.append(_dump_obj(j))
		l.append(", ")
	l[-1] = "]"
	return "".join(l)
def _dump_dict(i):
	if not i:
		return "{}"
	l = ["{"]
	for key, value in i.iteritems():
		l.append(_dump_obj(key))
		l.append(": ")
		l.append(_dump_obj(value))
		l.append(", ")
	l[-1] = "}"
	return "".join(l)
def _dump_tuple(i):
	if not i:
		return "()"
	l = ["("]
	for j in i:
		l.append(_dump_obj(j))
		l.append(", ")
	l[-1] = ")"
	return "".join(l)
def _dump_none(i):
	return "n"
_dump_map = {
	int: _dump_int,
	long: _dump_long,
	bool: _dump_bool,
	float: _dump_float,
	str: _dump_string,
	unicode: _dump_unicode,
	list: _dump_list,
	dict: _dump_dict,
	tuple: _dump_tuple,
	type(None): _dump_none,
}
def _dump_obj(i):
	mod = _dump_map.get(type(i))
	if mod is None:
		raise DumpError("dumpobj not support dump %s %s"%(type(obj), str(obj)))
	return mod(i)
def dumps(i):
	return _dump_obj(i)

def _test_data():
	s = dumps({
		"string": "abc",
		"int": 123,
		"long": -123L,
		"float": 1.01,
		"unicode": u"abcde",
		"dict": {
			"dict_int": -123,
			"dict_string": "☆★☆★☆",
		},
		"list": [10, 100, (101, True, None)],
		0: [("", "", [])],
	})
	print s
	print loads(s)
	print loads("[i1, i2, i3, (s1  ), {}, i-100000000000000000000000000000000000]")
	print [loads("l10")]
	print loads("s11 hello world")
	s = dumps("".join((chr(i) for i in xrange(256))))
	print s
	print loads(s)

def _test_performance():
	import time
	
	start = time.time()
	print "start dump"
	for i in xrange(1000000):
		s = dumps({-1:"0", "0":"HELLOWORLD", True:100000000})
	print time.time()-start
	
	start = time.time()
	print "start load"
	for i in xrange(1000000):
		aa = loads(s)
	print time.time()-start
	print "done."

if __name__ == "__main__":
	_test_data()
	_test_performance()
