# 2012-2014 (c) Unreal Mojo
# by Cyril Murzin

from pbx import pbx
from verify import verify_strings

import os
import sys
import re
import codecs
import subprocess

from clang.cindex import *

# ========================================================================================

class verify_strings_clang(verify_strings.verify_strings):

	stIDLE = 0
	stLOCALIZER = 1
	stARGUMENTS = 2
	stSTRING = 3

	def __init__(self, project):

		verify_strings.verify_strings.__init__(self, project)

		self.cindex = None

#-----------------------------------------------------------------------------------------

	def __iterate_arguments(self, arguments):

		brackets = []
		st = self.stIDLE

		for token in arguments:
			if st == self.stIDLE:
				if token.kind == TokenKind.PUNCTUATION:
					if len(brackets) > 0 and brackets[-1] == token.spelling:
						del brackets[-1]
					elif token.spelling == '(':
						brackets += [')']
					elif token.spelling == '[':
						brackets += [']']
					elif token.spelling == '@':
						st = self.stSTRING
					elif token.spelling == ',':
						if len(brackets) == 0:
							break

			elif st == self.stSTRING:
				if token.kind == TokenKind.LITERAL:
					self._postprocess_string(token.spelling[1:-1], self.__source, self.__nline)
					st = self.stIDLE
				else:
					break


	def __iterate_method(self, node):

		brackets = []
		arguments = []
		st = self.stIDLE

		for token in node.get_tokens():
			if st == self.stIDLE:
				if token.kind == TokenKind.IDENTIFIER:
					for pattern in self.__patterns:
						got = pattern.findall(token.spelling)
						if len(got) > 0:
							self.__nline = token.location.line
							st = self.stLOCALIZER
							break

			elif st == self.stLOCALIZER:
				if token.kind == TokenKind.PUNCTUATION:
					if token.spelling == '(':
						brackets = [')']
						arguments = []
						st = self.stARGUMENTS
					else:
						st = self.stIDLE
				else:
					st = self.stIDLE

			elif st == self.stARGUMENTS:
				if token.kind == TokenKind.PUNCTUATION:
					if brackets[-1] == token.spelling:
						del brackets[-1]
						if len(brackets) == 0:
							self.__iterate_arguments(arguments)
							st = self.stIDLE
					elif token.spelling == '(':
						brackets += [')']
					elif token.spelling == '[':
						brackets += [']']

				if st != self.stIDLE:
					arguments += [token]

	def __iterate_impl(self, node):

		if node.location.file.name == self.__source['path']:
			for child in node.get_children():
				kind = None
				try:
					kind = child.kind
				except:
					continue

				if kind == CursorKind.OBJC_CLASS_METHOD_DECL:
					self.__iterate_method(child)
				elif kind == CursorKind.OBJC_INSTANCE_METHOD_DECL:
					self.__iterate_method(child)


	def __iterate_root(self, node):

		deeper = True
		for child in node.get_children():
			kind = None
			try:
				kind = child.kind
			except:
				continue

			if kind == CursorKind.OBJC_IMPLEMENTATION_DECL:
				self.__iterate_impl(child)
				deeper = False
			elif kind == CursorKind.OBJC_CATEGORY_IMPL_DECL:
				self.__iterate_impl(child)
				deeper = False
			elif deeper:
				self.__iterate_root(child)


	def _analyze_sources(self):

		self.__patterns = []
		for localizer in self.localizers:
			self.__patterns += [re.compile(localizer)]

		for source in self.sources:
			self.__source = source
			tu = self.cindex.parse(None, [source['path'], "-fsyntax-only"], options = 0)

			self.__iterate_root(tu.cursor)


# ========================================================================================

def verify(project, verbose = 0, localizers = None, usage = False, notlocalized = False):

	callback = verify_strings_clang(project)
	callback.verbose = verbose
	callback.showusage = usage
	callback.notlocalized = notlocalized
	if localizers != None and len(localizers) > 0:
		callback.localizers = localizers

	try:
		clang_path = subprocess.check_output(["/usr/bin/xcode-select", "--print-path"]).strip() + "/Toolchains/XcodeDefault.xctoolchain/usr/lib"
		Config.set_library_path(clang_path)

		callback.cindex = Index.create()

	except LibclangError, e:
		print "**************************** CLANG LIBRARY PROBLEM ****************************"
		print str(e)
		print "*******************************************************************************"

		sys.exit(1)

	except:
		print "**************************** NO CLANG LIBRARY FOUND ***************************"
		print "*                                                                             *"
		print "*   Requires installed Apple DevTools (basically Xcode) with libclang.dylib   *"
		print "*                                                                             *"
		print "*******************************************************************************"

		sys.exit(1)

	try:
		project.process(callback)
	except LibclangError, e:
		raise Exception(str(e))
	except:
		raise Exception("CLUSTERFUCK[strings clang]")

	if project.ok:
		callback.postprocess()

	return project.ok

# ========================================================================================
