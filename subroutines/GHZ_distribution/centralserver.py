import netsquid as ns

from squidasm.squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.squidasm.util import get_qubit_state


def GHZ_distribution_Server(connection, epr_qubits, csockets):
    '''
    '''
    ## Loop through every client
    loop = zip(epr_qubits, csockets)
    # Skip over the first client
    loop.next()

    # Perform the loop
    for qubit, csocket in loop:
        # CZ from first qubit to current qubit
        epr_qubits[0].cphase(qubit)

        # X-basis measurement of qubit
        qubit.H()
        outcome = qubit.measure()

        # Flush the connection
        yield from connection.flush()
        
        # Send outcome to the client
        csocket.send(outcome)
    
    # Perform X-basis measurement of first qubit
    epr_qubits[0].H()
    outcome = epr_qubits[0].measure()

    # Flush the connection
    yield from connection.flush()

    # Send the outcome to the first client
    csockets[0].send(outcome)

    # Return nothing
    return
        

# class CentralServer(Program):
    
#     def __init__(self,
#                  nr_clients: int = None,
#                  nr_rounds: int = None
#                  ):
#         if not nr_clients:
#             print("Please provide a number of clients.")
#             raise ValueError
        
#         if not nr_rounds:
#             print('Please provide a number of rounds.')
#             raise ValueError
        
#         self.nr_clients = nr_clients
#         self.nr_rounds = nr_rounds
    
#         self.PEERS = [f"C{nr}" for nr in range(1, self.nr_clients+1)]
        
        
        
    
#     @property
#     def meta(self) -> ProgramMeta:
#         return ProgramMeta(
#             name="GHZdist",
#             csockets=[self.PEERS[nr] for nr in range(self.nr_clients)],
#             epr_sockets=[self.PEERS[nr] for nr in range(self.nr_clients)],
#             max_qubits=self.nr_clients + 1,
#         )
    
#     def run(self, context: ProgramContext):
#         # get classical sockets
#         csockets_clients = [context.csockets[self.PEERS[nr]] for nr in range(self.nr_clients)]
        
#         # get EPR sockets
#         epr_sockets_clients = [context.epr_sockets[self.PEERS[nr]] for nr in range(self.nr_clients)]
        
#         # get connection to quantum network processing unit
#         connection = context.connection

#         # Send a message to all the clients
#         msg = "Hello from the server, client nr."
#         for client_nr, csocket in enumerate(csockets_clients):
#             csocket.send(msg + str(client_nr + 1))
#         print(f"{ns.sim_time()} ns: Server sends: {msg} to clients")

#         # Distribute the GHZ states
#         for loop_nr in range(self.nr_rounds):
#             if self.nr_rounds >= 100:
#                 if (loop_nr - 1) % int(self.nr_rounds/100) == 0:
#                     print(f"At loop number {loop_nr} = {100*loop_nr/self.nr_rounds:.0f}%")
#             # Generate an EPR pair with every client
#             epr_qubits = [epr_socket.create_keep()[0] for epr_socket in epr_sockets_clients]
            
#             # Perform a Bell state measurement between qubit 1 and all other nodes
#             # First perform a CZ from the first to all other nodes
#             for i in range(1, self.nr_clients):
#                 epr_qubits[0].cphase(epr_qubits[i])

#             # Measure all qubits in the X basis
#             measurement_outcomes = []
#             for qubit in epr_qubits:
#                 qubit.H()
#                 measurement_outcomes.append(qubit.measure())
                
    
#             yield from connection.flush()
            
#             # Convert measurement outcomes to int
#             measurement_outcomes = [int(measurement_outcome) for measurement_outcome in measurement_outcomes]
            
            
#             # Send the measurement outcomes to the clients
#             for outcome, csocket in zip(measurement_outcomes, csockets_clients):
#                 csocket.send(outcome)
            
#         print(
#             f"{ns.sim_time()} ns: Server has distributed {self.nr_rounds} GHZ states and has send the corrections"
#         )

#         return {}