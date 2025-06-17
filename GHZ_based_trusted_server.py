#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:44:29 2024

@author: jarn
"""
#%%x
from programs.GHZ_based_trusted_server.server import CentralServerProgram
from programs.GHZ_based_trusted_server.client import Client as ClientProgram, Alice as Aliceprogram

from utils.messageencoding import binary_entropy, calculate_statistical_correction

from squidasm.squidasm.run.stack.run import run


from setup.info import Alice


from random import sample


## Setup programs
def get_number_announced_bits(nr_clients = 3, nr_rounds = 1e3, nr_estimation_rounds = 5e2, perform_statistical_correction_on_error_rate: bool = False, PE_tolerance: float = 1e-8, network_configuration = None, nr_runtimes = 1):
    """
    nr_clients:             (default 3) Number of clients.
    nr_rounds:              (default 1e3) Number of rounds to run.
    nr_estimation_rounds:   (default 1e2) Number of rounds to consume to estimate the error rate.
    verification_prob:      (default 0.1) Probability that a round will be a verification round. Used by the public source of randomness to determine what rounds are verification rounds.
    network_configuration:  (default None) Network configuration object from Squidasm.
    nr_runtimes:            (default 1) Number of times to run the simulation.
    """
    server_program = CentralServerProgram(nr_clients = nr_clients, nr_rounds = nr_rounds)

    programs = {"Server": server_program}

    for i in range(nr_clients):
        if f"C{i}" == Alice:
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
        config=network_configuration,
        programs=programs,
        num_times=nr_runtimes,
    )

    #%% Post-processing
    results = {"Server" : out[0][0]['first_outcomes']}

    for i in range(nr_clients):
        results[f"C{i}"] = out[i+1]

    announcements = []

    for i in range(nr_clients):
        announcements.append(list(results[f"C{i}"][0]['outcomes']))

    #%% Make random choice of verification rounds 
    PE_rounds_selection = sample(range(nr_rounds), k = nr_estimation_rounds) # PE = Parameter Estimation

    estimation_parities = []
    message_parities = []


    for round_nr in range(nr_rounds):
        if round_nr in PE_rounds_selection:
            announcements_round_sum = sum([announcements[c][round_nr] for c in range(nr_clients)]) % 2
            estimation_parities.append(announcements_round_sum)
        else:
            announcements_round_sum = sum([announcements[c][round_nr] for c in range(nr_clients)]) % 2
            message_parities.append(announcements_round_sum)

    # Calcualte error rate of verification rounds
    error_rate = sum(estimation_parities)/len(estimation_parities)

    # Perform statistical correction on estimation of error rate
    if perform_statistical_correction_on_error_rate:
        statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=nr_estimation_rounds, tolerance = PE_tolerance)
    else:
        statistical_correction = 0
    # Calculate the binary entropy, potentially including the statistical correction
    try:
        # Get the binary entropy
        bin_entropy = binary_entropy(error_rate)
        # Calculate the total number of bits
        message_size = (1 - bin_entropy) * (nr_rounds - nr_estimation_rounds)
    except ValueError:
        print(f"The (statistically corrected) error rate is too large: {error_rate:.2f} + ({statistical_correction:.3f})")
        message_size = 0

    # Return
    return message_size
    
    
if __name__ == '__main__':

    from setup.configuration import network_config

    nr_clients = 4
    nr_estimation_rounds = int(2e2)
    nr_rounds = int(1e3)
    tolerance = 1e-8
    nr_runtimes = 1
    message_size = get_number_announced_bits(
                                nr_clients=nr_clients,
                                nr_rounds = nr_rounds,
                                nr_estimation_rounds = nr_estimation_rounds,
                                network_configuration=network_config,
                                nr_runtimes=nr_runtimes,
                                )
    
    print(message_size)
    # statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=nr_estimation_rounds, tolerance = tolerance)
    # print(statistical_correction)

