ZLIB_CM = 0x78
ZLIB_CINFO = [
    0x01,
    0x5e,
    0x9c,
    0xda
]


def is_zlib_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read(2)

    if len(data) != 2:
        return False

    if data[0] != ZLIB_CM:
        return False

    return data[1] in ZLIB_CINFO
