#  MIT License
#
#  Copyright (c) 2018 Michael J Simms. All rights reserved.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import argparse
import time
import os
import platform
import subprocess
import sys
from slackclient import SlackClient


def post_message(slack_client, channel_id, my_name, msg):
    """Post the given message to the slack channel."""
    slack_client.api_call("chat.postMessage", channel=channel_id, text=my_name + " " + msg)

def do_command(slack_client, channel_id, my_name, command):
    """Parse and execute the specified command."""
    print "Received command: " + command
    result = subprocess.check_output(command, shell=True)
    post_message(slack_client, channel_id, my_name, result)

def listen_for_commands(api_token, channel_id):
    """Listen on the specified channel for commands that begin with the computer's host name."""
    slack_client = SlackClient(api_token)
    if slack_client.rtm_connect(with_team_state=False):

        # Connected.
        print "The bot is connected to Slack."

        # What name will we listen for?
        my_name = platform.node()
        my_name = my_name.replace('.local', '')
        print "The bot will listen for commands that start with: " + my_name

        # Read bot's user ID by calling Web API method `auth.test`
        _ = slack_client.api_call("auth.test")["user_id"]
        while True:
            slack_events = slack_client.rtm_read()
            for event in slack_events:
                if event["type"] == "message" and event["channel"] == channel_id and not "subtype" in event:
                    text = event["text"]
                    if text.startswith(my_name):
                        command = text.replace(my_name, '').lstrip()
                        do_command(slack_client, channel_id, my_name, command)
            time.sleep(1)

    else:
        print "Failed to connect the bot to Slack."

def main():
    """Entry point for the cherrypy version of the app."""

    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-token", type=str, action="store", default="", help="The API token to use.", required=True)
    parser.add_argument("--channel-id", type=str, action="store", default="", help="The channel ID of the channel to use.", required=True)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    listen_for_commands(args.api_token, args.channel_id)

if __name__ == "__main__":
    main()
