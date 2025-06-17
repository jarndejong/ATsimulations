#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:09:05 2024

@author: jarn
"""
from setup.info import nr_clients, client_names

from utils.networkconfigurations import create_central_server_network

link_typ = 'depolarise'

link_cfg = {
  'fidelity' : 0.99,
  't_cycle': 10,
  'prob_success': 0.9,
  }

network_config = create_central_server_network(client_names = client_names,
                                        link_typ = link_typ,
                                        link_cfg = link_cfg,
                                        clink_typ = 'instant',
                                        )