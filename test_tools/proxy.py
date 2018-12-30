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
import imp
import logging
import os
import signal
import socket
import sys
import threading
import time
import IN

g_server_thread = None

def signal_handler(signal, frame):
    global g_server_thread

    print("Exiting...")
    if g_server_thread:
        g_server_thread.terminate()
        g_server_thread.join()
    print("Done")

class ClientReadThread(threading.Thread):
    """An instance of this class is created for each client connection."""

    def __init__(self, conn, addr, destip, destport, post_file):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.serversocket = None
        self.clientsocket = conn
        self.addr = addr
        self.destip = destip
        self.destport = destport
        self.post_file = post_file
        self.post_module = None
        if os.path.isfile(self.post_file):
            self.post_module = imp.load_source("", self.post_file)

    def terminate(self):
        """Destructor"""
        self.stopped.set()
        if self.serversocket is not None:
            self.serversocket.close()
        self.clientsocket.close()

    def do_packet_processing(self, data, data_len):
        """Executes the packet processing code. This is where the user can specify logic to run for each packet."""
        try:
            if self.post_module is not None:
                data, data_len = self.post_module.process_packet(data, data_len)
        except:
            logging.error("Error processing the packet.")
        return data, data_len

    def copy_data(self, fromsocket, tosocket):
        """Read the next byte and send it to the ultimate destination."""
        data = fromsocket.recv(65536, socket.MSG_PEEK)
        data_len = len(data)
        if data_len > 0:
            data = fromsocket.recv(data_len)
            if self.post_file is not None and len(self.post_file) > 0:
                data, data_len = self.do_packet_processing(data, data_len)
            tosocket.send(data)

    def run(self):
        """Main run loop."""
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.connect((self.destip, self.destport))

        try:
            while not self.stopped.is_set():
                self.copy_data(self.clientsocket, self.serversocket)
                self.copy_data(self.serversocket, self.clientsocket)
        except:
            pass

        self.serversocket.close()
        self.clientsocket.close()

        # Let the server thread know that we're done.
        global g_server_thread
        g_server_thread.remove_client_thread(self)

class ServerProxy(threading.Thread):
    """This class listens for connections from clients and spawns a thread to manage each connection."""

    def __init__(self, bindip, bindport, destip, destport, post_file):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.bindip = bindip
        self.bindport = bindport
        self.destip = destip
        self.destport = destport
        self.proxysocket = None
        self.client_threads = []
        self.client_list_lock = threading.Lock()
        self.post_file = post_file

    def terminate(self):
        """Destructor"""
        self.stopped.set()
        self.join_client_threads()

    def add_client_thread(self, client_thread):
        """Stores a reference to a client read thread."""
        self.client_list_lock.acquire()
        self.client_threads.append(client_thread)
        self.client_list_lock.release()

    def remove_client_thread(self, client_thread):
        """Removes the client read thread from the list of threads."""
        self.client_list_lock.acquire()
        if client_thread in self.client_threads:
            self.client_threads.remove(client_thread)
        self.client_list_lock.release()

    def join_client_threads(self):
        """Joins all the client threads. Helps when shutting the application down cleanly."""
        self.client_list_lock.acquire()
        for client_thread in self.client_threads:
            client_thread.terminate()
            client_thread.join()
        self.client_list_lock.release()

    def run(self):
        """Main run loop."""
        print("Starting a listen thread on " + self.bindip + ":" + str(self.bindport) + ".")
        self.proxysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxysocket.bind((self.bindip, self.bindport))
        self.proxysocket.listen(1)
        self.proxysocket.settimeout(0.2)
        while not self.stopped.is_set():
            try:
                conn, addr = self.proxysocket.accept()
                client_thread = ClientReadThread(conn, addr, self.destip, self.destport, self.post_file)
                client_thread.start()
            except socket.timeout:
                pass
        self.proxysocket.close()
        print("Closed the server listen thread.")

def main():
    global g_server_thread

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindip", default="127.0.0.1", help="Host name on which to bind", required=False)
    parser.add_argument("--bindport", type=int, default=8080, help="Port on which to bind", required=False)
    parser.add_argument("--destip", default="127.0.0.1", help="Host name to which data is sent", required=False)
    parser.add_argument("--destport", type=int, default=8080, help="Port to which data is sent", required=False)
    parser.add_argument("--post", type=str, action="store", default="", help="Post processing code module (optional)", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    g_server_thread = ServerProxy(args.bindip, args.bindport, args.destip, args.destport, args.post)
    g_server_thread.start()

    # Wait for it to finish. We do it like this so that the main thread isn't blocked and can execute the signal handler.
    while g_server_thread.isAlive():
        time.sleep(1)
    g_server_thread.join()

if __name__ == "__main__":
    main()
