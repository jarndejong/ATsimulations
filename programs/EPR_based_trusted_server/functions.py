#%%
from programs.EPR_based_trusted_server.server import CentralServerProgram
from programs.EPR_based_trusted_server.client import Client as ClientProgram
from squidasm.squidasm.run.stack.run import run

from utils.messageencoding import binary_entropy, calculate_statistical_correction

from random import sample


## Setup programs
def get_number_announced_bits(
                            nr_clients: int = 3,
                            nr_rounds: int = int(1e3),
                            nr_estimation_rounds: int = int(3e2),
                            perform_statcor_PE: bool = False,
                            PE_tolerance: float = 1e-8,
                            network_configuration = None,
                            nr_runtimes: int = 1,
                            Alice: str = None,
                            print_loop_nrs: bool = False,
                            simultaneous_server: bool = False,
                            ):
    """ Get the number of announced bits for the given parameters in a trusted GHZ based setting.
    nr_clients:             (default 3) Number of clients. Used for extrapolation.
    nr_rounds:              (default 1e3) Number of rounds to run.
    nr_estimation_rounds:   (default 3e2) Number of rounds to consume to estimate the error rate.
    perform_statcor_PE:     (default False) Whether to perform statistical correction to PE ereror rate.
    PE_tolerance:           (default 1e-8) Tolerance for statistical correction of PE.
    network_configuration:  (default None) Network configuration object from Squidasm.
    nr_runtimes:            (default 1) Number of times to run the simulation.
    Alice:                  (default None) Client that is Alice.
    print_loop_nrs:         (default False) Print the loop number. Get's passed to the server program.
    simultaneous_server:    (default False) Whether the server can distribute EPR pairs between different pairs of clients simultaneously or not. Determines the scaling of the message length in terms of the number of clients.
    """
    ## Print how often the simulation will be run
    print(f"\t Simulation will repeat {nr_runtimes} times.")

    ## Import Alice if not provided
    if not Alice:
        Alice = "C0"
    
    ## Setup programs
    server_program = CentralServerProgram(nr_rounds = nr_rounds, print_loop_nrs = print_loop_nrs)

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

        for i in range(2):
            results[f"C{i}"] = out[i+1]

        ## For simulation purposes, its easier to group the outcomes by round
        outcomes = [[results[f"C{i}"][run_nr]['outcomes'][round_nr] for i in range(2)] for round_nr in range(nr_rounds)]

        ## Make random choice of estimation rounds 
        PE_rounds_selection = sample(range(nr_rounds), k = nr_estimation_rounds) # PE = Parameter Estimation

        ## Perform the parameter estimation
        estimation_parities = []
        for round_nr in PE_rounds_selection:
            estimation_parities.append(sum(outcomes[round_nr]) % 2)

        # Calcualte the error rate
        error_rate = sum(estimation_parities)/len(estimation_parities)

        # Perform statistical correction on estimation of error rate
        if perform_statcor_PE:
            statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=nr_estimation_rounds, tolerance = PE_tolerance)
        else:
            statistical_correction = 0

        ## Calculate the binary entropy, potentially including the statistical correction. Subsequently calculate the message size.
        try:
            # Get the binary entropy
            bin_entropy = binary_entropy(error_rate + statistical_correction)
            # Calculate the total number of bits
            message_size = (1 - bin_entropy) * (nr_rounds - nr_estimation_rounds)
        except ValueError:
            print(f"The (statistically corrected) error rate is too large: {error_rate:.2f} + ({statistical_correction:.3f})")
            message_size = 0
        
        ## Extrapolate the overall message length from the bi-partite rate.
        if simultaneous_server:
            scaling_factor = (nr_clients - 1*int(nr_clients/2)) # If nr_clients is odd then this should just be nr_clients, if nr_clients is even it should be nr_clients - 1.
            message_size /= scaling_factor
        else:
            scaling_factor = (1/2)*nr_clients*(nr_clients - 1)
            message_size /= scaling_factor

        ## Append the message length and run times to the lists
        message_lengths.append(message_size)
        run_times.append(results['simulation_time'])

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
    # statistical_correction = calculate_statistical_correction(nr_total_rounds=nr_rounds, nr_est_rounds=nr_estimation_rounds, tolerance = tolerance)
    # print(statistical_correction)

