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
import logging
import os
import shutil
import sys
import traceback

def log_error(log_str):
    """Writes an error message to the log file."""
    logger = logging.getLogger()
    logger.error(log_str)

def normjoin(*args):
    return os.path.normpath(os.path.join(*args))

def fix_file_dates(source_file_name, dest_file_name):
    """Sets the destination files creation and modification dates equal to those of the source file."""
    shutil.copystat(source_file_name, dest_file_name)
    print("Fixed dates for " + dest_file_name)

def copy_file(source_file_name, dest_file_name):
    """Copies the source file to the complete path given by the destination file name."""
    print("Copying " + source_file_name + " to " + dest_file_name)
    shutil.copy2(source_file_name, dest_file_name)
    print("Copying done.")

def hash_file(file_to_hash):
    """Computes a SHA-256 hash of the specified file."""
    print("Hashing " + file_to_hash + "...")
    hash_algorithm = hashlib.sha256()
    file = open(file_to_hash, 'rb')
    while True:
        contents = file.read(65536)
        if not contents:
            break
        hash_algorithm.update(contents)
    hash_str = hash_algorithm.hexdigest()
    return hash_str

def compare_dir(source_dir, dest_dir, recurse, sync, fix_dates, report_missing_files, no_hash):
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        # Generate the complete path.
        complete_file_name = os.path.join(source_dir, file_name)

        # File:
        if os.path.isfile(complete_file_name):
            try:
                # Generate the complete paths for the source and destination files.
                source_file_name = os.path.join(source_dir, file_name)
                dest_file_name = os.path.join(dest_dir, file_name)

                # Does the destination file even exist?
                dest_file_exists = os.path.exists(dest_file_name)

                # Are we logging missing files?
                if report_missing_files and dest_file_exists == False:
                    print(dest_file_name + " does not exist.")

                # Are we copying files that are missing or do not match?
                if sync:

                    # Assume we need to copy, try to prove otherwise.
                    needs_to_copy = True

                    # Don't bother hashing if the destination file is missing.
                    if dest_file_exists:

                        # If the no-hash flag was passed then do not compare file hashes.
                        if no_hash == False:

                            # Hash the source and destination files. Since both exist we need to know if they're different.
                            source_hash_str = hash_file(source_file_name)
                            dest_hash_str = hash_file(dest_file_name)
                            needs_to_copy = source_hash_str != dest_hash_str
                            if needs_to_copy:
                                print(source_file_name + " does not match " + dest_file_name)

                        # If the destination file exists and we're not hashing, then don't copy.
                        else:
                            needs_to_copy = False
                    
                    # If the file is missing then print it, even if the report-missing-files flag is False.
                    # This way the user knows why we're copying file file.
                    elif report_missing_files == False:
                        print(dest_file_name + " does not exist.")

                    # Copy the file if the hashes don't match or the destination file doesn't exist.
                    if needs_to_copy:
                        copy_file(source_file_name, dest_file_name)

                # Are we fixing the file dates?
                if fix_dates:
                    fix_file_dates(source_file_name, dest_file_name)
            except:
                log_error("[ERROR] Exception when comparing " + source_file_name + " to " + dest_file_name)
                log_error(traceback.format_exc())
                log_error(sys.exc_info()[0])

        # Dir:
        elif recurse and os.path.isdir(complete_file_name):
            # Generate the complete paths for the source and destination subdirs.
            source_dir_name = os.path.join(source_dir, file_name)
            dest_dir_name = os.path.join(dest_dir, file_name)

            # Recurse.
            compare_dir(source_dir_name, dest_dir_name, recurse, sync, fix_dates, report_missing_files, no_hash)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=str, action="store", default=".", help="Directory from which which files are read", required=True)
    parser.add_argument("--dest-dir", type=str, action="store", default=".", help="Directory to write", required=True)
    parser.add_argument("--recurse", action="store_true", default=True, help="Perform the sync recursively", required=False)
    parser.add_argument("--sync", action="store_true", default=False, help="Without this flag, files will not be copied", required=False)
    parser.add_argument("--fix-dates", action="store_true", default=False, help="Sets the destination files creation and modification dates", required=False)
    parser.add_argument("--report-missing-files", action="store_true", default=False, help="Print missing files to stdout; use without --sync if you just want a report of missing files", required=False)
    parser.add_argument("--no-hash", action="store_true", default=False, help="Prevents file hashing, only missing files will be synchronized", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    # Configure the error logger.
    logging.basicConfig(filename='error.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # Do stuff.
    compare_dir(args.source_dir, args.dest_dir, args.recurse, args.sync, args.fix_dates, args.report_missing_files, args.no_hash)

if __name__ == "__main__":
    main()
