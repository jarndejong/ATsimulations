import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

from random import getrandbits

# from subroutines.GHZ_distribution.client import GHZ_distribution_client

class ClientProgramZbasis(Program):    
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
        print(f"{ns.sim_time()} ns: Client C{self.client_number} says: setup complete, going into loop.")
        
        ##### GHZ creation and measurement
        measurement_outcomes = []
        server_outcomes = []
        # ghz_outcomes = []
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
            server_outcomes.append(int(m_server))
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'outcomes' : measurement_outcomes, 'server' : server_outcomes}

class ClientProgramXbasis(Program):    
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
        print(f"{ns.sim_time()} ns: Client C{self.client_number} says: setup complete, going into loop.")
        
        ##### GHZ creation and measurement
        measurement_outcomes = []
        server_outcomes = []
        # ghz_outcomes = []
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
             
            
            # Perform the steps to obtain the proper GHZ state
            # All clients i > 1 have to perform an X flip if the outcome of the server measurement s_i was 1.
            # For the X basis measurement this doesn't have an effect
            # The client i = 1 has to do a Z flip if the outcome of server measurement s_1 was m_{s_{1}} = 1. This will flip the outcome of the X measurement.

            qubit.H()
            outcome = qubit.measure()
            yield from connection.flush()

            ## Quantum part done

            # Receive the measurement outcome from the Server
            m_server = yield from csocket.recv()
            m_server = int(m_server)
            assert m_server in [0,1], f"Outcome received from the server is not 0 or 1 but {m_server}"
            
            # When the client is 1, do an Z flip based on the m_{s_{1}} outcome.
            # This Z flip just flips the X basis measurement outcome
            if self.client_number == 0:
                outcome = outcome ^ m_server

            # Flush the connection
            yield from connection.flush()
            
            measurement_outcomes.append(int(outcome))
            server_outcomes.append(int(m_server))
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'outcomes' : measurement_outcomes, 'server' : server_outcomes}

class ClientProgramYbasis(Program):    
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
        print(f"{ns.sim_time()} ns: Client C{self.client_number} says: setup complete, going into loop.")
        
        ##### GHZ creation and measurement
        measurement_outcomes = []
        server_outcomes = []
        # ghz_outcomes = []
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
             
            
            # Perform the steps to obtain the proper GHZ state
            # All clients i > 1 have to perform an X flip if the outcome of the server measurement s_i was 1.
            # For the X basis measurement this doesn't have an effect

            # The client i = 1 has to do a Z flip if the outcome of server measurement s_1 was 1

            # qubit.H()
            # qubit.S()
            qubit.rot_Z(1,1)
            qubit.H()
            outcome = qubit.measure()
            yield from connection.flush()

            ## Quantum part done

            # Receive the measurement outcome from the Server
            m_server = yield from csocket.recv()
            m_server = int(m_server)
            assert m_server in [0,1], f"Outcome received from the server is not 0 or 1 but {m_server}"
            
            # When the client is 1, do an Z flip based on the m_{s_{1}} outcome.
            # When the client is i>1, do an X flip based on the m_{s_{i}} outcome
            # Both these just flip the outcomes
            outcome = outcome ^ m_server

            # Flush the connection
            yield from connection.flush()
            
            measurement_outcomes.append(int(outcome))
            server_outcomes.append(int(m_server))
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'outcomes' : measurement_outcomes, 'server' : server_outcomes}

class ClientProgramXorYbasis(Program):    
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

        self.bases = [int(b) for b in bin(getrandbits(self.nr_rounds))[2:].zfill(self.nr_rounds)]
            
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
        print(f"{ns.sim_time()} ns: Client C{self.client_number} says: setup complete, going into loop.")
        
        ##### GHZ creation and measurement
        measurement_outcomes = []
        for loop_nr, basis in zip(range(self.nr_rounds),self.bases):
            # 

            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
             

            # All clients i > 1 have to perform an X flip if the outcome of the server measurement s_i was 1.
            # The client i = 1 has to do a Z flip if the outcome of server measurement s_1 was 1
            # In the case of a Y measurement, both these flips just flip the measurement outcome
            
            # Option X basis
            if basis == 0:
                qubit.H()
                outcome = qubit.measure()
                yield from connection.flush()

                ## Quantum part done
                # Receive the measurement outcome from the Server
                m_server = yield from csocket.recv()
                m_server = int(m_server)
                assert m_server in [0,1], f"Outcome received from the server is not 0 or 1 but {m_server}"
            
                # When the client is 1, do an Z flip based on the m_{s_{1}} outcome.
                # This Z flip just flips the X basis measurement outcome
                if self.client_number == 0:
                    outcome = outcome ^ m_server
            
            # Option Y basis
            elif basis == 1:
                qubit.rot_Z(1,1)
                qubit.H()
                outcome = qubit.measure()
                yield from connection.flush()

                ## Quantum part done

                # Receive the measurement outcome from the Server
                m_server = yield from csocket.recv()
                m_server = int(m_server)
                assert m_server in [0,1], f"Outcome received from the server is not 0 or 1 but {m_server}"
                
                # When the client is 1, do an Z flip based on the m_{s_{1}} outcome.
                # When the client is i>1, do an X flip based on the m_{s_{i}} outcome
                # Both these just flip the outcomes
                outcome = outcome ^ m_server

                # Flush the connection
                yield from connection.flush()

            # Append the outcomes to the list
            measurement_outcomes.append(int(outcome))
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'outcomes' : measurement_outcomes, 'bases' : self.bases}