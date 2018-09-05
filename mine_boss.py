#! /usr/bin/env python

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
import json
import io
import os
import sys
import requests
import signal
import subprocess
import threading
import time
import ConfigParser

g_miner_thread = None
g_stop = False

def signal_handler(signal, frame):
    global g_server_thread
    global g_stop

    print "Exiting..."
    g_stop = True
    if g_miner_thread:
        g_miner_thread.terminate()
        g_miner_thread.join()
    print "Done"

class MinerThread(threading.Thread):
    """An instance of this class runs the miner."""

    def __init__(self, cmd, working_dir):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.cmd = cmd
        self.wd = working_dir

    def terminate(self):
        """Destructor"""
        self.stopped.set()

    def run(self):
        """Main run loop."""
        if self.wd is not None and len(self.wd) > 0:
            print "Changing the working directory..."
            os.chdir(self.wd)
        print "Starting subprocess: " + self.cmd + "..."
        subprocess.call(self.cmd, shell=True)
        print "Subprocess terminated."

def list_coins():
    """Returns a JSON list of coins to mine, in order of profitability."""
    try:
        url = "https://whattomine.com/coins.json"
        r = requests.get(url)
        raw = json.loads(r.content)
        return raw['coins']
    except:
        pass
    return None

def select_coin(config, coins):
    """Select the coin to mine, should be one we have a config entry for."""
    if config is None:
        return
    if coins is None:
        return
    for coin in coins:
        try:
            cmd = config.get(coin, 'cmd')
            if len(cmd) > 0:
                wd = None
                try:
                    wd = config.get(coin, 'working dir')
                except ConfigParser.NoSectionError:
                    pass
                return cmd, wd
        except ConfigParser.NoSectionError:
            pass
    return None, None

def start_miner(cmd, working_dir):
    """Starts the miner thread."""
    global g_miner_thread

    if cmd is None:
        return
    g_miner_thread = MinerThread(cmd, working_dir)
    g_miner_thread.start()

def manage(config):
    """Implements the program logic."""
    global g_miner_thread
    global g_stop

    while not g_stop:
        if g_miner_thread is None or not g_miner_thread.isAlive():
            print "Retrieving coin list..."
            coins = list_coins()
            print "Selecting the coin to mine..."
            cmd, working_dir = select_coin(config, coins)
            print "Starting the miner..."
            start_miner(cmd, working_dir)
        time.sleep(1)

def load_config(config_file_name):
    """Loads the configuration file."""
    with open(config_file_name) as f:
        sample_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))
    return config

def main():
    """Entry point for the cherrypy version of the app."""

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, action="store", default="", help="The configuration file", required=False)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    # Register the signal handler.
    signal.signal(signal.SIGINT, signal_handler)

    # Parse the config file.
    config = load_config(args.config)

    # Select and run a miner.
    manage(config)

if __name__ == "__main__":
    main()
