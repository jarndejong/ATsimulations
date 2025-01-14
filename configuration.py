#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:09:05 2024

@author: jarn
"""

# from squidasm.squidasm.util.util import create_complete_graph_network

from info import nr_clients, client_names

# client_names = ["Server"] + [f"N{i}" for i in range(1, nr_clients + 1)]

# network_config = create_complete_graph_network(node_names = client_names,
#                                         link_typ = 'perfect',
#                                         link_cfg = {'dummy': 'null'},
#                                         clink_typ = 'instant',
#                                         )

from utils.networkconfigurations import create_central_server_network

link_typ = 'depolarise'

link_cfg = {
  'fidelity' : 0.99,
  't_cycle': 10,
  'prob_success': 0.9,
  }

network_config = create_central_server_network(client_names = client_names,
                                        # link_typ = link_typ,
                                        # link_cfg = link_cfg,
                                        # clink_typ = 'instant',
                                        )