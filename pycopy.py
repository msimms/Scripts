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
import sys
from time import sleep


def copy_file(source_file_name, dest_file_name, slow):
    """Mac OS sometimes sucks with network drives. After trying numerous other methods to fix this, I just wrote a 'slow' copy that writes the file in 1 MB chunks."""

    # Has the file already been (partially) copied?
    offset = os.path.getsize(dest_file_name)

    # Copy the rest of the file.
    with open(source_file_name, mode='rb') as source_file:

        # Skip past any part that we've already copied.
        source_file.seek(offset, 0)

        # Copy the rest.
        done = False
        while not done:
            with open(dest_file_name, mode='ab') as dest_file:
                # Read.
                contents = source_file.read(1024*1024)
                if not contents:
                    print('done')
                    done = True
                    break

                # Write.
                dest_file.write(contents)

                # Flush all the buffers.
                source_file.flush()
                dest_file.flush()

                # Print something so we know it's still working.
                print('.', end='', flush=True)

                # Slow mode.
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
