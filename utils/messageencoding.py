from math import log2

def encode_message_to_bits(message: str, total_bits: int) -> list[int]:
    """Encodes a string into a fixed-length list of bits (0s and 1s)."""
    # Convert string to bytes
    byte_data = message.encode('utf-8')
    required_bits = len(byte_data) * 8
    
    if required_bits > total_bits:
        raise ValueError("Message too long to fit in the specified number of bits.")
    
    # Convert each byte to 8 bits
    bits = []
    for byte in byte_data:
        bits.extend([(byte >> i) & 1 for i in reversed(range(8))])
    
    # Pad with zeros if necessary
    padding = total_bits - required_bits
    bits.extend([0] * padding)
    
    return bits


def decode_bits_to_message(bits: list[int]) -> str:
    """Decodes a fixed-length list of bits (0s and 1s) back into a string."""
    # Group bits into bytes
    if len(bits) % 8 != 0:
        raise ValueError("Bit list length must be a multiple of 8.")
    
    byte_list = []
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i+8]:
            byte = (byte << 1) | bit
        byte_list.append(byte)

    # Remove trailing null bytes (0x00) from padding
    message = bytes(byte_list).rstrip(b'\x00').decode('utf-8')
    return message

def binary_entropy(p: float) -> float:
    """Obtain the binary entropy h_2(p) of p, defined as -p*log(p) - (1-p)*log(1-p). Throws an exception when not 0 <= p <= 0.5"""
    if (p < 0) or (p > 0.5): raise ValueError
    return -p*log2(p) - (1-p)*log2(1-p)

def calculate_statistical_correction(nr_total_rounds: int, nr_est_rounds: int, tolerance: float):
    '''
    Calculate the statistical error for the Z or X basis that arises from parameter estimation.
    nr_est_rounds is the number of rounds used for estimation
    nr_total_rounds is the total number of rounds
    '''
    num = (nr_total_rounds+nr_est_rounds)*(nr_est_rounds+1)
    den = nr_total_rounds*nr_est_rounds**2
    tolerance_factor = log2(1/tolerance)
    
    return (tolerance_factor*num/den)**(1/2)