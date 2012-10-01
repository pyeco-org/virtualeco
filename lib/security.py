#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import zipfile
import traceback
import __builtin__
__open = __builtin__.open
__listdir = os.listdir
__remove = os.remove
__rmdir = os.rmdir
__mkdir = os.mkdir
__rename = os.rename
__chdir = os.chdir
__base = None

def within_base(path, base):
	return os.path.realpath(path).startswith(os.path.realpath(base or __base))

def secure_open(name, mode="r", buffering=True, base=None):
	#don't check symbolic links at this moment
	#sys.stderr.write("secure_open [%s] (%s) within [%s]\n"%(name, mode, base))
	if not within_base(name, base):
		raise IOError("cannot open [%s] (%s) outside of [%s]"%(name, mode, base))
	return __open(name, mode, buffering)

def secure_listdir(path, base=None):
	#sys.stderr.write("secure_listdir [%s] within [%s]\n"%(path, base))
	if not within_base(path, base):
		raise IOError("cannot list [%s] outside of [%s]"%(path, base))
	return __listdir(path)

def secure_remove(path, base=None):
	#sys.stderr.write("secure_remove [%s] within [%s]\n"%(path, base))
	if not within_base(path, base):
		raise IOError("cannot remove [%s] outside of [%s]"%(path, base))
	return __remove(path)

def secure_rmdir(path, base=None):
	#sys.stderr.write("secure_rmdir [%s] within [%s]\n"%(path, base))
	if not within_base(path, base):
		raise IOError("cannot remove dir [%s] outside of [%s]"%(path, base))
	return __rmdir(path)

def secure_mkdir(path, mode=0777, base=None):
	#sys.stderr.write("secure_mkdir [%s] (%s) within [%s]\n"%(path, mode, base))
	if not within_base(path, base):
		raise IOError("cannot create dir [%s] (%s) outside of [%s]"%(path, mode, base))
	return __mkdir(path)

def secure_rename(old, new, src_base=None, dst_base=None):
	#sys.stderr.write("secure_rename from [%s] within [%s]\n"%(old, src_base))
	#sys.stderr.write("secure_rename to [%s] within [%s]\n"%(new, dst_base))
	if not within_base(old, src_base):
		raise IOError("cannot rename from [%s] outside of [%s]"%(old, src_base))
	if not within_base(new, src_base):
		raise IOError("cannot rename to [%s] outside of [%s]"%(new, dst_base))
	return __rename(old, new)

def secure_chdir():
	return __chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

def secure_save_zip(path_src, path_zip, src_base=None, zip_base=None, compress=False):
	#sys.stderr.write("secure_save_zip from [%s] within [%s]\n"%(path_src, src_base))
	#sys.stderr.write("secure_save_zip to [%s] within [%s]\n"%(path_zip, zip_base))
	if not within_base(path_src, src_base):
		raise IOError("cannot save zip from [%s] outside of [%s]"%(path_src, src_base))
	if not within_base(path_zip, zip_base):
		raise IOError("cannot save zip to [%s] outside of [%s]"%(path_src, zip_base))
	mode = zipfile.ZIP_STORED if not compress else zipfile.ZIP_DEFLATED
	zip_obj = zipfile.ZipFile(path_zip, "w", mode)
	for root, dirs, files in os.walk(path_src):
		for dir_name in dirs:
			zip_obj.write(os.path.join(root, dir_name),
				os.path.join(root, dir_name).replace(path_src, ""))
		for file_name in files:
			zip_obj.write(os.path.join(root, file_name),
				os.path.join(root, file_name).replace(path_src, ""))
	zip_obj.close()

def __raise(e):
	raise e

def init(base):
	global __base
	__base = base
	__builtin__.open = secure_open
	__builtin__.file = secure_open
	os.listdir = secure_listdir
	os.remove = secure_remove
	os.unlink = secure_remove
	os.rmdir = secure_rmdir
	os.mkdir = secure_mkdir
	os.rename = secure_rename
	os.link = lambda *args: __raise(IOError("os.link disabled"))
	os.symlink = lambda *args: __raise(IOError("os.symlink disabled"))
	os.chdir = lambda *args: __raise(IOError("os.chdir disabled"))
	#posix
	os.chmod = lambda *args: __raise(IOError("os.chmod disabled"))
	os.chown = lambda *args: __raise(IOError("os.chown disabled"))
	os.chroot = lambda *args: __raise(IOError("os.chroot disabled"))
	os.mkfifo = lambda *args: __raise(IOError("os.mkfifo disabled"))
