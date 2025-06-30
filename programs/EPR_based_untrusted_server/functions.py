#%%
from programs.EPR_based_untrusted_server.server import CentralServerProgram
from programs.EPR_based_untrusted_server.client import Client as ClientProgram
from squidasm.squidasm.run.stack.run import run

from utils.messageencoding import binary_entropy, calculate_statistical_correction

from random import sample
from math import ceil

## Setup programs
def get_number_announced_bits(
                            nr_clients: int = 3,
                            nr_rounds: int = int(1e3),
                            nr_verification_rounds: int = int(3e2),
                            perform_statcor_VER: bool = True,
                            VER_tolerance: float = 1e-8,
                            nr_estimation_rounds: int = int(3e2),
                            perform_statcor_PE: bool = False,
                            PE_tolerance: float = 1e-8,
                            network_configuration = None,
                            nr_runtimes: int = 1,
                            Alice: str = None,
                            print_loop_nrs: bool = False,
                            ):
    """ Get the number of announced bits for the given parameters in a trusted GHZ based setting.
    nr_clients:             (default 3) Number of clients. Used for extrapolation.
    nr_rounds:              (default 1e3) Number of rounds to run.
    nr_verification_rounds: (default 3e2) Number of rounds to consume to perform verification.
    perform_statcor_VER:    (default True) Whether to perform statistical correction to verification error rate.
    VER_tolerance:          (default 1e-8) Tolerance for statistical correction of VER.
    nr_estimation_rounds:   (default 3e2) Number of rounds to consume to estimate the error rate.
    perform_statcor_PE:     (default False) Whether to perform statistical correction to PE ereror rate.
    PE_tolerance:           (default 1e-8) Tolerance for statistical correction of PE.
    network_configuration:  (default None) Network configuration object from Squidasm.
    nr_runtimes:            (default 1) Number of times to run the simulation.
    Alice:                  (default None) Client that is Alice.
    print_loop_nrs:         (default False) Print the loop number. Get's passed to the server program.
    """
    ## Print how often the simulation will be run
    print(f"\t Simulation will repeat {nr_runtimes} times.")

    ## Import Alice if not provided
    if not Alice:
        Alice = "C0"
    
    ## Setup programs
    server_program = CentralServerProgram(nr_rounds = nr_rounds, print_loop_nrs = print_loop_nrs)

    VER_rounds_selection = set(sample(range(nr_rounds), k = nr_verification_rounds)) # VER = verification

    programs = {"Server": server_program}

    for i in range(nr_clients):
        if f"C{i}" == Alice:
            node = ClientProgram(
                client_number = i,
                nr_rounds = nr_rounds,
                VER_rounds_selection = VER_rounds_selection,
                )
        else:
            node = ClientProgram(
                client_number = i,
                nr_rounds = nr_rounds,
                VER_rounds_selection = VER_rounds_selection,
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

        for i in range(2):
            results[f"C{i}"] = out[i+1]

        ## For simulation purposes, its easier to group the outcomes by round
        outcomes = [[results[f"C{i}"][run_nr]['outcomes'][round_nr] for i in range(2)] for round_nr in range(nr_rounds - nr_verification_rounds)]
        verification = [[results[f"C{i}"][run_nr]['verification'][round_nr] for i in range(2)] for round_nr in range(nr_verification_rounds)]

        #%% Simulate the first step now: verification of the results
        ###### Verification step ########
        ## Obtain error rate
        verification_parities = []
        for round_nr in range(nr_verification_rounds):
            verification_parities.append(sum(verification[round_nr]) % 2)
        
        verification_error_rate = sum(verification_parities)/len(verification_parities)

        # Perform statistical correction on estimation of error rate
        if perform_statcor_VER:
            verification_statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=nr_verification_rounds, tolerance = VER_tolerance)
        else:
            verification_statistical_correction = 0

        ## Make random choice of estimation rounds 
        PE_rounds_selection = sample(range(nr_rounds - nr_verification_rounds), k = nr_estimation_rounds) # PE = Parameter Estimation

        ## Perform the parameter estimation
        estimation_parities = []
        for round_nr in PE_rounds_selection:
            estimation_parities.append(sum(outcomes[round_nr]) % 2)

        # Calcualte the error rate
        PE_error_rate = sum(estimation_parities)/len(estimation_parities)

        # Perform statistical correction on estimation of error rate
        if perform_statcor_PE:
            PE_statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=nr_estimation_rounds, tolerance = PE_tolerance)
        else:
            PE_statistical_correction = 0

        ## Calculate the binary entropies of both the error rates, potentially including the statistical correction. Subsequently calculate the message size.
        try:
            # Calculate verification penalty
            bin_entropy_VER = binary_entropy(verification_error_rate + verification_statistical_correction)

            # Calculate estimation penalty
            bin_entropy_EST = binary_entropy(PE_error_rate + PE_statistical_correction)

            # Combined penalty, which also includes a subtraction for arranging the verification rounds.
            penalty = (1 - bin_entropy_VER - bin_entropy_EST)

            # Set to zero if negative keyrate.
            if penalty <= 0:
                penalty = 0

            message_size = penalty*(nr_rounds - nr_estimation_rounds - nr_verification_rounds) # See explanation ipynb notebook
        except ValueError:
            print(f"The (statistically corrected) error rates are too large:\n\t VER:{verification_error_rate:.2f} + ({verification_statistical_correction:.3f})\n\t  PE:{PE_error_rate:.2f} + ({PE_statistical_correction:.3f})")
            message_size = 0

        scaling_factor_simul = 2*2*int(ceil(nr_clients/2)) # If nr_clients is odd then this should just be 2*nr_clients, if nr_clients is even it should be 2*(nr_clients - 1).
        scaling_factor_sub = (1/2)*nr_clients*(nr_clients - 1)

        preshared_key_length = binary_entropy(nr_verification_rounds/nr_rounds) * nr_rounds

        ## Append the message length and run times to the lists
        message_lengths.append([message_size * scaling_factor_simul - preshared_key_length, message_size * scaling_factor_sub - preshared_key_length])
        run_times.append([results['simulation_time'] * scaling_factor_simul, results['simulation_time'] * scaling_factor_sub])

    # Return the list of message lengths and run times
    return message_lengths, run_times
    
if __name__ == '__main__':

    from setup.configuration import network_config

    nr_clients = 4
    nr_rounds = int(1e4)

    nr_estimation_rounds = int(1e3)
    do_PE_statist = False
    PE_tolerance = 1e-8

    nr_runtimes = 2
    message_lengths = get_number_announced_bits(
                                nr_clients=nr_clients,
                                nr_rounds = nr_rounds,
                                nr_estimation_rounds = nr_estimation_rounds, perform_statcor_PE = do_PE_statist, PE_tolerance = PE_tolerance,
                                network_configuration=network_config,
                                nr_runtimes=nr_runtimes,
                                )


    print(message_lengths)

