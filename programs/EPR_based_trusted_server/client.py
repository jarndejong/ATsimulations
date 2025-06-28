import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

from random import getrandbits

class Client(Program):    
    def __init__(self,
                 client_number: int = None,
                 nr_rounds: int = None,
                 ):
        
        if not nr_rounds:
            print('Please provide a number of rounds.')
            raise ValueError
        
        self.PEER = "Server"
        self.client_number = client_number
        self.nr_rounds = nr_rounds
            
    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"C{self.client_number}",
            csockets=[self.PEER],
            epr_sockets=[self.PEER],
            max_qubits=1,
        )

    def run(self, context: ProgramContext):
        # get classical sockets
        csocket = context.csockets[self.PEER]
        # get EPR sockets
        epr_socket = context.epr_sockets[self.PEER]
        # get connection to quantum network processing unit
        connection = context.connection

        # Setup complete, going into loop        
        ##### EPR Creation and measurement
        measurement_outcomes = []
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
             
            
            # Perform the steps to obtain the proper GHZ state
            # All clients i > 1 have to perform an X flip if the outcome of the server measurement s_i was 1.
            # This can be done in post-processing
            outcome = qubit.measure()
            yield from connection.flush()

            ## Quantum part done
            # Receive the measurement outcome from the Server
            m_server = yield from csocket.recv()
            m_server = int(m_server)
            assert m_server in [0,1], f"Outcome received from the server is not 0 or 1 but {m_server}"
            
            # When the client is not 1, do an X flip based on the m_{s_{i}} outcome.
            # This X flip just flips the Z basis measurement
            if self.client_number != 0:
                outcome = outcome ^ m_server

            # Flush the connection
            yield from connection.flush()
            
            measurement_outcomes.append(int(outcome))
        return {'outcomes' : measurement_outcomes}