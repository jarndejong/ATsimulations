import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

class NonparticipantProgram(Program):
    def __init__(self,
                 client_number: str = None, 
                 network_names: list[str] = None,
                 nr_rounds: int = None,
                 ):
        if not client_number:
            print("Please provide a client_number.")
            raise ValueError
        
        if not network_names:
            print("Please provide a list of nodes in the network.")
            raise ValueError
        
        if not nr_rounds:
            print('Please provide a number of rounds.')
            raise ValueError
        
        self.PEER = "Server"
        self.client_number = client_number
        self.nr_rounds = nr_rounds
        
    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="GHZdist",
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
        outcomes = []
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
            yield from connection.flush()
    
            # If client number is not 1, a Hadamard should be applied to the qubit to obtain the proper GHZ state
            # Nonparticipants always measure in the X basis, so another Hadamard is applied
            # They cancel for every client except nr 1, so only for client nr 1 a Hadamard is applied
            
            if self.client_number == 1:
                qubit.H()
            
            # Measure the EPR qubit
            result = qubit.measure()
            yield from connection.flush()
    
            # Receive corrections from Server to obtian the true GHZ state
            # This would be a Z correction for node 1, and an X correction for every other node
            # Only the Z correction for node 1 has a non-trivial effect on the X measurement of a non-participnt
            
            m_ghz = yield from csocket.recv()
            # Set the true measurement outcome
            outcome = int(result)
            if self.client_number == 1:
                outcome = outcome ^ m_ghz
            
            # append the outcome to the list of outcomes
            outcomes.append(outcome)

        
        print(
            f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
            )
        
        return outcomes

class AliceProgram(Program):    
    def __init__(self,
                 client_number: str = None, 
                 participants_selection: list[str] = None,
                 network_names: list[str] = None,
                 testing_key: str = None,
                 nr_rounds: int = None,
                 ):
        if not client_number:
            print("Please provide a client_number.")
            raise ValueError
        
        if not participants_selection:
            print("Please provide a selection of participants.")
            raise ValueError
        
        if not network_names:
            print("Please provide a list of nodes in the network.")
            raise ValueError
        
        if not testing_key:
            print("Please provide a testing key.")
            raise ValueError
        
        if not nr_rounds:
            print('Please provide a number of rounds.')
            raise ValueError
        
        self.PEER = "Server"
        self.client_number = client_number
        self.nr_rounds = nr_rounds
        
        self.participants = participants_selection
        self.non_participants = [node for node in network_names if node not in participants_selection]
        
        self.testing_key = testing_key
    
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
        testing_outcomes = []
        raw_key = []
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
            yield from connection.flush()
            
            # Now depending on if the testing key is 0 or 1, do a key round or a testing round
            if self.testing_key[loop_nr] == 0:
                # Now a keygen round -> Z-basis measurement
                # If client number is not 1, a Hadamard should be applied to the qubit to obtain the proper GHZ state
                # For keygen round, Alice measures in the Z-basis, so all Hadamards have to be applied except for if client_nr is 1
                # Change to Hadamard basis 
                if self.client_number > 1:
                    qubit.H()
                
                # Measure the EPR qubit
                result = qubit.measure()
                yield from connection.flush()
        
                # Receive corrections from Server to obtian the true GHZ state
                # This would be a Z correction for node 1, and an X correction for every other node
                # Only the Z correction for node 1 has a non-trivial effect on the X measurement of a non-participnt
                m_ghz = yield from csocket.recv()
                
                # Set the true measurement outcome
                outcome = int(result)
                if self.client_number > 1:
                    outcome = outcome ^ m_ghz
                
                # append the outcome to the list of outcomes
                raw_key.append(outcome)
            
            else:
                # Now a testing round -> X-basis measurement
                
                # If client number is not 1, a Hadamard should be applied to the qubit to obtain the proper GHZ state
                # For testing round, Alice measures in the X basis, which is another Hadamard + measurement
                # These cancel, so only apply a Hadamard before measurement if client number is 1
                
                if self.client_number == 1:
                    qubit.H()
                
                # Measure the EPR qubit
                result = qubit.measure()
                yield from connection.flush()
        
                # Receive corrections from Server to obtian the true GHZ state
                # This would be a Z correction for node 1, and an X correction for every other node
                # Only the Z correction for node 1 has a non-trivial effect on the X measurement of a non-participnt
                
                m_ghz = yield from csocket.recv()
                # Set the true measurement outcome
                outcome = int(result)
                if self.client_number == 1:
                    outcome = outcome ^ m_ghz
                
                # append the outcome to the list of outcomes
                testing_outcomes.append(outcome)
                
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'raw_key' : raw_key, 'testing' : testing_outcomes}

class ParticipantProgram(Program):
    PEER = "Server"
    
    def __init__(self,
                 client_number: str = None, 
                 network_names: list[str] = None,
                 testing_key: str = None,
                 nr_rounds: int = None,
                 ):
        if not client_number:
            print("Please provide a client_number.")
            raise ValueError
        
        
        if not network_names:
            print("Please provide a list of nodes in the network.")
            raise ValueError
            
        if not testing_key:
            print("Please provide a testing key.")
            raise ValueError
        
        if not nr_rounds:
            print('Please provide a number of rounds.')
            raise ValueError
        self.PEER = "Server"
        self.client_number = client_number
        self.nr_rounds = nr_rounds
        
        self.testing_key = testing_key

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
        testing_outcomes = []
        raw_key = []
        
        for loop_nr in range(self.nr_rounds):
            # Receive half of EPR pair with Server
            qubit = epr_socket.recv_keep()[0]
            yield from connection.flush()
            
            # Now depending on if the testing key is 0 or 1, do a key round or a testing round
            if self.testing_key[loop_nr] == 0:
                # Now a keygen round -> Z-basis measurement
                # If client number is not 1, a Hadamard should be applied to the qubit to obtain the proper GHZ state
                # For keygen round, Alice measures in the Z-basis, so all Hadamards have to be applied except for if client_nr is 1
                # Change to Hadamard basis 
                if self.client_number > 1:
                    qubit.H()
                
                # Measure the EPR qubit
                result = qubit.measure()
                yield from connection.flush()
        
                # Receive corrections from Server to obtian the true GHZ state
                # This would be a Z correction for node 1, and an X correction for every other node
                # Only the Z correction for node 1 has a non-trivial effect on the X measurement of a non-participnt
                m_ghz = yield from csocket.recv()
                
                # Set the true measurement outcome
                outcome = int(result)
                if self.client_number > 1:
                    outcome = outcome ^ m_ghz
                
                # append the outcome to the list of outcomes
                raw_key.append(outcome)
            
            else:
                # Now a testing round -> X-basis measurement
                
                # If client number is not 1, a Hadamard should be applied to the qubit to obtain the proper GHZ state
                # For testing round, Alice measures in the X basis, which is another Hadamard + measurement
                # These cancel, so only apply a Hadamard before measurement if client number is 1
                
                if self.client_number == 1:
                    qubit.H()
                
                # Measure the EPR qubit
                result = qubit.measure()
                yield from connection.flush()
        
                # Receive corrections from Server to obtian the true GHZ state
                # This would be a Z correction for node 1, and an X correction for every other node
                # Only the Z correction for node 1 has a non-trivial effect on the X measurement of a non-participnt
                
                m_ghz = yield from csocket.recv()
                # Set the true measurement outcome
                outcome = int(result)
                if self.client_number == 1:
                    outcome = outcome ^ m_ghz
                
                # append the outcome to the list of outcomes
                testing_outcomes.append(outcome)
        
        print(
               f"{ns.sim_time()} ns: Client C{self.client_number} has finished all measurements"
               )
        return {'raw_key' : raw_key, 'testing' : testing_outcomes}