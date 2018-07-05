# MIT License
# 
# Copyright (c) 2018 Mike Simms
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import os
import subprocess
import sys


def update_dir(args, dir_name):
    """Processes the specified directory, recursively if necessary."""

    try:
        for filename in os.listdir(dir_name):
            subdir = os.path.join(dir_name, filename)
            if os.path.isdir(subdir):
                git_dir = os.path.join(subdir, '.git')
                git_head = os.path.join(subdir, 'HEAD')
                svn_dir = os.path.join(subdir, '.svn')

                # git repo
                if os.path.exists(git_dir):
                    print "Updating git repo at " + subdir
                    os.chdir(subdir)
                    subprocess.call(["git", "pull"])
                    if args.prune:
                        subprocess.call(["git", "remote", "prune", "origin"])

                # git mirror
                elif os.path.exists(git_head):
                    print "Updating git mirror at " + subdir
                    os.chdir(subdir)
                    subprocess.call(["git", "fetch"])
                    if args.prune:
                        subprocess.call(["git", "remote", "prune", "origin"])

                # svn
                elif os.path.exists(svn_dir):
                    print "Updating svn repo at " + subdir
                    os.chdir(subdir)
                    subprocess.call(["svn", "update"])

                # recurse?
                elif args.recurse:
                    print "Recursing into " + subdir
                    update_dir(args, subdir)
    except OSError as exception:
        print exception


def main():
    """Function-ified entry point for the program."""

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=str, action="store", default="",
                        help="Directory to update, ex: --root src/", required=False)
    parser.add_argument("--prune", action="store_true", default=False,
                        help="Prunes local branches not on the remote", required=False)
    parser.add_argument("--recurse", action="store_true", default=False,
                        help="Recurses subdirectories, looking for more repos", required=False)

    try:
        args = parser.parse_args()
    except IOError as exception:
        parser.error(exception)
        sys.exit(1)

    # If the user provides a path then update the repos in that directory.
    # If the user does not provide a path then update the repos in this directory.
    if len(args.root) > 0:
        rootdir = os.path.realpath(args.root)
    else:
        rootdir = os.path.dirname(os.path.realpath(__file__))

    # Loop through the top level directories and update git and svn repos, including git mirrors.
    update_dir(args, rootdir)


if __name__ == "__main__":
    main()
