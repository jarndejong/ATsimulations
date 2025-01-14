#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:44:29 2024

@author: jarn
"""

from protocols.GHZdistribution.centralserver import CentralServer
from protocols.Anonymoustransmission.client import AliceProgram, ClientProgram

# from squidasm.run.stack.config import StackNetworkConfig
from squidasm.squidasm.run.stack.run import run


from info import nr_clients, nr_rounds, testing_key
from info import Alice, client_names

from configuration import network_config


## Setup programs
server_program = CentralServer(nr_clients = nr_clients, nr_rounds = nr_rounds)


programs = {"Server": server_program}

for i in range(1, nr_clients+1):
    if f"C{i}" == Alice:
        # node = AliceProgram(
        #     client_number = i, 
        #     nr_rounds = nr_rounds,
        #     )
        node = ClientProgram(
            client_number = i,
            nr_rounds = nr_rounds
            )
    else:
        node = ClientProgram(
            client_number = i,
            nr_rounds = nr_rounds
            )
    programs[f'C{i}'] = node



## Run the simulation. Programs argument is a mapping of network node labels to programs to run on that node
out = run(
    config=network_config,
    programs=programs,
    num_times=1,
)



#%% Post-processing
results = {"Server" : out[0]}

for i in range(1, nr_clients + 1):
    results[f"C{i}"] = out[i]

# for node in participants:
#     print(results[node][0]['raw_key'])

# QZs = {Bob: 1 - sum(x == y for x,y in zip(results[Alice][0]['raw_key'],results[Bob][0]['raw_key']))/len(results[Bob][0]['raw_key']) for Bob in Bobs}

## Testing rounds
# testing_outcomes = [results[part][0]['testing'] for part in participants]
# for nonpar in nonparticipants:
#     nonpar_testing_outcomes = [outcome for index, outcome in enumerate(results[nonpar][0]) if testing_key[index] == 1]
    
#     testing_outcomes.append(nonpar_testing_outcomes)

##
# Qx = 0
# for testround in zip(*testing_outcomes):
#     Qx += sum(testround) % 2

# Qx /= len(testing_outcomes[0])

announcements = []
for i in range(1, nr_clients + 1):
    announcements.append(list(zip(*[results[f"C{i}"][0]['bases'], results[f"C{i}"][0]['outcomes']])))

parities = []
quadY = []
doubY = []
for round_announcements in zip(*announcements):
    b, o = list(zip(*round_announcements))
    if (sum(b) % 4) == 0:
        parities.append(sum(o) % 2)
        quadY.append(sum(o) % 2)
    elif (sum(b) % 2) == 0:
        parities.append((sum(o) + 1) % 2)
        doubY.append((sum(o) + 1) % 2)

print(sum(parities), len(parities))

print(sum(quadY), len(quadY))

print(sum(doubY), len(doubY))