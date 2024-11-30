#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyEOT End-of-Train Device Decoder
Copyright (c) 2018 Eric Reuter

This source file is subject of the GNU general public license

history:    2018-08-09 Initial Version

purpose:    Receives demodulated FFSK bitstream from GNU Radio, indentifes
            potential packets, and passes them to decoder classes for
            parsing and verification.  Finally human-readable data are printed
            to stdout.

            Requires eot_decoder.py and helpers.py
"""

import datetime
import collections
from eot_decoder import EOT_decode
import zmq
import csv

# Socket to talk to server
context = zmq.Context()
sock = context.socket(zmq.SUB)

# create fixed length queue
queue = collections.deque(maxlen=256)

working_csv_filename = f"logs/eot_log_{datetime.datetime.now().isoformat()}.csv"

def open_csv():
    with open(working_csv_filename, mode='w') as eot_file:
        eot_writer = csv.writer(eot_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        eot_writer.writerow(['Timestamp', 'Unit Address', 'Pressure', 'Motion', 'Marker Light', 'Turbine', 'Battery Cond', 'Battery Charge', 'Arm Status'])

def logEOT(EOT):
    with open(working_csv_filename, mode='a') as eot_file:
        eot_writer = csv.writer(eot_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        eot_writer.writerow([datetime.datetime.now().isoformat(), EOT.unit_addr, EOT.pressure, EOT.motion, EOT.mkr_light, EOT.turbine, EOT.batt_cond_text, EOT.batt_charge, EOT.arm_status])

def printEOT(EOT):
    localtime = str(datetime.datetime.now().
                    strftime('%Y-%m-%d %H:%M:%S.%f'))[:-3]
    print("")
    print("EOT {}".format(localtime))
    #   print(EOT.get_packet())
    print("---------------------")
    print("Unit Address:   {}".format(EOT.unit_addr))
    print("Pressure:       {} psig".format(EOT.pressure))
    print("Motion:         {}".format(EOT.motion))
    print("Marker Light:   {}".format(EOT.mkr_light))
    print("Turbine:        {}".format(EOT.turbine))
    print("Battery Cond:   {}".format(EOT.batt_cond_text))
    print("Battery Charge: {}".format(EOT.batt_charge))
    print("Arm Status:     {}".format(EOT.arm_status))


def main():
    #  Connect to GNU Radio and subscribe to stream
    sock.connect("tcp://localhost:5555")
    sock.setsockopt(zmq.SUBSCRIBE, b'')

    while True:
        newData = sock.recv()  # get whatever data are available
        for byte in newData:
            queue.append(str(byte))  # append each new symbol to deque

            buffer = ''  # clear buffer
            for bit in queue:  # move deque contents into buffer
                buffer += bit

            if (buffer.find('10101011100010010') == 0):  # look for frame sync
                EOT = EOT_decode(buffer[6:])  # first 6 bits are bit sync
                if (EOT.valid):
                    printEOT(EOT)
                    logEOT(EOT)

if __name__ == '__main__':
    open_csv()
    main()
