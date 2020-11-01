from reedsolo import RSCodec, ReedSolomonError


def code(data):
    data = bytes(data, encoding='utf8')
    rsc = RSCodec(10)
    coded_data = rsc.encode(data)
    binary_coded_data = ''
    for byte in coded_data:
        binary = bin(byte)[2::]
        binary = '0' * (8 - len(binary)) + binary
        binary_coded_data += binary
    quart_coded_data = '0123'
    for i in range(0, len(binary_coded_data), 2):
        byte_pair = binary_coded_data[i] + binary_coded_data[i + 1]
        if byte_pair == '00':
            quart_coded_data += '0'
        elif byte_pair == '01':
            quart_coded_data += '1'
        elif byte_pair == '10':
            quart_coded_data += '2'
        elif byte_pair == '11':
            quart_coded_data += '3'
        else:
            raise ValueError
    quart_coded_data += '3333'
    return quart_coded_data


def decode(quart_coded_data):
    quart_coded_data = quart_coded_data[4:-4:]
    binary_coded_data = ''
    for byte in quart_coded_data:
        if byte == '0':
            binary_coded_data += '00'
        elif byte == '1':
            binary_coded_data += '01'
        elif byte == '2':
            binary_coded_data += '10'
        elif byte == '3':
            binary_coded_data += '11'
        else:
            raise ValueError
    coded_data = []
    for bit_chunk in range(0, len(binary_coded_data), 8):
        chunk_data = ''
        for bit_ind in range(8):
            chunk_data += binary_coded_data[bit_chunk + bit_ind]
        value = int(chunk_data, 2)
        coded_data.append(value)
    coded_data = bytes(coded_data)
    rsc = RSCodec(10)
    decoded_data = rsc.decode(coded_data)[0].decode()
    return decoded_data


if __name__ == '__main__':
    encoded = code('I Love You')
    print(encoded)
    decoded = decode(encoded)
    print(decoded)
