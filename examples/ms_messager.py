#!/usr/bin/python
## ===========
## pysap - Python library for crafting SAP's network protocols packets
##
## Copyright (C) 2014 Core Security Technologies
##
## The library was designed and developed by Martin Gallo from the Security
## Consulting Services team of Core Security Technologies.
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##==============

# Standard imports
import logging
from optparse import OptionParser, OptionGroup
# External imports
from scapy.config import conf
from scapy.packet import bind_layers, Raw
from scapy.supersocket import socket
# Custom imports
from pysap.SAPMS import SAPMS
from pysap.SAPNI import SAPNI, SAPNIStreamSocket


# Bind SAP NI with MS packets
bind_layers(SAPNI, SAPMS, )

# Set the verbosity to 0
conf.verb = 0


# Command line options parser
def parse_options():

    description = \
    """This example script connects with the Message Server service and sends
    a message to another client.

    """

    epilog = \
    """pysap - http://corelabs.coresecurity.com/index.php?module=Wiki&action=view&type=tool&name=pysap"""

    usage = "Usage: %prog [options] -d <remote host> -t <target server> -m <message>"

    parser = OptionParser(usage=usage, description=description, epilog=epilog)

    target = OptionGroup(parser, "Target")
    target.add_option("-d", "--remote-host", dest="remote_host", help="Remote host")
    target.add_option("-p", "--remote-port", dest="remote_port", type="int", help="Remote port [%default]", default=3900)
    parser.add_option_group(target)

    misc = OptionGroup(parser, "Misc options")
    misc.add_option("-c", "--client", dest="client", default="pysap's-messager", help="Client name [%default]")
    misc.add_option("-m", "--message", dest="message", default="Message", help="Message to send to the target client [%default]")
    misc.add_option("-t", "--target", dest="target", default="pysap's-listener", help="Target client name to send the message [%default]")
    misc.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Verbose output [%default]")
    parser.add_option_group(misc)

    (options, _) = parser.parse_args()

    if not options.remote_host:
        parser.error("Remote host is required")
    if not options.message or not options.target:
        parser.error("Target server and message are required !")

    return options


# Main function
def main():
    options = parse_options()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Initiate the connection
    conn = SAPNIStreamSocket.get_nisocket(options.remote_host, options.remote_port)
    print "[*] Connected to the message server %s:%d" % (options.remote_host, options.remote_port)

    client_string = options.client

    # Send MS_LOGIN_2 packet
    p = SAPMS(flag=0x00, iflag=0x08, toname=client_string, fromname=client_string)

    print "[*] Sending login packet"
    response = conn.sr(p)[SAPMS]

    print "[*] Login performed, server string: %s" % response.fromname

    # Sends a message to another client
    p = SAPMS(flag=0x02, iflag=0x01, toname=options.target, fromname=client_string, opcode=1)
    p /= Raw(options.message)

    print "[*] Sending packet to: %s" % options.target
    conn.send(p)


if __name__ == "__main__":
    main()