#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:44:29 2024

@author: jarn
"""
#%%x
from programs.anonymous_transmission_trusted_server.server import CentralServerProgram
# from programs.anonymous_transmission_trusted_server.client import ClientProgramYbasis as ClientProgram
# from programs.anonymous_transmission_trusted_server.client import ClientProgramXbasis as ClientProgram
# from programs.anonymous_transmission_trusted_server.client import ClientProgramZbasis as ClientProgram
from programs.anonymous_transmission_trusted_server.client import Client as ClientProgram


from squidasm.squidasm.run.stack.run import run


from setup.info import nr_clients, nr_rounds, testing_key
from setup.info import Alice, client_names

from setup.configuration import network_config

from utils.messageencoding import encode_message_to_bits, decode_bits_to_message

message = "Hello! The Pello"

length = 8*40

encoded_list = encode_message_to_bits(message, length)

out = decode_bits_to_message(encoded_list)

print(out)