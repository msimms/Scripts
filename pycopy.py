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
import sys
from time import sleep


def copy_file(source_file_name, dest_file_name, slow):
    with open(source_file_name, mode='rb') as source_file:
        with open(dest_file_name, mode='wb') as dest_file:
            while True:
                contents = source_file.read(1024*1024)
                if not contents:
                    print('done')
                    break
                dest_file.write(contents)
                print('.', end='', flush=True)
                if slow:
                    sleep(0.25)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", type=str, action="store", default="", help="File to read", required=True)
    parser.add_argument("--dest-file", type=str, action="store", default="", help="File to write", required=True)
    parser.add_argument("--slow", action="store_true", default=False, help="Makes the copy run slowly; this was just to get around bugs in mac os", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    copy_file(args.source_file, args.dest_file, args.slow)

if __name__ == "__main__":
    main()
