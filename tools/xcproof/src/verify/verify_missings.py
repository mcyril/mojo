# 2012, 2013 (c) Unreal Mojo
# by Cyril Murzin

from verify import verify_base

import os

# ========================================================================================

class verify_missing(verify_base.verify_base):

	def __init__(self, project):

		verify_base.verify_base.__init__(self, project)

		self.missing = []				# accumulate missing file

		self.showtree = False

	#
	# process one file
	#
	def process(self, key, parentkeys, file, fullpath):

		result = False

		if os.path.exists(fullpath):
			result = True
		else:
			self.missing += [{ 'path':fullpath, 'key':key, 'parentkeys':parentkeys }]

		return result

	#
	# tell iterator that something was wrong
	#
	def ok(self):

		if len(self.missing) == 0:
			return True
		else:
			return False

	#
	# log progress
	#
	def log(self, name, fullpath, level, stcode):
		if self.showtree:
			verify_base.verify_base.log(self, name, fullpath, level, stcode)

#-----------------------------------------------------------------------------------------

	def postprocess(self):

		verify_base.verify_base.postprocess(self)

		if self.showtree:
			print "-------------------------------------------------------------------------------"
		print "* Files processed total: %d" % self.project.nfilesprocessed
		print "* Files verified:        %d" % self.project.nfileschecked
		print "* Files verify failed:   %d" % len(self.missing)

		if not self.ok():
			oldparentkeys = []

			print "* Missing files:"
			for file in self.missing:
				if oldparentkeys != file['parentkeys']:
					self.project.print_path(file['parentkeys'])
					oldparentkeys = file['parentkeys']

				print "*\t%s" % file['path']

# ========================================================================================

def verify(project, verbose = 0, tree = False):

	callback = verify_missing(project)
	callback.verbose = verbose
	callback.showtree = tree

	try:
		project.process(callback)
	except:
		pass # just bypass, 'cause integrity ruined; ok == False

	callback.postprocess()

	return project.ok

# ========================================================================================
