import math
import os
import string

ALPHABET = "_-" + string.digits + string.ascii_letters
alphabet_len = len(ALPHABET)


def generate(size: int = 21) -> str:
    mask = (2 << int(math.log(alphabet_len - 1) / math.log(2))) - 1
    step = int(math.ceil(1.6 * mask * size / alphabet_len))
    nanon_id = ""
    while True:
        random_bytes = bytearray(os.urandom(step))
        for i in range(step):
            random_byte = random_bytes[i] & mask
            if random_byte >= alphabet_len:
                continue
            value = ALPHABET[random_byte]
            if not value:
                continue
            nanon_id += value
            if len(nanon_id) == size:
                return nanon_id
