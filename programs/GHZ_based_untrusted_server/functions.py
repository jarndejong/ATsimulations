#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:44:29 2024

@author: jarn
"""
#%%
from programs.GHZ_based_untrusted_server.server import CentralServerProgram
from programs.GHZ_based_untrusted_server.client import Client as ClientProgram
from squidasm.squidasm.run.stack.run import run

from utils.messageencoding import binary_entropy, calculate_statistical_correction

from random import sample
from math import ceil, log


def get_number_announced_bits(
                            nr_clients: int = 3,
                            nr_rounds: int = int(1e3),
                            nr_verification_rounds: int = int(3e2),
                            perform_statcor_VER: bool = True,
                            VER_tolerance: float = 1e-8,
                            perform_separate_PE: bool = True,
                            nr_estimation_rounds: int = int(3e2),
                            perform_statcor_PE: bool = False,
                            PE_tolerance: float = 1e-8,
                            network_configuration = None,
                            nr_runtimes = 1,
                            Alice: str = None,
                            print_loop_nrs: bool = False,
                            anon_tolerance: float = 1e-8,
                            ):
    """
    nr_clients:             (default 3) Number of clients.
    nr_rounds:              (default 1e3) Number of rounds to run.
    nr_verification_rounds: (default 3e2) Number of rounds to consume to perform verification.
    perform_statcor_VER:    (default True) Whether to perform statistical correction to verification error rate.
    VER_tolerance:          (default 1e-8) Tolerance for statistical correction of VER.
    perform_separate_PE:    (default True) Whether to perform PE separately from VER, instead of inferring it from VER.
    nr_estimation_rounds:   (default 3e2) Number of rounds to consume to estimate the error rate.
    perform_statcor_PE:     (default False) Whether to perform statistical correction to PE ereror rate.
    PE_tolerance:           (default 1e-8) Tolerance for statistical correction of PE.
    network_configuration:  (default None) Network configuration object from Squidasm.
    nr_runtimes:            (default 1) Number of times to run the simulation.
    Alice:                  (default None) Client that is Alice.
    print_loop_nrs:         (default False) Print the loop number. Get's passed to the server program.
    anon_tolerance:         (default 1e-8) Level of anonymity; see keyrate calculations.
    """
    ## Print how often the simulation will be run
    print(f"\t Simulation will repeat {nr_runtimes} times.")

    ## Import Alice if not provided
    if not Alice:
        Alice = "C0"

    if not network_configuration:
        raise ValueError('Please provide a network configuration.')
    ## Setup programs
    server_program = CentralServerProgram(nr_clients = nr_clients, nr_rounds = nr_rounds, print_loop_nrs = print_loop_nrs)
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
    message_lengths = []
    run_times = []
    
    # Loop through every run separately
    for run_nr in range(nr_runtimes):
        results = {"simulation_time" : out[0][run_nr]['simulation_time']}

        for i in range(nr_clients):
            results[f"C{i}"] = out[i+1]

        # bases = []
        # announcements = []

        # for i in range(nr_clients):
        #     announcements.append(list(results[f"C{i}"][run_nr]['outcomes']))
        #     bases.append(list(results[f"C{i}"][run_nr]['bases']))
        
        #%% For simulation purposes, its easier to group the outcomes and bases by round
        outcomes = [[results[f"C{i}"][run_nr]['outcomes'][round_nr] for i in range(nr_clients)] for round_nr in range(nr_rounds)]
        bases = [[results[f"C{i}"][run_nr]['bases'][round_nr] for i in range(nr_clients)] for round_nr in range(nr_rounds)]

        #%% Make random choice of verification and estimation rounds
        # This would be a public source of randomness
        VER_rounds_selection = set(sample(range(nr_rounds), k = nr_verification_rounds)) # VER = verification

        PE_rounds_selection = set(sample(sorted(set(range(nr_rounds)) - VER_rounds_selection), k = nr_estimation_rounds)) # PE = Parameter Estimation

        # broadcasting_rounds_selection = set(range(nr_rounds)) - VER_rounds_selection - PE_rounds_selection # Rest of the rounds, used for anonymous broadcasting

        #%% Simulate the first step now: verification of the results
        ###### Verification step ########
        ## Obtain error rate
        verification_parities = []
        for round_nr in VER_rounds_selection:
            bases_sum = sum(bases[round_nr])
            if (bases_sum % 4) == 0:
                verification_parities.append(sum(outcomes[round_nr]) % 2)
            elif (bases_sum % 4) == 2:
                verification_parities.append((sum(outcomes[round_nr]) + 1) % 2)
        
        verification_error_rate = sum(verification_parities)/len(verification_parities)

        # Perform statistical correction on estimation of error rate
        if perform_statcor_VER:
            verification_statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=len(verification_parities), tolerance = VER_tolerance)
        else:
            verification_statistical_correction = 0
        
        ###### Parameter estimation step ########
        if perform_separate_PE:
            ## Obtain error rate
            estimation_parities = []
            for round_nr in PE_rounds_selection:
                bases_sum = sum(bases[round_nr])
                if (bases_sum % 4) == 0:
                    estimation_parities.append(sum(outcomes[round_nr]) % 2)
                elif (bases_sum % 4) == 2:
                    estimation_parities.append((sum(outcomes[round_nr]) + 1) % 2)
            
            PE_error_rate = sum(estimation_parities)/len(estimation_parities)

            # Perform statistical correction on estimation of error rate
            if perform_statcor_PE:
                PE_statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=len(estimation_parities), tolerance = PE_tolerance)
            else:
                PE_statistical_correction = 0
        else:
            # No extra rounds are used for parameter estimation now. The PE_error rate becomes the verification error rate.
            # The statistical correction, if applicable, also becomes that of the VER rounds.
            PE_rounds_selection = {}
            nr_estimation_rounds = 0
            PE_error_rate = verification_error_rate

            if perform_statcor_PE:
                PE_statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=len(verification_parities), tolerance = PE_tolerance)
            else:
                PE_statistical_correction = 0



        ##### Calculate message length
        try:
            # Calculate verification penalty
            penalty_VER = 1/(ceil(log(anon_tolerance)/log(verification_error_rate + verification_statistical_correction))) ##  See explanation ipynb notebook

            # Calculate estimation penalty
            bin_entropy_EST = binary_entropy(PE_error_rate + PE_statistical_correction)
            penalty_EST = (1/2)*(1 - bin_entropy_EST) # See explanation ipynb notebook

            message_size = penalty_VER * penalty_EST * (nr_rounds - nr_estimation_rounds - nr_verification_rounds) # See explanation ipynb notebook
        except ValueError:
            print(f"The (statistically corrected) error rates are too large:\n\t VER:{verification_error_rate:.2f} + ({verification_statistical_correction:.3f})\n\t  PE:{PE_error_rate:.2f} + ({PE_statistical_correction:.3f})")
            message_size = 0

        ## Append the message length and run times to the lists
        message_lengths.append(message_size)
        run_times.append(results['simulation_time'])

    # Return the list of message lengths and run times
    return message_lengths, run_times


# %%
if __name__ == '__main__':
    from setup.configuration import network_config

    nr_clients = 4
    nr_rounds = int(1e4)

    nr_verification_rounds = int(1e3)
    do_VER_statist = True
    VER_tolerance = 1e-8

    nr_estimation_rounds = int(1e3)
    do_PE_statist = False
    PE_tolerance = 1e-8
    perform_separate_PE = True


    nr_runtimes = 1
    message_size = get_number_announced_bits(
                            nr_clients = nr_clients,
                            nr_rounds = nr_rounds,
                            nr_verification_rounds = nr_verification_rounds, perform_statcor_VER = do_VER_statist, VER_tolerance = VER_tolerance,
                            nr_estimation_rounds = nr_estimation_rounds, perform_statcor_PE = do_PE_statist, PE_tolerance = PE_tolerance,
                            network_configuration = network_config,
                            nr_runtimes = 1,
                            )
    
    print(message_size)
