# 2012-2016 (c) Unreal Mojo
# by Cyril Murzin

import sys
import re

# ========================================================================================

STATE_SKIP		= 0
STATE_OK		= 1
STATE_FAIL		= 2
STATE_FOLDER	= 10

PROGRESS_INIT	= 0
PROGRESS_STEP	= 1
PROGRESS_INCS	= 2
PROGRESS_DONE	= 3

PROGRESS		= ["-", "\\", "|", "/"]

# ========================================================================================

class verify_base(object):

	def __init__(self, project):
		self.project = project
		self.verbose = 0
		self.progress_value = 0
		self.progress_total = 0

		self.__WILDCARDS_CACHE_SIZE = 256
		self.__wildcards_cache = {}

	#
	# process one file
	#
	def process(self, key, parentkeys, file, fullpath):
		return True

	#
	# tell iterator that something was wrong
	#
	def ok(self):
		return True

	#
	# show progress
	#
	def progress(self, state, value):
		draw = False
		if state == PROGRESS_INIT:
			self.progress_value = -1
			self.progress_total = value
		elif state == PROGRESS_STEP:
			if value >= self.progress_total:
				self.progress_value = self.progress_total - 1
			else:
				self.progress_value = value
			draw = True
		elif state == PROGRESS_INCS:
			if self.progress_value + value < self.progress_total:
				self.progress_value += value
			draw = True
		elif state == PROGRESS_DONE:
			print '\r', ' ' * 80, '\r',
			sys.stdout.flush()

		if draw:
			value = self.progress_value * 77 / self.progress_total
			total = 77

			done = '#' * (value + 1)
			todo = '.' * (total - value - 1)

			s = '[{0}] '.format(done + todo)
			s = '\r' + s + PROGRESS[self.progress_value % 4] + ' '

			print s,
			sys.stdout.flush()

	#
	# log progress
	#
	def log(self, name, fullpath, level, stcode):

		if stcode == STATE_SKIP:
			status = ""
		elif stcode == STATE_OK:
			status = ""
		elif stcode == STATE_FAIL:
			status = " *FAIL*"
		elif stcode == STATE_FOLDER:
			status = " \\"
		else:
			status = ""

		if level > 0:
			indent = "%%%ds%%s%%s" % (level * 4)
			outstr = indent % (" ", name, status)
		else:
			outstr = "%s%s" % (name, status)

		if self.verbose > 0:
			outstr += " (%s)" % fullpath

		print outstr

	#
	# utilities
	#
	def wildcard(self, format):
		cached = self.__wildcards_cache.get(format)
		if cached != None:
			return cached

		if not hasattr(self, '__format_translate'):
			self.__format_translate = [
				(re.compile(_token), _pattern, _explen)
					for _token, _pattern, _explen in [
						(r'%c',          "(.)",              False),
						(r'%(\d)c',      "(.{%s})",          True),
						(r'%[di]',       "(\d+)",            False),
						(r'%0(\d)[di]',  "(\d{%s})",         True),
						(r'%(\d)[di]',   "(\d{%s})",         True),
						(r'%\.(\d)[di]', "(\d{%s})",         True),
						(r'%u',          "(\d+)",            False),
						(r'%[fgeE]',     "(\d+\.\d+)",       False),
						(r'%s',          "(\S+)",            False),
						(r'%(\d)s',      "(.{%s})",          True),
						(r'%@',          "(\S+)",            False),
						(r'%([xX])',     "(0%s[\dA-Za-f]+)", False),
						(r'%o',          "(0[0-7]*)",        False)
					]]

		st = True	# is pure string
		th = 0		# threshold when not pure string has more than XXX chars
		wc = True	# is pure wildcard
		nc = False	# is pure wildcard with fixed length digits

		format_pattern = ""

		i = 0
		length = len(format)
		while i < length:
			found = None
			for token, pattern, explen in self.__format_translate:
				found = token.match(format, i)

				if found != None:
					st = False
					nc = nc or explen
					groups = found.groupdict() or found.groups()
					if groups:
						pattern = pattern % groups
					format_pattern += pattern
					i = found.end()
					break

			if found == None:
				th += 1
				wc = False
				ch = format[i]
				if ch in "^$()<>[]{}|.*+?\\":
					format_pattern += "\\"
				format_pattern += ch
				i += 1

		if (wc and not nc) or st or (not st and th < 3):
			result = (None, not st, None, None)
		else:
			result = (format_pattern, True, not st, th)

		if len(self.__wildcards_cache) > self.__WILDCARDS_CACHE_SIZE:
			self.__wildcards_cache.clear()
		self.__wildcards_cache[format] = result

		return result

#-----------------------------------------------------------------------------------------

	def _preinitialize(self):
		pass


	def postprocess(self):
		self._preinitialize()

# ========================================================================================
