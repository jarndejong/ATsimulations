#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:09:58 2024

@author: jarn
"""
from random import choice, sample, shuffle
from math import log


#%% Network setup
nr_clients = 4
nr_Bobs = 2

#%% Protocol parameters

shuffle_testing_rounds = False

nr_rounds = int(1e2)

p = 0.03 + 1/(log(nr_rounds, 10)**2)



#%% Calculations
# Setup network
client_names = [f"C{i}" for i in range(1, nr_clients + 1)]
Bobs = None
Alice = choice(client_names)
Bobs = sample(client_names, k = nr_Bobs)


# If alice is in the list of participants, redo random choice
while Alice in Bobs:
    Alice = choice(client_names )
    Bobs = sample(client_names, k = nr_Bobs)

participants = Bobs + [Alice]

nonparticipants = [node for node in client_names if node not in participants]

# Setup protocol params
m = int(p*nr_rounds) # number of testing rounds
k = nr_rounds - m # number of keygen rounds

testing_key = [1]*m + [0]*k

if shuffle_testing_rounds:
    shuffle(testing_key)