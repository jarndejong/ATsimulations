import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

from random import getrandbits

from subroutines.GHZ_distribution.client import GHZ_distribution_client
from subroutines.GHZ_verification.client import GHZ_verification_client

class ClientProgram(Program):    
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

        msg = yield from csocket.recv()
        print(f"{ns.sim_time()} ns: Client C{self.client_number} receives: {msg}")
        
        
        ##### GHZ creation and measurement
        measurement_bases = []
        measurement_outcomes = []
        # ghz_outcomes = []
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
            yield from connection.flush() 
            
            # Perform the steps to obtain the proper GHZ state
            qubit = GHZ_distribution_client(qubit, csocket, client_number = self.client_number)
            
            # Perform simple random verification
            outcome, basis = GHZ_verification_client(connection, qubit)
            
            
            measurement_bases.append(basis)
            measurement_outcomes.append(outcome)
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'outcomes' : measurement_outcomes, 'bases' : measurement_bases}