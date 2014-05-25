# 2012-2014 (c) Unreal Mojo
# by Cyril Murzin

from pbx import pbx
from verify import verify_base
from plist import plistReader

import os
import re
import codecs
import subprocess

from xml.dom import minidom

# ========================================================================================

class verify_images(verify_base.verify_base):

	def __init__(self, project):

		verify_base.verify_base.__init__(self, project)

		self.extension = ".png"	# exactly with leading dot
		self.suffix = "@2x"

		self.sources = []
		self.xibs = []
		self.plists = []
		self.htmls = []

		self.images = []

	#	self.headers = False	# do [not] bypass headers
		self.showusage = False
		self.bundles = False

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
			elif typ.startswith("image.") and file['path'].endswith(self.extension):
				self.images += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys, 'bundled':False }]
			elif typ.startswith("text.plist.") and typ != "text.plist.strings":
				self.plists += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]
			elif typ == "file.xib":
				self.xibs += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]
			elif typ == "text.html":
				self.htmls += [{ 'file':file, 'path':fullpath, 'type':typ, 'key':key, 'parentkeys':parentkeys }]
			elif self.bundles and typ == "wrapper.plug-in":
				bundle = pbx._pbx_bundle(fullpath)
				for item in bundle.list_with_ext(self.extension):
					self.images += [{ 'file': { 'path':file['path'] + item }, 'path':fullpath + item, 'type':"image" + self.extension, 'key':key, 'parentkeys':parentkeys, 'bundled':True }]

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

#-----------------------------------------------------------------------------------------

	#
	# private methods
	#

	def wildcard(self, str):
		result = verify_base.verify_base.wildcard(self, str)
		if result[0] == None:
			pass
		elif result[2]:
			if len(self.suffix) > 0 and result[0].find(self.suffix) >= 0:
				th = result[2] - len(self.suffix)
				if th < 3:
					result = (None, result[1], None, None)

		return result


	def __safe_append_to_(self, imgstate, image, source, nline):

		if not image in imgstate:
			imgstate[image] = dict([('usage', [(source, nline)])])
		else:
			usage = imgstate[image]['usage']

			if nline == 0:
				for use in usage:
					if use[0] == source:
						return

			usage += [(source, nline)]


	def _postprocess_image(self, base, hasext, source, nline = 0, allowre = False):

		found = False
		if base + self.extension in self.__imagesmap:
			self.__safe_append_to_(self.__imagesmap, base + self.extension, source, nline)
			found = True
		if len(self.suffix) > 0 and not base.endswith(self.suffix) and base + self.suffix + self.extension in self.__imagesmap:
			self.__safe_append_to_(self.__imagesmap, base + self.suffix + self.extension, source, nline)
			found = True

		haswild = False

		if allowre and not found:
			wildcard, haswild, dummy1, dummy2 = self.wildcard(base)
			if wildcard != None:
				if len(self.suffix) > 0:
					wildpat = re.compile("^" + wildcard + ("(%s)*\\%s$" % (self.suffix, self.extension)))
				else:
					wildpat = re.compile("^" + wildcard + ("\\%s$" % self.extension))
				founds = [s for s in self.__imagesmap.keys() if wildpat.match(s) != None]

				for image in founds:
					self.__safe_append_to_(self.__imagesmap, image, source, nline)
					found = True

		if not found and not haswild and hasext:
			self.__safe_append_to_(self.__missings, base + self.extension, source, nline)

		return found


	def _postprocess_sources(self):

		objcstrpat = re.compile(r"@\"(([^\"\\]|\\.)*)\"")

		for source in self.sources:
			fin = codecs.open(source['path'], "rU", encoding = pbx._pbx_file_encoding(source))
			try:
				nline = 1

				for line in fin:
					got = objcstrpat.findall(line)
					for one in got:
						hasext = False
						if one[0].endswith(self.extension):
							base = one[0][:-4]
							hasext = True
						else:
							base = one[0]

						self._postprocess_image(base, hasext, source, nline, True)

					nline += 1

			except:
				pass

			finally:
				fin.close()


	def _postprocess_xibs(self):

		for xib in self.xibs:
			xibdoc = minidom.parse(xib['path'])
			xibstrings = xibdoc.getElementsByTagName("string")

			for xibstring in xibstrings:
				if xibstring.hasAttribute("key") and xibstring.attributes['key'].value == "NSResourceName":
					children = xibstring.childNodes
					if len(children) == 1 and children[0].nodeType == minidom.Node.TEXT_NODE:
						if children[0].nodeValue.endswith(self.extension):
							self._postprocess_image(children[0].nodeValue[:-4], True, xib)


	def _postprocess_plist_item(self, item, plist):
		if hasattr(item, "iteritems"):
			for key in item:
				self._postprocess_plist_item(item[key], plist)
		elif hasattr(item, "__iter__"):
			for elt in item:
				self._postprocess_plist_item(elt, plist)
		elif isinstance(item, basestring):
			hasext = False
			if item.endswith(self.extension):
				base = item[:-4]
				hasext = True
			else:
				base = item

			self._postprocess_image(base, hasext, plist)


	def _postprocess_plists(self):

		for plist in self.plists:
			root = None

			try:
 				root = plistReader(plist['path']).read()
			except:
				pass

			if root != None:
				self._postprocess_plist_item(root, plist)


	def _postprocess_htmls(self):

		htmltagpat = re.compile(r"(?i)<\/?\w+((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>")
		htmlsrcpat = re.compile(r"src=[\"'](([^\"\\]|\\.)*)[\"']")

		for html in self.htmls:
			fin = codecs.open(html['path'], "rU", encoding = pbx._pbx_file_encoding(html))
			try:
				htmlstr = fin.read()

				for htmltag in htmltagpat.finditer(htmlstr):
					tag = repr(htmltag.group())

					if tag.startswith("<img"):
						got = htmlsrcpat.findall(tag)
						for one in got:
							print one[0] # TODO
							break

			except:
				pass

			finally:
				fin.close()

#-----------------------------------------------------------------------------------------

	def postprocess(self):

		verify_base.verify_base.postprocess(self)

		self.__imagesmap = {}
		self.__missings = {}

		for image in self.images:
			if image['bundled']:
				self.__imagesmap[image['file']['path']] = dict(image.items() + [('usage', [])])
			else:
				self.__imagesmap[os.path.basename(image['path'])] = dict(image.items() + [('usage', [])])

		# fill images usage in source files
		self._postprocess_sources()

		# fill images usage in xib files
		self._postprocess_xibs()

		# fill images usage in plist files
		self._postprocess_plists()

		# fill images usage in html files
		self._postprocess_htmls()

		if self.showusage:
			print "[PROBABLY] Usage of image files(%s) statistics" % self.extension
			print "-------------------------------------------------------------------------------"

		orphanes = []

		# process statistics
		for key in sorted(self.__imagesmap):
			imgstate = self.__imagesmap[key]

			if len(imgstate['usage']) > 0:
				if self.showusage:
					print key

					for src in imgstate['usage']:
						nline = src[1]
						path = src[0]['path']
						if self.verbose == 0:
							path = os.path.basename(path)

						if nline > 0:
							print "    %s:%d" % (path, nline)
						else:
							print "    %s" % path
			else:
				orphanes += [imgstate]

		if len(orphanes) > 0:

			if self.showusage:
				print "-------------------------------------------------------------------------------"
			print "[PROBABLY] Orphan image files(%s)" % self.extension
			print "-------------------------------------------------------------------------------"

			for orphan in orphanes:
				if self.verbose == 0:
					if orphan['bundled']:
						print orphan['file']['path']
					else:
						print os.path.basename(orphan['path'])
				else:
					print orphan['path']

		if len(self.__missings) > 0:

			if self.showusage or len(orphanes) > 0:
				print "-------------------------------------------------------------------------------"
			print "[PROBABLY] Missing image files(%s)" % self.extension
			print "-------------------------------------------------------------------------------"

			for mkey in sorted(self.__missings):
				print mkey
				for src in self.__missings[mkey]['usage']:
					nline = src[1]
					path = src[0]['path']
					if self.verbose == 0:
						path = os.path.basename(path)

					if nline > 0:
						print "    %s:%d" % (path, nline)
					else:
						print "    %s" % path

# ========================================================================================

def verify(project, verbose = 0, usage = False, bundles = False):

	callback = verify_images(project)
	callback.verbose = verbose
	callback.showusage = usage
	callback.bundles = bundles

	try:
		project.process(callback)
	except:
		raise Exception("CLUSTERFUCK [images]")

	if project.ok:
		callback.postprocess()

	return project.ok

# ========================================================================================
