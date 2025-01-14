from random import getrandbits


def GHZ_verification_client(connection, qubit):
    '''
    Perform the client steps to verify the GHZ state.
    '''
    # Pick a random basis
    basis = getrandbits(1)

    # If basis = 1 rotate the Y to the X basis
    if basis:
        qubit.rot_Z(3,1)
    
    # Measure in the X basis: Hadamard then Z measurement
    qubit.H()
    outcome = qubit.measure()

    # Flush the connection
    yield from connection.flush()
    
    # Return the outcome and the basis choice
    return outcome, basis