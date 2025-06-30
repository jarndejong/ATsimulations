#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:09:05 2024

@author: jarn
"""
from utils.networkconfigurations import create_central_server_network

##### Setup the network configuration here. Of course after importing, one can change the parameters (link_cfg is just a dict).
# See also https://squidasm.readthedocs.io/en/latest/modules/configurations/link_configurations.html
# and https://squidasm.readthedocs.io/en/latest/tutorial/section4_NetworkConfiguration.html#link-types
# and for parameter sweeping also https://squidasm.readthedocs.io/en/latest/tutorial/section4_NetworkConfiguration.html#parameter-sweeping
## Depolarise type
link_typ = 'depolarise'
link_cfg = {
  'fidelity' : 0.99,
  't_cycle': 10,
  'prob_success': 0.9,
  }


## Heralded type


def star_network(nr_clients: int = 2,
                 link_typ = link_typ,
                 link_cfg = link_cfg,
                 clink_typ = 'instant'):
    '''
    Importable function te create a star network.
    '''
    # Setup client names
    client_names = [f"C{i}" for i in range(nr_clients)]

    # Create network
    network_config = create_central_server_network(
        client_names = client_names,
        link_typ = link_typ,
        link_cfg = link_cfg,
        clink_typ = clink_typ,
    )

    # Return
    return network_config