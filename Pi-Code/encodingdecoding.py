import numpy


def ReadFile(filename):
    try:
        file = open(filename, 'r')
        file_content = file.read()
        file.close()
        return file_content
    except IOError:
        return None


def StringToByteArray(string):
    byte_array = bytearray()
    byte_array.extend(map(ord, string))
    return byte_array


def getVandermondeMatrix(data, parity):
    vander_set = numpy.linspace(0, data + parity - 1, data + parity)
    vander_matrix = numpy.vander(vander_set, data, increasing=True)
    vander_matrix = numpy.mod(vander_matrix, 255)
    return vander_matrix


def getEncodingMatrix(vander_matrix):
    vander_upper = vander_matrix[0:len(vander_matrix[0])]
    upper_inverse = numpy.linalg.inv(vander_upper)
    encoding_matrix = numpy.matmul(vander_matrix, upper_inverse)
    return encoding_matrix


def getDataMatrix(data, server):
    data_matrix = [[0 for j in range(int(len(data) / server) + 1)] for i in range(server)]
    server_count = 0
    byte_offset = 0

    for byte in data:
        if byte_offset >= int(len(data) / server) + 1:
            server_count = server_count + 1
            byte_offset = 0
        data_matrix[server_count][byte_offset] = byte
        byte_offset = byte_offset + 1

    return data_matrix


def GetEncodedData(encoder, data):
    encoded_matrix = numpy.matmul(encoder, data)
    return encoded_matrix


def DecodeData(encoder, data, order):
    encoder_altered = [[0.0]*len(encoder[0])]*len(encoder[0])
    data_altered = [[0]*len(data[0])]*len(encoder[0])
    count = 0
    for value in order:
        encoder_altered[count] = encoder[value]
        data_altered[count] = data[value]
        count = count + 1
    encoder_altered = numpy.linalg.inv(encoder_altered)
    decoded_matrix = numpy.matmul(encoder_altered, data_altered)
    decoded_bytes = bytearray()
    for row in decoded_matrix:
        for byte in row:
            decoded_bytes.append(int(round(byte)))
    return decoded_bytes.replace(b"\x00", b"")



