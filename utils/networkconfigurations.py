import itertools
from typing import List

import netsquid.qubits
import numpy as np
from netqasm.sdk.qubit import Qubit
from netsquid.qubits import operators
from netsquid.qubits import qubitapi as qapi
from netsquid_netbuilder.modules.clinks import ICLinkConfig
from netsquid_netbuilder.modules.qdevices import IQDeviceConfig
from netsquid_netbuilder.modules.qlinks import IQLinkConfig

import squidasm.sim.stack.globals
from squidasm.run.stack.config import (
    CLinkConfig,
    DefaultCLinkConfig,
    DepolariseLinkConfig,
    GenericQDeviceConfig,
    LinkConfig,
    StackConfig,
    StackNetworkConfig,
)


def create_central_server_network(
    client_names: List[str],
    link_typ: str = "perfect",
    link_cfg: IQLinkConfig = None,
    clink_typ: str = "instant",
    clink_cfg: ICLinkConfig = None,
    server_qdevice_typ: str = "generic",
    server_qdevice_cfg: IQDeviceConfig = None,
    client_qdevice_typ: str = "generic",
    client_qdevice_cfg: IQDeviceConfig = None,
    ) -> StackNetworkConfig:
    """
    Create a central distributing network configuration.
    The network generated will connect one node (the server), to all other nodes (the clients); clients are not connected to each other. 
    The link will be the link and clink models provided.
    
    The server takes its own qdevice configuration.
    
    :param client_names: List of str with the names of the clients. The number of names will determine the number of clients. The server is called "Server".
    :param link_typ: str specification of the link model to use for quantum links.
    :param link_cfg: Configuration of the link model.
    :param clink_typ: str specification of the clink model to use for classical communication.
    :param clink_cfg: Configuration of the clink model.
    :param server_qdevice_typ: str specification of the qdevice model to use for the quantum device of the Server.
    :param server_qdevice_cfg: Configuration of qdevice of server.
    :param client_qdevice_typ: str specification of the qdevice model to use for quantum devices of the clients.
    :param client_qdevice_cfg: Configuration of qdevice of client.
    :return: StackNetworkConfig object with a network.
    """
    network_config = StackNetworkConfig(stacks=[], links=[], clinks=[])

    assert len(client_names) > 0
    
    ## Create server
    server_qdevice_cfg = (
        GenericQDeviceConfig.perfect_config() if server_qdevice_cfg is None
        else server_qdevice_cfg
    )
    node = StackConfig(
        name="Server", qdevice_typ=server_qdevice_typ, qdevice_cfg=server_qdevice_cfg
    )
    network_config.stacks.append(node)
    
    ## Create clients
    for client_name in client_names:
        client_qdevice_cfg = (
            GenericQDeviceConfig.perfect_config()
            if client_qdevice_cfg is None
            else client_qdevice_cfg
        )
        node = StackConfig(
            name=client_name, qdevice_typ=client_qdevice_typ, qdevice_cfg=client_qdevice_cfg
        )
        network_config.stacks.append(node)
        
    ## Connect clients to server
    for client_name in client_names:
        ## Quantum link
        link = LinkConfig(stack1="Server", stack2=client_name, typ=link_typ, cfg=link_cfg)
        network_config.links.append(link)
        
        ## Classical link
        clink = CLinkConfig(stack1="Server", stack2=client_name, typ=clink_typ, cfg=clink_cfg)
        network_config.clinks.append(clink)

    return network_config

def create_line_network(
        node_names: List[str],
        link_typ: str = "perfect",
        link_cfg: IQLinkConfig = None,
        clink_typ: str = "instant",
        clink_cfg: ICLinkConfig = None,
        qdevice_typ: str = "generic",
        qdevice_cfg: IQDeviceConfig = None,
        ) -> StackNetworkConfig:
    """
    Create a line network configuration.
    The nodes are positioned along a line, where each node is connected to only its previous and next neighbour.
    The link will be the link and clink models provided.
    
    :param node_names: List of str with the names of the nodes. The number of names will determine the number of nodes.
    :param link_typ: str specification of the link model to use for quantum links
    :param link_cfg: Configuration of the link model.
    :param clink_typ: str specification of the clink model to use for classical communication.
    :param clink_cfg: Configuration of the clink model.
    :param qdevice_typ: str specification of the qdevice model to use for the quantum device of the nodes.
    :param qdevice_cfg: Configuration of qdevice.
    :return: StackNetworkConfig object with a network.
    """
    network_config = StackNetworkConfig(stacks=[], links=[], clinks=[])

    assert len(node_names) > 0
    # {'dummy': 'null'}
    ## Create nodes
    for node_name in node_names:
        qdevice_cfg = (
            GenericQDeviceConfig.perfect_config()
            if qdevice_cfg is None
            else qdevice_cfg
        )
        node = StackConfig(
            name=node_name, qdevice_typ=qdevice_typ, qdevice_cfg=qdevice_cfg
        )
        network_config.stacks.append(node)
        
    ## Connect nodes to their right neighbour
    for node_1, node_2 in zip(node_names, node_names[1:]):
        ## Quantum link
        link = LinkConfig(stack1=node_1, stack2=node_2, typ=link_typ, cfg=link_cfg)
        network_config.links.append(link)
        
        ## Classical link
        clink = CLinkConfig(stack1=node_1, stack2=node_2, typ=clink_typ, cfg=clink_cfg)
        network_config.clinks.append(clink)

    return network_config