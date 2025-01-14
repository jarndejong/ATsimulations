import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

from squidasm.squidasm.util import get_qubit_state

class AliceProgram(Program):    
    def __init__(self,
                 message: list[str] = None,
                 client_number: int = None,
                 nr_rounds: int = None,
                 ):
        
        if not nr_rounds:
            print('Please provide a number of rounds.')
            raise ValueError
        
        self.PEER = "Server"
        self.message = message
        self.client_number = client_number
        self.nr_rounds = nr_rounds
        
    
    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="Alice",
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
            
            ## Measure in the X basis or Y basis
            # If client number is not 1, a Hadamard should have been applied to correct towards the GHZ state
            # So the Hadamard of the correction and of the (X-basis) measurement cancel out in that case
            if self.client_number == 1:
                qubit.H()
                
            # For a Y basis measurement, apply a Rz(pi/2) gate
            # basis = 0
            if basis:
                qubit.rot_Z(3,1)
            
            # Perform measurement
            # Measure the EPR qubit
            result = qubit.measure()
            yield from connection.flush()
    
            # Receive corrections from Server to obtian the true GHZ state
            # This would be a Z correction for node 1, and an X correction for every other node
            # The Z correction for node 1 halways has a non-trivial effect
            # The X correction only has a non-trivial effect if the measurement basis was 1 (Y)
            m_ghz = yield from csocket.recv()
            
            
            if self.client_number == 1:
                result = result ^ m_ghz
            else:
                result = result ^ (m_ghz ^ basis)
            
            measurement_bases.append(basis)
            measurement_outcomes.append(result)
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'outcomes' : measurement_outcomes, 'bases' : measurement_bases}

