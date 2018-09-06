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
import hashlib
import os
import sys
import fuzzer

def fuzz_file(fuzz, in_file_name, out_dir):
    """Fuzzes a file once, using the supplied fuzzer instance, and stores the output in the specified directory using the SHA-256 hash as the name."""
    try:
        # Read the file into memory.
        with open(in_file_name, 'rb') as in_file:
            in_contents = in_file.read()

            # Fuzz the contents.
            print "Fuzzing " + in_file_name + "..."
            out_contents, _ = fuzz.fuzz(in_contents, len(in_contents))

            # Hash the contents.
            hash_algorithm = hashlib.sha256()
            hash_algorithm.update(in_contents)
            hash_str = hash_algorithm.hexdigest()

            # Write the output file.
            out_file_name = os.path.join(out_dir, hash_str)
            print "Writing the fuzzed contents to " + out_file_name + "..."
            with open(out_file_name, 'wb') as out_file:
                out_file.write(out_contents)
            print "Done."
    except:
        print "Exception when fuzzing " + in_file_name

def fuzz_dir(fuzz, in_dir, out_dir):
    """Fuzzes all the files in the specified directory, storing the results in the given output directory."""
    for r, d, f in os.walk(in_dir):
        for in_file_name in f:
            in_file_name = os.path.join(r, file)
            fuzz_file(fuzz, in_file_name, out_dir)

def main():
    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-file", default="", help="Name of the file to fuzz", required=False)
    parser.add_argument("--in-dir", default="", help="Name of the directory to fuzz", required=False)
    parser.add_argument("--out-dir", default="", help="Name of the directory to receiving the fuzzed files", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    # Create the fuzzer.
    fuzz = fuzzer.Fuzzer({})

    # Are we fuzzing an individual file?
    if len(args.in_file) > 0:
        fuzz_file(fuzz, args.in_file, args.out_dir)

    # Are we fuzzing a complete directory?
    if len(args.in_dir) > 0:
        fuzz_dir(fuzz, args.in_dir, args.out_dir)

if __name__ == "__main__":
    main()
