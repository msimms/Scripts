#! /usr/bin/env python

# -*- coding: utf-8 -*-
# 
# # MIT License
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

def read_entire_file(file_name):
    """Reads an entire file."""
    result = ""
    with open(file_name, 'rt') as local_file:
        while True:
            next_block = local_file.read(8192)
            if not next_block:
                break
            result = result + next_block
    return result

def write_entire_file(file_name, data):
    """Writes a file."""
    with open(file_name, 'wt') as local_file:
        local_file.write(data)

def process_file(file_name, trailing_whitespace):
    """Performs the specified modifications to the file with the given name, overwriting it in the process."""
    file_contents = read_entire_file(file_name)
    file_lines = file_contents.split('\n')
    new_file_contents = ""
    for line in file_lines:
        if trailing_whitespace:
            new_line = line.rstrip(' \t')
        else:
            new_line = line
        new_file_contents = new_file_contents + new_line + '\n'
    new_file_contents = new_file_contents + '\n'
    write_entire_file(file_name, new_file_contents)

def process_dir(dir_name, trailing_whitespace):
    """Performs the specified modifications to every file in the directory with the given name, overwriting them in the process."""
    for root, directories, filenames in os.walk(dir_name):
        for filename in filenames:
            process_file(os.path.join(root, filename), trailing_whitespace)

def main():
    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="", help="", required=False)
    parser.add_argument("--dir", default="", help="", required=False)
    parser.add_argument("--trailing-whitespace", action="store_true", default=False, help="Remove trailing whitespace", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    if len(args.file) > 0:
        process_file(args.file, args.trailing_whitespace)
    if len(args.dir) > 0:
        process_dir(args.dir, args.trailing_whitespace)

if __name__ == "__main__":
    main()
