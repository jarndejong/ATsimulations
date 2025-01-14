def GHZ_distribution_client(qubit, csocket_with_server, client_number = 1):
    '''
    Perform the client steps that are necessary to obtain the proper GHZ state over the entire network.
    '''
    # Receive the measurement outcome from the Server
    m_server = yield from csocket_with_server.recv()

    assert m_server in [0,1], f"Outcome received from the server is not 0 or 1 but {m_server}"

    # Perform a Z correction to the qubit based on the correction
    if m_server:
        qubit.Z()
    
    # Perform a Hadamard on the qubit if it's not the first client
    if client_number != 1:
        qubit.H()
    
    # Return the qubit
    return qubit