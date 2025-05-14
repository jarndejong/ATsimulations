import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

class CentralServerProgram(Program):
    def __init__(self,
                 nr_clients: int = None,
                 client_names: list = None,
                 nr_rounds: int = None
                 ):
        if not nr_clients:
            print("Please provide a number of clients.")
            raise ValueError
        self.nr_clients = nr_clients

        if not nr_rounds:
            print('Please provide a number of rounds.')
            raise ValueError
        self.nr_rounds = nr_rounds
        
        if not client_names:
            print("No client names provided, defaulting to [C1, C2, ..... C{nr_clients}]")
            client_names = [f"C{nr}" for nr in range(self.nr_clients)]
        self.PEERS = client_names
        
    
    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="GHZdist",
            csockets=[self.PEERS[nr] for nr in range(self.nr_clients)],
            epr_sockets=[self.PEERS[nr] for nr in range(self.nr_clients)],
            max_qubits=self.nr_clients,
        )
    
    def run(self, context: ProgramContext):
        # get classical sockets
        csockets_clients = [context.csockets[self.PEERS[nr]] for nr in range(self.nr_clients)]
        
        # get EPR sockets
        epr_sockets_clients = [context.epr_sockets[self.PEERS[nr]] for nr in range(self.nr_clients)]
        
        # get connection to quantum network processing unit
        connection = context.connection

        # List of the first qubit measurement outcome
        first_outcomes = []

        # Distribute the GHZ states
        for loop_nr in range(self.nr_rounds):
            # Print info of rounds number
            if self.nr_rounds >= 100:
                if (loop_nr - 1) % int(self.nr_rounds/100) == 0:
                    print(f"At loop number {loop_nr} = {100*loop_nr/self.nr_rounds:.0f}%")

            # Initialize the outcomes for this round
            outcomes = [0]*self.nr_clients

            # Generate an EPR pair with every client
            epr_qubits = [epr_socket.create_keep()[0] for epr_socket in epr_sockets_clients]
            
            ### ------- Distribute the GHZ state -------- ###
            ## Loop through every client except first
            for client_nr in range(1,self.nr_clients):

                # CX from first qubit to current qubit
                epr_qubits[0].cnot(epr_qubits[client_nr])

                # Z-basis measurement of qubit
                outcomes[client_nr] = epr_qubits[client_nr].measure()
                
            # Perform X-basis measurement of first qubit
            epr_qubits[0].H()
            outcomes[0] = epr_qubits[0].measure()

            # Flush the connection
            yield from connection.flush()

            ## Send the measurement outcomes
            for client_nr in range(self.nr_clients):
                # Send outcome to the client
                csockets_clients[client_nr].send(str(outcomes[client_nr]))
        
        print(
            f"{ns.sim_time()} ns: Server has distributed {self.nr_rounds} GHZ states and has send the corrections"
        )

        return {'first_outcomes': first_outcomes,}