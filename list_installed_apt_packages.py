#! /usr/bin/env python

# MIT License
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
"""This script looks through the apt log files for packages that were manually installed."""
"""It's a quick hack for getting the installed package list while ignoring dependencies."""

import gzip
import os
import subprocess

COMMANDLINE_STR = "Commandline"
INSTALL_STR = "install "

install_packages = []

# Look through the log file data for install commands.
def parse_log_file_data(log_data):
    log_str = str(log_data)
    line_data = log_str.split("\\n")
    for line in line_data:
        if line.find(COMMANDLINE_STR) == 0:
            install_offset = line.find(INSTALL_STR)
            if install_offset > 0:
                package = (line[install_offset + len(INSTALL_STR):])
                if not package in install_packages: # De-dupe
                    install_packages.append(package)

# List all the apt log files.
apt_log_path = '/var/log/apt/'
results = subprocess.run(['ls', apt_log_path], stdout=subprocess.PIPE)
results_str = str(results.stdout)
for file_path in results_str.split("\\n"):
    if file_path.find("history.log") == 0:
        split_path = os.path.splitext(file_path)

        # Read and parse the gzipped log data.
        if split_path[1] == '.gz':
            with gzip.open(os.path.join(apt_log_path, file_path), 'rb') as f:
                file_contents = f.read()
                parse_log_file_data(file_contents)

        # Read and parse the log data.
        elif split_path[1] == '.log':
            with open(os.path.join(apt_log_path, file_path), 'rb') as f:
                file_contents = f.read()
                parse_log_file_data(file_contents)

# Pretty print the result.
for package in install_packages:
    print(package)
