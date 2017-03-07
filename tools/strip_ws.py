#!/usr/bin/python -B

# 2011-2017 (c) Unreal Mojo
# by Cyril Murzin

#
# kind present to Yuriy and Antoxa ;) with friendly excerpt from
# FidoNet Policy Version 4.07 as per June 9, 1989
#
# The FidoNet judicial philosophy can be summed up in two rules:
#
#	1) Thou shalt not excessively annoy others.
#	2) Thou shalt not be too easily annoyed.
#

import os
import sys
import getopt

STRIP_WS_VERSION = "0.0.3.1"

def process_file(path):
	global optApply
	global optForce

	if path.endswith((".m", ".mm", ".c", ".cp", ".cpp", ".cxx", ".h", ".hpp", ".pch", ".py", ".lua", ".inl", ".l", ".ll", ".y", ".yy", ".swift")):
		processed = 0
		npath = path + ".$$$"

		mfin = os.stat(path).st_mode
		fin = open(path, "rU")
		try:
			fout = open(npath, "w+")
			try:
				for line in fin:
					line1 = line.rstrip() + "\n"

					if line != line1:
						processed = processed + 1

					fout.write(line1)

			finally:
				fout.close()
				os.chmod(npath, mfin)

		finally:
			fin.close()

		if optApply and ((processed > 0) or optForce):
			print "stripped %d lines in %s" % (processed, path)
			os.rename(npath, path)
		else:
			if (not optApply) and (processed > 0):
				print "detected %d lines in %s" % (processed, path)
			os.unlink(npath)

	return

def process_dir(path):
	for fn in os.listdir(path):
		if fn.startswith("."):
			continue

		npath = os.path.join(path, fn)

		if os.path.isdir(npath):
			process_dir(npath)
		elif os.path.isfile(npath):
			process_file(npath)

	return

def usage():
	print " ----------------------------------------------------------------------------------"
	print " Source Code Whitespaces Cleaner v%s" % STRIP_WS_VERSION
	print " Copyright 2011-2013 (c) Unreal Mojo, by Cyril Murzin"
	print "                         <<...a bit more than expected>>"
	print " ----------------------------------------------------------------------------------"
	print " Usage: python %s [-a|-f|-h] path" % sys.argv[0]
	print " ----------------------------------------------------------------------------------"
	print "   -h, -?  --help    print this help text"
	print "   -a      --apply   apply changes"
	print "   -f      --force   force file overwrite"
	print " ----------------------------------------------------------------------------------"
	print "  script also normalizes CR/LF for file, use -f to normalize non-strippable files"
	print "  run script with no options to perform detection (without the applying of changes)"
	print " ----------------------------------------------------------------------------------"
	print

def main():
	global optApply
	global optForce

	optApply = False
	optForce = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "afh?", ["apply", "force", "help"])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-a", "--apply"):
			optApply = True
		elif o in ("-f", "--force"):
			optForce = True
		elif o in ("-h", "-?", "--help"):
			usage()
			sys.exit()
		else:
			print "** unhandled option %s **" % o
			usage()
			sys.exit(1)

	if len(args) > 0:
		for path in args:
			if os.path.isdir(path):
				process_dir(path)
			elif os.path.isfile(path):
				process_file(path)
			else:
				print "** %s bad file/directory to process **" % path
	else:
		print "** no file/directory to process, try -h for help **"
		sys.exit(1)

	sys.exit();

if __name__ == "__main__":
    main()
