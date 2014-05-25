#!/usr/bin/python -O -OO

# 2012-2014 (c) Unreal Mojo
# by Cyril Murzin

import os
import sys
import getopt

from pbx import pbx
from verify import verify_missings
from verify import verify_images
from verify import verify_strings
from verify import verify_strings_clang

from plist import plistReader

CXPROOF_VERSION = "0.0.4"

# ========================================================================================

def usage():
	print " ----------------------------------------------------------------------------------"
	print " XCode project PROOFing tool v%s" % CXPROOF_VERSION
	print "   Copyright 2012-2014 (c) Unreal Mojo, by Cyril Murzin"
	print "                           <<...a bit more than expected>>"
	print " Portions acknowledged from"
	print "   mergepbx / ASCII plist access; copyright (c) Simon Wagner"
	print "   biplist / Binary plist access; copyright (c) Andrew Wooster"
	print "   six / biplist dependance; copyright (c) 2010-2013 Benjamin Peterson"
	print " ----------------------------------------------------------------------------------"
	print " Usage: python %s [options] <xcode-project-path>" % sys.argv[0]
	print " ----------------------------------------------------------------------------------"
	print "  -h, -?  --help   print this help text"
	print "  -v               verbose mode (also show full paths)"
	print
	print " ----------------------------------------------------------------------------------"
	print " * integrity check pass (always enabled, running first)"
	print
	print " * pass tweaks:"
	print "     --tree        show project files tree"
	print " ----------------------------------------------------------------------------------"
	print " * images analysis pass"
	print
	print "  -i               enable pass (verify project for orphan/missing image files)"
	print
	print " * pass tweaks:"
	print "     --imap        show image usage map"
	print "     --ibundles    check enclosed bundles' contents"
	print " ----------------------------------------------------------------------------------"
	print " * strings analysis pass"
	print
	print "  -s               enable pass (verify project for localized strings problems)"
	print
	print " * pass tweaks:"
	print "     --sclang      use libclang as source code parser (SLOW!)"
	print "     --smap        show strings usage map"
	print "     --non-localized"
	print "                   show possible non-localized strings"
	print "     --localizer=..."
	print "                   alternative localizer function name (regexp & multiple allowed)"
	print "     --localizer-prefix=..."
	print "                   alternative localizer function name prefix (multiple allowed)"
	print " ----------------------------------------------------------------------------------"
	print

def main():

	verbose = 0

	checkIntegrity = True
	checkIntegrityTree = False

	checkImages = False
	checkImagesMap = False
	checkImagesBundles = False

	checkStrings = False
	checkStringsClang = False
	checkStringsLocalizers = []
	checkStringsMap = False
	checkStringsNonLocalized = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "h?vis", ["help", "verbose", "tree", "images", "imap", "ibundles", "strings", "smap", "non-localized", "localizer=", "localizer-prefix=", "sclang"])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-h", "-?", "--help"):
			usage()
			sys.exit()
		elif o in ("-v", "--verbose"):
			verbose += 1
		elif o == "--tree":
			checkIntegrityTree = True
		elif o in ("-i", "--images"):
			checkImages = True
		elif o == "--imap":
			checkImagesMap = True
		elif o == "--ibundles":
			checkImagesBundles = True
		elif o in ("-s", "--strings"):
			checkStrings = True
		elif o == "--sclang":
			checkStringsClang = True
		elif o == "--smap":
			checkStringsMap = True
		elif o == "--non-localized":
			checkStringsNonLocalized = True
		elif o == "--localizer":
			checkStringsLocalizers += [a]
		elif o == "--localizer-prefix":
			checkStringsLocalizers += [a + "[^\(]*"]
		else:
			print "** unhandled option %s **" % o
			usage()
			sys.exit(1)

	if len(args) > 0:
		for path in args:

			while path.endswith('/'):
				path = path[:-1]

			if len(args) > 1:
				prefix = "** %s: " % path
			else:
				prefix = "** "

			pbxproj = None

 			fin = None

			try:
 				pbxproj = plistReader(path + "/project.pbxproj").read()
				if pbxproj == None:
					raise Exception("corrupted project")

				pathdir = os.path.dirname(path)
				if len(pathdir) == 0:
					pathdir = "./"

				project = pbx.pbx(pbxproj, pathdir)

				print "==============================================================================="
				print "Verifying project %s" % path
				print "-------------------------------------------------------------------------------"

				if checkIntegrity and not verify_missings.verify(project, verbose, tree = checkIntegrityTree):
					print "%sIntegrity check failed" % prefix
				else:
					print "%sProject is intact" % prefix

					if checkImages:
						print "==============================================================================="
						verify_images.verify(project, verbose, usage = checkImagesMap, bundles = checkImagesBundles)

					if checkStrings:
						print "==============================================================================="
						if checkStringsClang:
							verify_strings_clang.verify(project, verbose, localizers = checkStringsLocalizers, usage = checkStringsMap, notlocalized = checkStringsNonLocalized)
						else:
							verify_strings.verify(project, verbose, localizers = checkStringsLocalizers, usage = checkStringsMap, notlocalized = checkStringsNonLocalized)

				print "==============================================================================="

			except Exception, e:
				print "%sIntegrity check failed: %s" % (prefix, e.message)

	else:
		print "** no project file to process, try -h for help **"
		sys.exit(1)

# ========================================================================================

if __name__ == "__main__":
	main()
