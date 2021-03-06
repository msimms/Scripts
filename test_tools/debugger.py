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

from subprocess import Popen, PIPE
import argparse
import time
import pydbg
import sys

def breakpoint_handler(pydbg):
   if pydbg.first_breakpoint:
      return pydbg.defines.DBG_CONTINUE

   context = dbg.get_thread_context(dbg.h_thread)
   print "eip = %08x" % context.Eip
   print "edi = %08x" % context.Edi
   return pydbg.defines.DBG_CONTINUE

def debug_process(file_name):
    dbg = pydbg.pydbg()
    dbg.set_callback(pydbg.defines.EXCEPTION_BREAKPOINT, breakpoint_handler)
    dbg.load(file_name)
    dbg.resume_all_threads()
    pydbg.debug_event_loop(dbg)

def launch_proc(file_name):
    try:
        running_procs = [
            Popen([file_name], stdout=PIPE, stderr=PIPE)
        ]

        while running_procs:
            for proc in running_procs:
                retcode = proc.poll()
                if retcode is not None:
                    running_procs.remove(proc)
                    break
                else:
                    time.sleep(0.1)

        if retcode != 0:
            pass
    except:
        pass

def main():
    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="/Applications/Calculator.app/Contents/MacOS/Calculator", help="Name of the file to debug", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
