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
import signal
import socket
import sys
import threading
import time

g_server_thread = None
g_client_threads = []

def signal_handler(signal, frame):
    global g_server_thread
    global g_client_threads

    print "Exiting..."
    print "Killing the server thread..."
    if g_server_thread:
        g_server_thread.terminate()
        g_server_thread.join()
    print "Killing client read threads..."
    for client_thread in g_client_threads:
        client_thread.terminate()
        client_thread.join()
    print "Done"

class ClientReadThread(threading.Thread):
    """An instance of this class is created for each client connection."""

    def __init__(self, conn, addr, destip, destport):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.serversocket = None
        self.clientsocket = conn
        self.addr = addr
        self.destip = destip
        self.destport = destport

    def terminate(self):
        """Destructor"""
        global g_client_threads

        print "Terminating a client read thread."
        if self in g_client_threads:
            g_client_threads.remove(self)
        self.stopped.set()
        if self.serversocket is not None:
            self.serversocket.close()
        if self.clientsocket is not None:
            self.clientsocket.close()
        print "Done terminating a client read thread."

    def read_client_data(self):
        """Read the next byte and send it to the ultimate destination."""
        try:
            data = self.clientsocket.recv(65536, socket.MSG_PEEK)
            data_len = len(data)
            if data_len > 0:
                data = self.clientsocket.recv(data_len)
                self.serversocket.send(data)
        except:
            self.stopped.set()

    def read_server_data(self):
        """Read the response, if nay, and send it back to the origin."""
        try:
            data = self.serversocket.recv(65536, socket.MSG_PEEK)
            data_len = len(data)
            if data_len > 0:
                data = self.serversocket.recv(data_len)
                self.clientsocket.send(data)
        except:
            self.stopped.set()

    def run(self):
        """Main run loop."""
        global g_client_threads

        print "Starting a client read thread."

        # Connect to the ultimate destination.
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.connect((self.destip, self.destport))

        while not self.stopped.is_set():
            self.read_client_data()
            self.read_server_data()

        if self.serversocket is not None:
            self.serversocket.close()
        if self.clientsocket is not None:
            self.clientsocket.close()

        print "Closed a client read socket."

class ServerProxy(threading.Thread):
    """This class listens for connections from clients and spawns a thread to manage each connection."""

    def __init__(self, bindip, bindport, destip, destport):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.bindip = bindip
        self.bindport = bindport
        self.destip = destip
        self.destport = destport
        self.proxysocket = None

    def terminate(self):
        """Destructor"""
        print "Terminating the server proxy."
        self.stopped.set()
        if self.proxysocket is not None:
            print "Closing the server socket."
            self.proxysocket.close()
        print "Done terminating the server proxy."

    def run(self):
        """Main run loop."""
        print "Starting a listen thread on " + self.bindip + ":" + str(self.bindport) + "."
        self.proxysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxysocket.bind((self.bindip, self.bindport))
        self.proxysocket.listen(1)
        while not self.stopped.is_set():
            conn, addr = self.proxysocket.accept()
            if conn is not None:
                client_thread = ClientReadThread(conn, addr, self.destip, self.destport)
                g_client_threads.append(client_thread) # Register the new thread for signals
                client_thread.start()
        self.proxysocket.close()
        print "Closed the server listen thread."

def main():
    global g_server_thread

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindip", default="127.0.0.1", help="Host name on which to bind", required=False)
    parser.add_argument("--bindport", type=int, default=8080, help="Port on which to bind", required=False)
    parser.add_argument("--destip", default="127.0.0.1", help="Host name to which data is sent", required=False)
    parser.add_argument("--destport", type=int, default=8080, help="Port to which data is sent", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    g_server_thread = ServerProxy(args.bindip, args.bindport, args.destip, args.destport)
    g_server_thread.start()

    # Wait for it to finish. We do it like this so that the main thread isn't blocked and can execute the signal handler.
    while g_server_thread.isAlive():
        time.sleep(1)
    g_server_thread.join()

if __name__ == "__main__":
    main()
