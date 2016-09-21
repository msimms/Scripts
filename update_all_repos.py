import argparse
import os
import subprocess
import sys

# Parse command line options
parser = argparse.ArgumentParser()
parser.add_argument("--root", type=str, action="store", default="", help="Directory to update, ex: --root src/", required=False)
parser.add_argument("--prune", action="store_true", default=False, help="Prunes local branches not on the remote", required=False)

try:
	args = parser.parse_args()
except IOError as e:
	parser.error(e)
	sys.exit(1)

# If the user provides a path then update the repos in that directory.
# If the user does not provide a path then update the repos in this directory.
if len(args.root) > 0:
	rootdir = os.path.realpath(args.root)
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
			if args.prune:
				subprocess.call(["git", "remote", "prune", "origin"])

		# git mirror
		if os.path.exists(gitHEAD):
			print "Updating git repo at " + subdir
			os.chdir(subdir)
			subprocess.call(["git", "fetch"])
			if args.prune:
				subprocess.call(["git", "remote", "prune", "origin"])

		# svn
		elif os.path.exists(svnDir):
			print "Updating svn repo at " + subdir
			os.chdir(subdir)
			subprocess.call(["svn", "update"])
