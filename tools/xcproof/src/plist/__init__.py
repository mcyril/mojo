# 2013 (c) Unreal Mojo
# by Cyril Murzin

#
#	simple classes to aggregate plist file access variations
#	uses:
#		ASCII (NeXTStep) plist access classes by Simon Wagner
#			https://github.com/simonwagner/mergepbx
#			(part of mergepbx: script for merging XCode project files in git)
#		Python built-in plistlib module to access XML plist
#		Binary plist access classes by Andrew Wooster
#			https://bitbucket.org/wooster/biplist
#

from asplist import NSPlistReader, NSPlistWriter
from biplist import PlistReader, PlistWriter

import subprocess
import plistlib
import json

# ========================================================================================

UNKNOWN = -1
ASCII = 0
XML = 1
BINARY = 2
JSON = 3
ANY_VALID = 10

# ========================================================================================

class plistReader(object):
	def __init__(self, path):
		self.path = path
		self.typ = UNKNOWN

	def read(self):
		try:
		#	use old (xcproof 0.0.1) plist reading mechanism to speed-up processing under OS X with plutil tool installed
			json_string = subprocess.check_output(["/usr/bin/plutil", "-convert", "json", "-o", "-", self.path])
			self.typ = ANY_VALID
			return json.loads(json_string)
		except:
		#	use new (xcproof 0.0.2) universal plist reading mechanism with 3rd party codecs
			fin = None
			try:
				fin = open(self.path)

		#	try BINARY plist with biplist codec
				try:
					self.typ = BINARY
					fin.seek(0)
					return PlistReader(fin).parse()
				except:
		#	try XML plist with built-in codec
					try:
						self.typ = XML
						fin.seek(0)
						return plistlib.readPlist(fin)
					except:
		#	try JSON plist (never seen that though) with built-in codec
						try:
							self.typ = JSON
							fin.seek(0)
							return json.load(fin)
						except:
		#	try ASCII plist with mergepbx's codec
							try:
								self.typ = ASCII
								fin.seek(0)
								return NSPlistReader(fin).read()
							except:
								self.typ = UNKNOWN
								raise
			finally:
				if fin != None:
					fin.close()

class plistWriter(object):
	def __init__(self, path, typ=XML):
		self.path = path
		self.typ = typ

	def write(self, data):
		fout = None
		try:
			fout = open(self.path, "w")
			if self.typ == ASCII:
				NSPlistWriter(fout).write(data)
			elif self.typ == XML:
				plistlib.writePlist(data, fout)
			elif self.typ == BINARY:
				PlistWriter(fout).writeRoot(data)
			elif self.typ == JSON:
				json.dump(data, fout)
			else:
				raise
		except:
			pass
		finally:
			if fout != None:
				fout.close()
