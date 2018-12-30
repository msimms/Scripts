# -*- coding: utf-8 -*-
# 
# # MIT License
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
import fuzzer
import sys

from scapy.all import *
from scapy.utils import rdpcap

def read_packets_from_file(file_name):
    return rdpcap(file_name)

def inject_packets(packets, src_mac, dst_mac, src_ip, dst_ip):
    for packet in packets:
        packet[Ether].src = src_mac
        packet[Ether].dst = dst_mac
        packet[IP].src = src_ip
        packet[IP].dst = dst_ip
        sendp(packet)

def main():
    # Parse command line options.
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="packets.pcap", help="Pcap file from which to source packets", required=True)
    parser.add_argument("--fuzz", action="store_true", default=False, help="Applies the packet fuzzer", required=False)
    parser.add_argument("--iterations", type=int, default=1, help="The number of times to replay the data", required=False)
    parser.add_argument("--src-mac", default="00:00:00:00:00:00", help="New source MAC", required=True)
    parser.add_argument("--dst-mac", default="00:00:00:00:00:00", help="New destination MAC", required=True)
    parser.add_argument("--src-ip", default="127.0.0.1", help="New source IP", required=True)
    parser.add_argument("--dst-ip", default="127.0.0.1", help="New destination IP", required=True)

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit(1)

    # Read the packets.
    packets = read_packets_from_file(args.file)

    for _ in range(0, args.iterations):
        if args.fuzz:
            pass
        inject_packets(packets, args.src_mac, args.dst_mac, args.src_ip, args.dst_ip)

if __name__ == "__main__":
    main()
