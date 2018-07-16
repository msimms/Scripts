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
import socket
import sys
import threading
import time

g_server_thread = None

def signal_handler(signal, frame):
    global g_server_thread

    if g_server_thread:
        g_server_thread.terminate()

class ClientReadThread(threading.Thread):
    """An instance of this class is created for each client connection."""

    def __init__(self, conn, addr, destip, destport):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.destip = destip
        self.destport = destport

    def run(self):
        """Main run loop."""
        data = self.conn.recv(10)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.destip, self.destport))
        s.send(data)
        s.close()
        self.conn.close()

class ServerProxy(threading.Thread):
    """This class listens for connections from clients and spawns a thread to manage each connection."""

    def __init__(self, sourceip, sourceport, destip, destport):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.sourceip = sourceip
        self.sourceport = sourceport
        self.destip = destip
        self.destport = destport

    def terminate(self):
        """Destructor"""
        print "Terminating"
        self.stopped.set()

    def run(self):
        """Main run loop."""
        print "Starting a listen thread on " + self.host + ":" + str(self.port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.sourceip, self.sourceport))
        while not self.stopped.wait(10):
            s.listen(1)
            conn, addr = s.accept()
            client_thread = ClientReadThread(conn, addr, self.destip, self.destport)
            client_thread.start()
        s.close()

def main():
    global g_server_thread

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--sourceip", default="127.0.0.1", help="Host name on which to bind", required=False)
    parser.add_argument("--sourceport", type=int, default=8080, help="Port on which to bind", required=False)
    parser.add_argument("--destip", default="127.0.0.1", help="Host name to which data is sent", required=False)
    parser.add_argument("--destport", type=int, default=8080, help="Port to which data is sent", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    g_server_thread = ServerProxy(args.sourceip, args.sourceport, args.destip, args.destport)
    g_server_thread.start()

    # Wait for it to finish. We do it like this so that the main thread isn't blocked and can execute the signal handler.
    while g_server_thread.isAlive():
        time.sleep(1)
    g_server_thread.join()

if __name__ == "__main__":
    main()
