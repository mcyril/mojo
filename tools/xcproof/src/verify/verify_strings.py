# 2012-2014 (c) Unreal Mojo
# by Cyril Murzin

from pbx import pbx
from verify import verify_base

import os
import re
import codecs

# ========================================================================================

class verify_strings(verify_base.verify_base):

	def __init__(self, project):

		verify_base.verify_base.__init__(self, project)

		self.localizers = [r"NSLocalizedString[^\(]*"] # 'NSLocalizedString' as prefix
		self.allownested = True

		self.sources = []
		self.plists = []

		self.strings = []

	#	self.headers = False	# do [not] bypass headers
		self.showusage = False
		self.notlocalized = False


	#
	# process one file
	#
	def process(self, key, parentkeys, file, fullpath):

		typ = pbx._pbx_file_type(file)
		if typ != None:
			if typ.startswith("sourcecode.c.objc"): # objc/objc++ only
				self.sources += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]
	#		elif self.headers and self.headers == "sourcecode.c.h":
	#			self.sources += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]
			elif typ == "text.plist.strings":
				self.strings += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]
			elif typ.startswith("text.plist."):
				self.plists += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]

		return True


	#
	# tell iterator that something was wrong
	#
	def ok(self):

		return True


	#
	# log progress
	#
	def log(self, name, fullpath, level, stcode):
		pass


	#
	# private methods
	#

	def __retrieve_keys(self, string):

		keys = {}
		pairs = {}

		fin = codecs.open(string['path'], "rU", encoding = pbx._pbx_file_encoding(string, "utf16"))
		try:
			nline = 1

			for line in fin:
				got = self.__locstrpat.findall(line)
				if len(got) == 2:
					key = got[0][0]
					if key in keys:
						keys[key] += [nline]
					else:
						keys[key] = [nline]
						if self.notlocalized:
							pairs[key] = got[1][0]

				nline += 1

		except:
			pass

		finally:
			fin.close()

		return keys, pairs


	def __analyze_group(self, localized):

		groups = [ref[1] for ref in localized['refs']]
		missings = [[] for g in groups]

		for i in range(len(groups)):
			for j in range(len(groups)):
				if i == j:
					continue

				for key in groups[i]:
					if not key in groups[j] and not key in missings[j]:
						missings[j] += [key]

		for i in range(len(missings)):
			localized['refs'][i] = (localized['refs'][i][0], localized['refs'][i][1], missings[i], localized['refs'][i][3])


	def __analyze_dupes_and_missings(self, ref):
		ok = True

		for key in sorted(ref[1]):
			nlines = ref[1][key]

			if len(nlines) > 1:
				print "%16s* '%s' duplicated in lines: %s" % ("", key, ", ".join(str(i) for i in nlines))
				ok = False

		for missing in ref[2]:
			print "%16s* '%s' missing" % ("", missing)
			ok = False

		return ok

#-----------------------------------------------------------------------------------------

	def __safe_append_to_(self, strstates, key, string, source, nline, flag = 0):

		if key == None:
			strstate = strstates
		else:
			if not key in strstates:
				strstates[key] = {}

			strstate = strstates[key]

		if not string in strstate:
			strstate[string] = dict([('usage', [(source, nline, flag)])])
		else:
			usage = strstate[string]['usage']

			if nline == 0:
				for use in usage:
					if use[0] == source:
						return

			usage += [(source, nline, flag)]


	def _postprocess_string(self, string, source, nline):

		found = False

		for key in self.__localized:
			localized = self.__localized[key]

			found = string in localized['allpossibles']
			if found:
				self.__safe_append_to_(self.__stringsmap, localized['name'], string, source, nline)
				if string in localized['allmissings']:
					self.__safe_append_to_(self.__missings, None, string, source, nline, 1)
				break

		if not found:
			for key in self.__singlets:
				localized = self.__singlets[key]

				found = string in localized[1]
				if found:
					self.__safe_append_to_(self.__stringsmap, key, string, source, nline)
					break

		if self.allownested and not found:
			wildcard, haswild, dummy1, dummy2 = self.wildcard(string)
			if wildcard != None:
				wildpat = re.compile("^" + wildcard + "$")

				for key in self.__localized:
					localized = self.__localized[key]

					founds = [s for s in localized['allpossibles'] if wildpat.match(s) != None]

					for expanded in founds:
						self.__safe_append_to_(self.__stringsmap, localized['name'], expanded, source, nline)
						found = True

				for key in self.__singlets:
					localized = self.__singlets[key]

					founds = [s for s in localized[1] if wildpat.match(s) != None]

					for expanded in founds:
						self.__safe_append_to_(self.__stringsmap, key, expanded, source, nline)
						found = True

		if not found:
			self.__safe_append_to_(self.__missings, None, string, source, nline, 0)

		return found


	def _analyze_sources(self):

		objcstrpat = r"@\"(([^\"\\]|\\.)*)\""

		if self.allownested:
			tail = r"\s*\([^@]*" + objcstrpat + "[^@]*" + objcstrpat + "\s*\)"
		else:
			tail = r"\s*\(\s*" + objcstrpat + "[^@]*" + objcstrpat + "\s*\)"

		patterns = []
		for localizer in self.localizers:
			patterns += [re.compile(localizer + tail)]

		for source in self.sources:
			fin = codecs.open(source['path'], "rU", encoding = pbx._pbx_file_encoding(source))
			try:
				nline = 1

				for line in fin:
					for pattern in patterns:
						got = pattern.findall(line)
						for one in got:
							self._postprocess_string(one[0], source, nline)

					nline += 1
			except:
				pass
			finally:
				fin.close()

#-----------------------------------------------------------------------------------------

	def _preinitialize(self):

		self.__locstrpat = re.compile(r"\"(([^\"\\]|\\.)*)\"")


	def postprocess(self):

		verify_base.verify_base.postprocess(self)

		self.__localized = {}
		self.__singlets = {}

		# preprocess string files
		for string in self.strings:
			variant = None
			name = string['file']['path']

			parents = string['parentkeys']
			if len(parents) > 0:
				obj = self.project.objects[parents[-1]]

				if obj['isa'] == 'PBXVariantGroup':	# localized strings are placed in the 1st level of variant groups
					variant = parents[-1]
					name = obj['name']

			keys, pairs = self.__retrieve_keys(string)

			if variant == None:
				self.__singlets[name] = (string, keys, [])
			else:
				if variant in self.__localized:
					self.__localized[variant]['refs'] += [(string, keys, [], pairs)] # one day I have to stop to use tuples w/o a good reason
				else:
					self.__localized[variant] = { 'name':name, 'refs':[(string, keys, [], pairs)] }

		# mapping phase
		self.__stringsmap = {}

		# search for localized strings problems: dupes, outta' synced keys
		# print localized strings statistics
		if len(self.__localized) > 0:

			print "Strings files marked as localized in project"
			print "-------------------------------------------------------------------------------"

			for key in sorted(self.__localized):
				localized = self.__localized[key]

				print localized['name']

				self.__analyze_group(localized)

				allmissings = []
				insynch = True

				for ref in localized['refs']:
					if self.verbose > 0:
						print "%16s: %s" % (ref[0]['file']['name'], ref[0]['path'])
					else:
						print "%16s: %s" % (ref[0]['file']['name'], ref[0]['file']['path'])

					insynch = self.__analyze_dupes_and_missings(ref) and insynch

					allmissings += ref[2]

				localized['allpossibles'] = localized['refs'][0][1].keys() + localized['refs'][0][2]
				localized['allmissings'] = allmissings

				self.__stringsmap[localized['name']] = dict([(k, dict([('usage', [])])) for k in localized['allpossibles']])

				if self.notlocalized:
					if not insynch:
						print " * NON-LOCALIZED: <<skipping>>"
					else:
						print " * NON-LOCALIZED:"

		# search for regular strings problems: dupes
		# print regular strings statistics
		if len(self.__singlets) > 0:

			if self.showusage or len(self.__localized) > 0:
				print "-------------------------------------------------------------------------------"
			print "Strings files in project with no defined language(s)"
			print "-------------------------------------------------------------------------------"

			for key in sorted(self.__singlets):
				print key

				self.__analyze_dupes_and_missings(self.__singlets[key])

				self.__stringsmap[key] = dict([(k, dict([('usage', [])])) for k in self.__singlets[key][1]])

		self.__missings = {}

		# search for potential localized strings in sources
		self._analyze_sources()

		if self.showusage and len(self.__stringsmap) > 0:
			if len(self.__localized) > 0 or len(self.__singlets) > 0:
				print "-------------------------------------------------------------------------------"
			print "[PROBABLY] Usage of strings statistics"

		orphanes = {}

		# process statistics
		for locstrings in sorted(self.__stringsmap):
			if self.showusage:
				print "-------------------------------------------------------------------------------"
				print locstrings

			strstates = self.__stringsmap[locstrings]
			orphanes[locstrings] = []

			for key in sorted(strstates):
				strstate = strstates[key]

				if len(strstate['usage']) > 0:
					if self.showusage:
						print "    '%s'" % key

						for src in strstate['usage']:
							nline = src[1]
							path = src[0]['path']
							if self.verbose == 0:
								path = os.path.basename(path)

							if nline > 0:
								print "        %s:%d" % (path, nline)
							else:
								print "        %s" % path
				else:
					orphanes[locstrings] += [key]

		norphans = sum([len(orphanes[key]) for key in orphanes])

		if norphans > 0:

			if self.showusage or len(self.__localized) > 0 or len(self.__singlets) > 0:
				print "-------------------------------------------------------------------------------"
			print "[PROBABLY] Orphan strings"

			for locstrings in sorted(orphanes):
				print "-------------------------------------------------------------------------------"
				print locstrings

				for key in sorted(orphanes[locstrings]):
					print "    '%s'" % key

		if len(self.__missings) > 0:

			if self.showusage or norphans > 0 or len(self.__localized) > 0 or len(self.__singlets) > 0:
				print "-------------------------------------------------------------------------------"
			print "[PROBABLY] Missing strings"
			print "-------------------------------------------------------------------------------"

			for mkey in sorted(self.__missings):
				print "    '%s'" % mkey
				for src in self.__missings[mkey]['usage']:
					nline = src[1]
					path = src[0]['path']
					if self.verbose == 0:
						path = os.path.basename(path)

					if nline > 0:
						print "        %s:%d" % (path, nline)
					else:
						print "        %s" % path

# ========================================================================================

def verify(project, verbose = 0, localizers = None, usage = False, notlocalized = False):

	callback = verify_strings(project)
	callback.verbose = verbose
	callback.showusage = usage
	callback.notlocalized = notlocalized
	if localizers != None and len(localizers) > 0:
		callback.localizers = localizers

	try:
		project.process(callback)
	except:
		raise Exception("CLUSTERFUCK[strings]")

	if project.ok:
		callback.postprocess()

	return project.ok

# ========================================================================================
