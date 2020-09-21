def code_to_binary(text):
    byte_string = bytearray(text, 'utf8')
    binary_data = ''
    for byte in byte_string:
        binary = bin(byte)
        binary = binary[2::]
        binary = '0' * (8 - len(binary)) + binary
        binary_data += binary
    return binary_data


def decode_from_binary(binary_data):
    byte_list = chunk_string(binary_data, 8)
    symbols = [chr(int(byte_list[i], 2)) for i in range(len(byte_list))]
    data = ''.join(symbols)
    return data


def chunk_string(line, length):
    chunks = [line[0 + i:length + i] for i in range(0, len(line), length)]
    return chunks


def from_binary_to_2bit(data):
    if len(data) != 2:
        raise ValueError
    else:
        if data == '00':
            return '0'
        elif data == '01':
            return '1'
        elif data == '10':
            return '2'
        elif data == '11':
            return '3'
        else:
            raise ValueError


def from_2bit_to_binary(data):
    if data == '0':
        return '00'
    elif data == '1':
        return '01'
    elif data == '2':
        return '10'
    elif data == '3':
        return '11'
    else:
        raise ValueError


def code_to_2bit(binary_data):
    byte_list = chunk_string(binary_data, 2)
    pieces_2bit = [from_binary_to_2bit(byte_list[i]) for i in range(len(byte_list))]
    data = ''.join(pieces_2bit)
    return data


def decode_to_binary(data_2bit):
    pieces_2bit = [from_2bit_to_binary(data_2bit[i]) for i in range(len(data_2bit))]
    data = ''.join(pieces_2bit)
    return data


def code(data):
    binary = code_to_binary(data)
    data_2bit = code_to_2bit(binary)
    return data_2bit


def decode(data_2bit):
    binary = decode_to_binary(data_2bit)
    data = decode_from_binary(binary)
    return data


if __name__ == '__main__':
    res = code('I Love You!')
    print(f'Cells: {len(res)}')
    print(res)
    res = decode(res)
    print(res)
