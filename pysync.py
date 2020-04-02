#! /usr/bin/env python

# -*- coding: utf-8 -*-
# 
# # MIT License
# 
# Copyright (c) 2020 Mike Simms
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
import hashlib
import os
import shutil
import sys

def normjoin(*args):
    return os.path.normpath(os.path.join(*args))

def fix_file_dates(source_file_name, dest_file_name):
    """Sets the destination files creation and modification dates equal to those of the source file."""
    shutil.copystat(source_file_name, dest_file_name)

def copy_file(source_file_name, dest_file_name):
    """Copies the source file to the complete path given by the destination file name."""
    shutil.copy2(source_file_name, dest_file_name)
    print(source_file_name + " copied to " + dest_file_name)

def hash_file(file_to_hash):
    """Computes a SHA-256 hash of the specified file."""
    hash_algorithm = hashlib.sha256()
    file = open(file_to_hash)
    while True:
        contents = file.read(65536)
        if not contents:
            break
        hash_algorithm.update(contents)
    hash_str = hash_algorithm.hexdigest()
    return hash_str

def compare_dir(source_dir, dest_dir, recurse, sync, fix_dates):
    for root, subdir_names, file_names in os.walk(source_dir):
        for file_name in file_names:
            # Generate the complete paths for the source and destination files.
            source_file_name = os.path.join(source_dir, file_name)
            dest_file_name = os.path.join(dest_dir, file_name)

            # Hash the source file.
            source_hash_str = hash_file(source_file_name)

            # Hash the destination file, if it exists.
            needs_to_copy = True
            dest_hash_str = ""
            if os.path.exists(dest_file_name):
                dest_hash_str = hash_file(dest_file_name)
                needs_to_copy = source_hash_str != dest_hash_str
                if needs_to_copy:
                    print(dest_file_name + " does not match " + source_file_name)
            else:
                print(dest_file_name + " does not exist.")

            # If synchronizing then copy the file.
            if sync and needs_to_copy:
                copy_file(source_file_name, dest_file_name)

            # If fixing dates then do that.
            if fix_dates:
                fix_file_dates(source_file_name, dest_file_name)

        # Do the subdirectories
        if recurse:
            for subdir_name in subdir_names:
                # Generate the complete paths for the source and destination subdirs.
                source_dir_name = os.path.join(source_dir, subdir_name)
                dest_dir_name = os.path.join(dest_dir, subdir_name)

                # Recurse.
                compare_dir(source_dir_name, dest_dir_name, recurse, sync, fix_dates)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=str, action="store", default=".", help="Directory to read", required=True)
    parser.add_argument("--dest-dir", type=str, action="store", default=".", help="Directory to write", required=True)
    parser.add_argument("--recurse", action="store_true", default=True, help="Set to TRUE to perform the sync recursively", required=False)
    parser.add_argument("--sync", action="store_true", default=False, help="Set to TRUE to synchronize the directory", required=False)
    parser.add_argument("--fix-dates", action="store_true", default=False, help="Set to TRUE to set the destination files creation and modification dates", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    compare_dir(args.source_dir, args.dest_dir, args.recurse, args.sync, args.fix_dates)

if __name__ == "__main__":
    main()
