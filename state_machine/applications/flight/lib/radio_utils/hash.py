"""Hash/Checksum library for the radio protocol"""

def bsdChecksum(bytedata):
    """Very simple, very inescure but fast checksum"""
    checksum = 0

    for b in bytedata:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += b
        checksum &= 0xffff
    return bytes([checksum >> 8, checksum & 0xff])
