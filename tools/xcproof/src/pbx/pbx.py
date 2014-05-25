# 2012-2014 (c) Unreal Mojo
# by Cyril Murzin

from verify import verify_base

import os

# ========================================================================================

class pbx(object):

	def __init__(self, pbxproj, projectpath):

		self.pbxproj = pbxproj			# internals
		self.projectpath = projectpath	# path for project
		self.groups = []				# groups
		self.files = []					# full set of project's file keys

		# integrity check
		if not 'objects' in self.pbxproj:
			raise Exception("no objects found")

		self.objects = self.pbxproj['objects'] # objects list

		# make prebuilt lists
		for key in self.objects:
			object = self.objects[key]
			isa = object['isa']

			if isa == 'PBXFileReference':
				self.files.append(key)
			elif isa == 'PBXGroup' or isa == 'PBXVariantGroup':
				self.groups.append(key)
			elif isa == 'PBXProject':
				if hasattr(self, 'project'):
					raise Exception("duplicated root object")
				else:
					self.project = key	# preserve root key from object

		# integrity checks
		if not hasattr(self, 'project'):					# got root object
			raise Exception("got no root object")
		elif not 'rootObject' in self.pbxproj:				# root key exists
			raise Exception("no root key exists")
		elif self.project != self.pbxproj['rootObject']:	# root key matches root object
			raise Exception("root key does not match root object")

		self.srcroot = self.projectpath + self.objects[self.project]['projectRoot'] # source root path

	#
	# hmm... utility to get path and name; TODO: confirm later that data isn't synthesized and from project (so re-use principle is OK)
	#
	def obtain_namepath(self, object):
		if 'path' in object:
			path = object['path']
		else:
			path = ""

		if 'name' in object:
			name = object['name']
		else:
			name = path

		return (name, path)

	#
	# create path for certain file and make decision if we should check/process it
	#
	def reinterpret_paths(self, object, parentpath, path, level):

		if level > 0:
			if 'sourceTree' in object:
				tree = object['sourceTree']

				if tree == '<group>':
					return (parentpath + "/" + path, True)		# file is in group, i.e. local; OK for us
				elif tree == '<absolute>':
					return (path, False)						# absolute file path usually useless from SDK or badly formed project; both not our case
				elif tree == 'SOURCE_ROOT':
					return (self.srcroot + "/" + path, True)	# file is in source tree, explicitly from root; OK for us
				elif tree == 'SDKROOT':
					return ("/" + path, False)					# file is in SDK explicitly; not our case
				elif tree == 'BUILT_PRODUCTS_DIR':
					return (path, False)						# file is in build phase; not our case
				else:
					return (self.srcroot + "/" + path, False)	# dunno what is it; not our case
			else:
					return (self.srcroot + "/" + path, False)	# dunno what is it; not our case
		else:
			return (self.srcroot, False)						# root is definatle not our case

	#
	# hmm... utility to print path
	#
	def print_path(self, keys):
		level = 0
		for key in keys:
			level += 1

			object = self.objects[key]
			name, path = self.obtain_namepath(object)

			indent = "%%%ds%%s" % (level * 4)
			print indent % (" ", name)

	#
	# check certain file
	#
	def check_file(self, key, parentkeys, fullpath, level):

		file = self.objects[key]

		name, path = self.obtain_namepath(file)
		fullpath, check = self.reinterpret_paths(file, fullpath, path, level)

		status = verify_base.SKIP

		self.nfilesprocessed += 1

		if check:
			self.nfileschecked += 1

			if self.callback.process(key, parentkeys, file, fullpath):
				status = verify_base.OK
			else:
				status = verify_base.FAIL

		self.callback.log(name, fullpath, level, status)

	#
	# project hierarchy iterator bottleneck
	#
	def ckeck_group_deep(self, key, parentkeys, fullpath, level):

		group = self.objects[key]
		should_process = ('children' in group) and len(group['children']) > 0

		if should_process:

			name, path = self.obtain_namepath(group)
			fullpath, check = self.reinterpret_paths(group, fullpath, path, level)

			self.callback.log(name, fullpath, level, verify_base.FOLDER)

			if 'children' in group:
				for child in group['children']:
					if child in self.groups:
						self.ckeck_group_deep(child, parentkeys + [key], fullpath, level + 1)
					elif child in self.files:
						self.check_file(child, parentkeys + [key], fullpath, level + 1)

	#
	# main entry for processing of hierarchy
	#
	def process(self, callback):

		# clean up statics
		self.nfilesprocessed = 0		# statistics
		self.nfileschecked = 0			# statistics
		self.ok = False					# generalized conclusion about project's integrity

		if callback == None:
			raise

		self.callback = callback		# callback class

		# walk source group tree
		self.ckeck_group_deep(self.objects[self.project]['mainGroup'], [], self.srcroot, 0)

		self.ok = self.callback.ok()

		return self.ok


class _pbx_bundle():

	def __init__(self, path):

		self.path = path
		self.ext = None

	def __process_file(self, path):
		if path.endswith(self.ext):
			self.__founds += [path]

	def __process_dir(self, path):
		for fn in os.listdir(self.path + path):
			if fn.startswith("."):
				continue

			npath = os.path.join(path, fn)

			if os.path.isdir(self.path + npath):
				self.__process_dir(npath)
			elif os.path.isfile(self.path + npath):
				self.__process_file(npath)

	def list_with_ext(self, ext):
		self.ext = ext

		self.__founds = []
		self.__process_dir("/")

		return self.__founds


def _pbx_file_type(file):
	typ = file.get('lastKnownFileType')
	if typ != None:
		if typ == "file":	# unknown type, try resolve it with extension
			path = file.get('path')

			if path != None:
				if path.endswith(".m"):
					typ = "sourcecode.c.objc"
				elif path.endswith(".mm"):
					typ = "sourcecode.c.objcpp"
				elif path.endswith(".c"):
					typ = "sourcecode.c.c"
				elif path.endswith(".cpp"):
					typ = "sourcecode.cpp.cpp"
				elif path.endswith(".h"):
					typ = "sourcecode.c.h"
				elif path.endswith(".png"):
					typ = "image.png"
				elif path.endswith(".jpg"):
					typ = "image.jpeg"
				elif path.endswith(".plist"):
					typ = "text.plist.xml"

	return typ

#
# translate NSStringEncoding value to codecs string
#
def _pbx_file_encoding(source, dflt = "utf8"):

	finfo = source['file']

	enc = None

	if 'fileEncoding' in finfo:
		ienc = int(finfo['fileEncoding'])

		if ienc == 1:
			enc = "ascii"
		elif ienc == 3:
			enc = "euc_jp"
		elif ienc == 4:
			enc = "utf8"
		elif ienc == 5:
			enc = "latin_1"
		elif ienc == 8:
			enc = "shift_jis"
		elif ienc == 9:
			enc = "iso8859_2"
		elif ienc == 10:
			enc = "utf16"
		elif ienc == 11:
			enc = "cp1251"
		elif ienc == 12:
			enc = "cp1252"
		elif ienc == 13:
			enc = "cp1253"
		elif ienc == 14:
			enc = "cp1254"
		elif ienc == 15:
			enc = "cp1250"
		elif ienc == 21:
			enc = "iso2022_jp"
		elif ienc == 30:
			enc = "mac_roman"

	if enc == None:
		fin = open(source['path'], "rb")
		try:
			dat = fin.read(2)
			if ord(dat[0]) == 0xff and ord(dat[1]) == 0xfe:
				enc = "utf16"
			elif ord(dat[1]) == 0xff and ord(dat[0]) == 0xfe:
				enc = "utf16"
			elif dflt != "utf16":
				enc = dflt
			else:
				enc = "utf8"
		except:
			enc = dflt
		finally:
			fin.close()

	return enc

# ========================================================================================
