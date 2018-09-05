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
import platform
import random
import requests
import signal
import subprocess
import threading
import time
import ConfigParser

TASK_BEST_COIN = "Best Coin"

g_task_thread = None
g_stop = False

def signal_handler(signal, frame):
    global g_server_thread
    global g_stop

    print "Exiting..."
    g_stop = True
    if g_task_thread:
        g_task_thread.terminate()
        g_task_thread.join()
    print "Done"

def post_to_slack(config, message):
    """Post a message to the the slack channel specified in the configuration file."""
    try:
        key = config.get('Slack', 'key')
        channel = config.get('Slack', 'channel')

        from slacker import Slacker
        slack = Slacker(key)
        slack.chat.post_message(channel, message)
    except ConfigParser.NoOptionError:
        pass
    except ConfigParser.NoSectionError:
        pass
    except ImportError:
        print "Failed ot import Slacker. Cannot post to Slack. Either install the module or remove the Slack section from the configuration file."
    except:
        pass

class TaskThread(threading.Thread):
    """An instance of this class runs a subprocess."""

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

def select_task(config):
    """Selects the next task, based on the rules in the configuration file."""
    task = TASK_BEST_COIN # The default task
    try:
        task_list_str = config.get('General', 'tasks')
        task_list = task_list_str.split(',')
        task = task_list[random.randint(0, len(task_list) - 1)]
    except ConfigParser.NoOptionError:
        pass
    except ConfigParser.NoSectionError:
        pass
    return task

def get_task_cmd(config, task):
    """Returns the command to run the specified task."""
    try:
        cmd = config.get(task, 'cmd')
        if len(task) > 0:
            wd = None
            try:
                wd = config.get(task, 'working dir')
            except ConfigParser.NoSectionError:
                pass
            return cmd, wd
    except ConfigParser.NoOptionError:
        print "Command line not specified for " + task + "."
    except ConfigParser.NoSectionError:
        print "Section not specified for " + task + "."
    return None, None

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
        cmd, wd = get_task_cmd(config, coin)
        if cmd is not None:
            return cmd, wd
    return None, None

def start_task(config, cmd, working_dir):
    """Starts the miner thread."""
    global g_task_thread

    if cmd is None:
        return
    
    post_to_slack(config, "Starting " + cmd + " on " + platform.node() + ".")
    g_task_thread = TaskThread(cmd, working_dir)
    g_task_thread.start()

def manage(config):
    """Implements the program logic."""
    global g_task_thread
    global g_stop

    cmd = None
    working_dir = None

    while not g_stop:
        if g_task_thread is None or not g_task_thread.isAlive():
            print "Selecting task..."
            task = select_task(config)
            if task == TASK_BEST_COIN:
                print "Retrieving coin list..."
                coins = list_coins()
                print "Selecting the coin to mine..."
                cmd, working_dir = select_coin(config, coins)
            else:
                cmd, working_dir = get_task_cmd(config, task)
            if cmd is not None and len(cmd) > 0:
                print "Starting the task..."
                start_task(config, cmd, working_dir)
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
