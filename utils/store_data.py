from os import makedirs
from pickle import dump, load

def save_run_to_disk(
        basepath: str = "./results/MessageLengths/",
        filename: str = None,
        message_lengths: list = None,
        simulation_times: list = None,
        params: dict = None,
        ):
    '''
    Save the results from a run of the GHZ-based trusted server to disk.
    At the given basepath location, the function will save a file containing the message lengths, and any other parameters that are provided.
    
    :param basepath: str specifying the base path to create folder where data is saved.
    :param filename: the parameter/property unique to the specific run, that will be used in the filename to specify it.
    :param message_lengths: list of the message lengths, which are essentially the results of the simulation.
    :param simulation_time: list of the simulation runtime for each run.
    :param params: dict of parameters of interest of the specific run.
    '''
    # Check if filename provided
    if not filename:
        raise ValueError("Please provide a filename.")

    # Create the base directory if its not already there.
    makedirs(basepath, exist_ok = True)

    # Save the file
    with open(basepath + filename, 'wb') as fh:
        # Save message lengths
        dump({'message_lengths': message_lengths, 'simulation_times': simulation_times, 'params': params}, fh)

def load_from_disk(
        basepath: str = "./results/MessageLengths/",
        filename: str = None,
        ):
    '''
    Load from file.
    :returns: message_length, params pair, where message_lengths is a list, and params is a dictionary.
    '''
    with open(basepath + filename, 'rb') as fh:
        loaded = load(fh)
        return loaded['message_lengths'], loaded['simulation_time'], loaded['params']