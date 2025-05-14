#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:44:29 2024

@author: jarn
"""
#%%x
from programs.GHZ_distribution_verification_random_bases.server import CentralServerProgram
# from programs.GHZ_distribution_verification_random_bases.client import ClientProgramYbasis as ClientProgram
# from programs.GHZ_distribution_verification_random_bases.client import ClientProgramXbasis as ClientProgram
# from programs.GHZ_distribution_verification_random_bases.client import ClientProgramZbasis as ClientProgram
from programs.GHZ_distribution_verification_random_bases.client import ClientProgramXorYbasis as ClientProgram


from squidasm.squidasm.run.stack.run import run


from setup.info import nr_clients, nr_rounds, testing_key
from setup.info import Alice, client_names

from setup.configuration import network_config


## Setup programs
server_program = CentralServerProgram(nr_clients = nr_clients, nr_rounds = nr_rounds)


programs = {"Server": server_program}

for i in range(nr_clients):
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
results = {"Server" : out[0][0]['first_outcomes']}

for i in range(nr_clients):
    results[f"C{i}"] = out[i+1]

bases = []
announcements = []

for i in range(nr_clients):
    announcements.append(list(results[f"C{i}"][0]['outcomes']))
    bases.append(list(results[f"C{i}"][0]['bases']))

#%%
parities = []
for round_nr in range(nr_rounds):
    bases_round_sum = sum([bases[c][round_nr] for c in range(nr_clients)])
    announcements_round_sum = sum([announcements[c][round_nr] for c in range(nr_clients)]) % 2
    if (bases_round_sum % 4) == 0:
        parities.append(announcements_round_sum)
    elif (bases_round_sum % 4) == 2:
        parities.append(announcements_round_sum ^ 1)

print(sum(parities), len(parities))
#%%
# parities = []
# for round_bases, round_announcements in zip(zip(*bases),zip(*announcements)):
#     # print(round_bases)
#     # print(round_announcements)
#     # print(round_bases)
#     if sum(round_bases) % 4 == 0:
#         print('\n')
#         print(round_bases)
#         print(round_announcements)
#         parities.append(sum(round_announcements) % 2)
#         # if (sum(round_announcements) % 2) != 0:
#         #     print('huh2')
#             # print(round_bases)
#             # print(round_announcements)
#     # elif sum(round_bases) % 4 == 2:
#     #     parities.append((sum(parities) + 1) % 2)
#     #     if (sum(round_announcements)) % 2 != 1:
#             # print('huh')
#             # print(round_bases)
#             # print(round_announcements)


# print(sum(parities), len(parities))

# %%
