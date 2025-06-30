from utils.store_data import save_run_to_disk

from programs.EPR_based_trusted_server.functions import get_number_announced_bits as EPR_trusted_length
from programs.EPR_based_untrusted_server.functions import get_number_announced_bits as EPR_untrusted_length
from programs.GHZ_based_trusted_server.functions import get_number_announced_bits as GHZ_trusted_length
from programs.GHZ_based_untrusted_server.functions import get_number_announced_bits as GHZ_untrusted_length

from setup.configuration import star_network, link_cfg, link_typ

nr_clients = 6

nr_rounds_list = [int(1e3), int(2e3), int(5e3), int(1e4), int(2e4)]

nr_VER_rounds_list = [int(2e2), int(3.5e2), int(5e2), int(6e2), int(6e2)]
do_VER_statist = True
VER_tolerance = 1e-8

nr_PE_rounds_list = [int(2e2), int(3.5e2), int(5e2), int(6e2), int(6e2)]
do_PE_statist = False
PE_tolerance = 1e-8

anon_tolerance = 1e-8

nr_runtimes = 1

## Create the network configuration (see also notes in setup.configuration!)
network_config = star_network(nr_clients = nr_clients,
                              link_typ = link_typ,
                              link_cfg = link_cfg)

bip_network_config = star_network(nr_clients = 2,
                              link_typ = link_typ,
                              link_cfg = link_cfg)


## Setup saving parameters
basepath = "./Results/lengths_per_nr_rounds/testrun/"

params = {
    "nr_clients": nr_clients,
    "link_typ": link_typ,
    "link_config": link_cfg,
    "nr_runtimes": nr_runtimes,
    "nr_rounds": None,
}

for i in range(3):
    ###     
    params['nr_rounds'] = nr_rounds_list[i]
    ## Bipartite trusted setting
    EPR_trusted_lengths, durations = EPR_trusted_length(
                                    nr_clients=nr_clients,
                                    nr_rounds = nr_rounds_list[i],
                                    nr_estimation_rounds = nr_PE_rounds_list[i],
                                    perform_statcor_PE = do_PE_statist,
                                    network_configuration = bip_network_config,
                                    nr_runtimes = nr_runtimes,
                                    )
    print(EPR_trusted_lengths)

    save_run_to_disk(basepath = basepath,
                     filename = f"EPR_trusted_nrRounds{nr_rounds_list[i]}.pickle",
                     message_lengths = EPR_trusted_lengths,
                    simulation_times = durations,
                     params = params)

    ### Bipartite untrusted setting
    EPR_untrusted_lengths, durations = EPR_untrusted_length(nr_clients = nr_clients,
                                    nr_rounds = nr_rounds_list[i],
                                    nr_verification_rounds = nr_VER_rounds_list[i],
                                    perform_statcor_VER = do_VER_statist,   
                                    VER_tolerance = VER_tolerance,
                                    nr_estimation_rounds = nr_PE_rounds_list[i],
                                    perform_statcor_PE = do_PE_statist,
                                    PE_tolerance = PE_tolerance,
                                    network_configuration = bip_network_config,
                                    nr_runtimes = nr_runtimes,
    )

    print(EPR_untrusted_lengths)
    save_run_to_disk(basepath = basepath,
                    filename = f"EPR_untrusted_nrRounds{nr_rounds_list[i]}.pickle",
                    message_lengths = EPR_untrusted_lengths,
                    simulation_times = durations,
                    params = params)
    
    ### GHZ trusted setting
    GHZ_trusted_lengths, durations = GHZ_trusted_length(
                                    nr_clients = nr_clients,
                                    nr_rounds = nr_rounds_list[i],
                                    nr_estimation_rounds = nr_PE_rounds_list[i],
                                    perform_statcor_PE = do_PE_statist,
                                    network_configuration = network_config,
                                    nr_runtimes = nr_runtimes,
                                    )
    print(GHZ_trusted_lengths)
    save_run_to_disk(basepath = basepath,
                    filename = f"GHZ_trusted_nrRounds{nr_rounds_list[i]}.pickle",
                    simulation_times = durations,
                    message_lengths = GHZ_trusted_lengths,
                    params = params)
    


    ### GHZ untrusted setting
    GHZ_untrusted_combined_PE, durations = GHZ_untrusted_length(nr_clients = nr_clients,
                                    nr_rounds = nr_rounds_list[i],
                                    nr_verification_rounds = nr_VER_rounds_list[i],
                                    perform_statcor_VER = do_VER_statist,
                                    VER_tolerance = VER_tolerance,
                                    perform_separate_PE = False,
                                    network_configuration = network_config,
                                    nr_runtimes = nr_runtimes,
                                    anon_tolerance = anon_tolerance,
                                     )
    print(GHZ_untrusted_combined_PE)
    save_run_to_disk(basepath = basepath,
                    filename = f"GHZ_untrusted_comPE_nrRounds{nr_rounds_list[i]}.pickle",
                    message_lengths = GHZ_untrusted_combined_PE,
                    simulation_times = durations,
                    params = params)

    ### GHZ untrusted with separate PE
    GHZ_untrusted_separate_PE, durations = GHZ_untrusted_length(nr_clients = nr_clients,
                                    nr_rounds = nr_rounds_list[i],
                                    nr_verification_rounds = nr_VER_rounds_list[i],
                                    perform_statcor_VER = do_VER_statist,   
                                    VER_tolerance = VER_tolerance,
                                    perform_separate_PE = True,
                                    nr_estimation_rounds = nr_PE_rounds_list[i],
                                    perform_statcor_PE = do_PE_statist,
                                    PE_tolerance = PE_tolerance,
                                    network_configuration = network_config,
                                    nr_runtimes = nr_runtimes,
                                    anon_tolerance = anon_tolerance,
                                     )
    print(GHZ_untrusted_separate_PE)
    save_run_to_disk(basepath = basepath,
                filename = f"GHZ_untrusted_sepPE_nrRounds{nr_rounds_list[i]}.pickle",
                message_lengths = GHZ_untrusted_combined_PE,
                simulation_times = durations,
                params = params)