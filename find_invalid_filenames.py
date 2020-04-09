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
import os
import re
import sys

valid_zfs_file_name  = re.compile(r"^[\s\.\:\_\-\*\,a-zA-Z0-9]+") # Source https://unix.stackexchange.com/questions/23569/allowed-and-safe-characters-for-zfs-filesystem-in-freebsd
valid_fat_file_name  = re.compile(r"^[\s\.\_\$\%\@\~\!\(\)\{\}\^\+\-\,\;\=\[\]\#\&a-zA-Z0-9]+") # Matches long FAT file names, source http://averstak.tripod.com/fatdox/names.htm
valid_ntfs_file_name = re.compile(r"^[\s\.\:\_\$\%\@\~\!\/\(\)\{\}\^\+\-\,\;\=\[\]\#\&a-zA-Z0-9]+")
valid_hfs_file_name  = re.compile(r"^[\s\.\_\$\%\@\~\!\\\/\(\)\{\}\^\+\-\,\;\=\[\]\#\&a-zA-Z0-9]+")

def search_dir(dir, recurse, zfs, fat, ntfs, hfs):
    for file_name in os.listdir(dir):

        # Generate the complete path.
        complete_file_name = os.path.join(dir, file_name)

        # Check for validity.
        if zfs:
            matched = re.match(valid_zfs_file_name, file_name)
            if matched is None or matched.group() != file_name:
                print(complete_file_name + " is invalid for ZFS.")
        if fat:
            matched = re.match(valid_fat_file_name, file_name)
            if matched is None or matched.group() != file_name:
                print(file_name + " is invalid for FAT.")
        if ntfs:
            matched = re.match(valid_ntfs_file_name, file_name)
            if matched is None or matched.group() != file_name:
                print(complete_file_name + " is invalid for NTFS.")
        if hfs:
            matched = re.match(valid_hfs_file_name, file_name)
            if matched is None or matched.group() != file_name:
                print(complete_file_name + " is invalid for HFS.")

        # Dir:
        if recurse and os.path.isdir(complete_file_name):
            search_dir(os.path.join(dir, file_name), recurse, zfs, fat, ntfs, hfs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, action="store", default=".", help="Directory in which to search", required=True)
    parser.add_argument("--recurse", action="store_true", default=True, help="Perform the sync recursively", required=False)
    parser.add_argument("--zfs", action="store_true", default=False, help="Print files containing invalid characters incompatible with the ZFS file system", required=False)
    parser.add_argument("--fat", action="store_true", default=False, help="Print files containing invalid characters incompatible with the FAT file system", required=False)
    parser.add_argument("--ntfs", action="store_true", default=False, help="Print files containing invalid characters incompatible with the NTFS file system", required=False)
    parser.add_argument("--hfs", action="store_true", default=False, help="Print files containing invalid characters incompatible with the HFS file system", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    if args.zfs or args.fat or args.ntfs or args.hfs:
        search_dir(args.dir, args.recurse, args.zfs, args.fat, args.ntfs, args.hfs)
    else:
        print("No file system formats were specified.")

if __name__ == "__main__":
    main()
