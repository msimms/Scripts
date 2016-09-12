import os
import subprocess
import sys

# If the user provides a path then update the repos in that directory.
# If the user does not provide a path then update the repos in this directory.
if len(sys.argv) >= 2:
	rootdir = os.path.realpath(sys.argv[1])
else:
	rootdir = os.path.dirname(os.path.realpath(__file__))

# Loop through the top level directories and update git and svn repos, including git mirrors.
for filename in os.listdir(rootdir):
	subdir = os.path.join(rootdir, filename)
	if os.path.isdir(subdir):
		gitDir = os.path.join(subdir, '.git')
		gitHEAD = os.path.join(subdir, 'HEAD')
		svnDir = os.path.join(subdir, '.svn')

		# git repo
		if os.path.exists(gitDir):
			print "Updating git repo at " + subdir
			os.chdir(subdir)
			subprocess.call(["git", "pull"])

		# git mirror
		if os.path.exists(gitHEAD):
			print "Updating git repo at " + subdir
			os.chdir(subdir)
			subprocess.call(["git", "fetch"])

		# svn
		elif os.path.exists(svnDir):
			print "Updating svn repo at " + subdir
			os.chdir(subdir)
			subprocess.call(["svn", "update"])
