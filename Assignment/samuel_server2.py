import socket
import threading
import os
import time

POSITIVE_ACK = "pack"
NEGATIVE_ACK = "nack"
PORT = [i for i in range(5000, 5050, 1)]
HOST = "127.0.0.1"
ACK_SIZE = 5
PACKET_SIZE = 256
CRC = "10110100101011111011010010101111"

PRINT_ENABLED = True

def xor(a, b): 
    result = [] 
    for i in range(1, len(b)): 
        if a[i] == b[i]: 
            result.append('0') 
        else: 
            result.append('1') 
    return ''.join(result) 

def mod2div(divident, divisor): 
    pick = len(divisor)  
    tmp = divident[0 : pick] 
    while pick < len(divident): 
        if tmp[0] == '1': 
            tmp = xor(divisor, tmp) + divident[pick] 
        else:
            tmp = xor('0'*pick, tmp) + divident[pick] 
        pick += 1
    if tmp[0] == '1': 
        tmp = xor(divisor, tmp) 
    else: 
        tmp = xor('0'*pick, tmp) 
    checkword = tmp 
    return checkword 
   
def decodeData(data, key): 
    l_key = len(key) 
    appended_data = data + '0'*(l_key-1) 
    remainder = mod2div(appended_data, key) 
    return remainder 

def RecvFile(sock):
    global_counter = 0
    start_time = time.time()
    file_size_correctly_received = False
    ack_num = -1
    while not file_size_correctly_received:
        file_size = sock.recv(1024)
        try:
            file_size = file_size.decode("utf-8")
            if PRINT_ENABLED:
                print(f"Received file size {file_size}")
            remainder = decodeData(file_size, CRC)
            if int(remainder) != 0:
                raise Exception("file size received wrongly")
            file_size = file_size[:-(len(CRC) - 1)]
            file_size = int(file_size)
            if file_size < 0:
                raise Exception("file size cannot be negative")
            file_size_correctly_received = True
            if PRINT_ENABLED:
                print(f"THE FILE SIZE IS {file_size}")
            sock.send((POSITIVE_ACK + str((ack_num + 1) % 10)).encode("utf-8"))
            ack_num += 1
            if PRINT_ENABLED:
                print("Sent positive ack for file size")
        except Exception as e:
            print("Exception in receiving file size")
            print(e)
            file_size_correctly_received = False
            sock.send((NEGATIVE_ACK + str((ack_num + 1) % 10)).encode("utf-8"))
            ack_num += 1
            print("Sent negative ack for file size")
        global_counter += 1
        if PRINT_ENABLED:
            print(str(global_counter))

    received_size = 0
    f = open("Received_file.txt", "wb")
    while received_size < file_size:
        file_content_correctly_received = False
        while not file_content_correctly_received:
            data = sock.recv(PACKET_SIZE)
            if data:
                data = data.decode("utf-8")
                if PRINT_ENABLED:
                    print(f"Received: {data}")
                crc_header = data[-(len(CRC) - 1):]
                if PRINT_ENABLED:
                    print(f"crc header: {crc_header}")
                crc_header_valid = check_crc_addition(crc_header)
                remainder = decodeData(data, CRC)
                if crc_header_valid and int(remainder) == 0:
                    file_content_correctly_received = True
                if file_content_correctly_received:
                    data = data[:-(len(CRC) - 1)]
                    received_size += PACKET_SIZE - len(CRC) + 1#len(data)
                    if PRINT_ENABLED:
                        print(f"Received this much data so far: {received_size}")
                    f.write(data.encode("utf-8"))
                    if PRINT_ENABLED:
                        print("Sending Positive Ack")
                    sock.send((POSITIVE_ACK + str((ack_num + 1) % 10)).encode("utf-8")) 
                    ack_num += 1
                else:
                    if PRINT_ENABLED:
                        print("Sending Negative Ack")
                    sock.send((NEGATIVE_ACK + str((ack_num + 1) % 10)).encode("utf-8"))
                    ack_num += 1
                global_counter += 1
                if PRINT_ENABLED:
                    print(str(global_counter))
                    print("\n")           

    end_time = time.time()
    print("File successfully received complete")
    through_put = calculate_throughput(file_size, (end_time - start_time))
    f.close()

# in Mbps
def calculate_throughput(file_size, transfer_time):
    through_put = (file_size * 8 / transfer_time) / 1000000
    print(f"Transfer time: {transfer_time}s")
    print(f"Through_put: {through_put}")
    return through_put


def check_crc_addition(crc_header):
    for i in range(len(crc_header)):
        if crc_header[i] != '1' and crc_header[i] != '0':
            if PRINT_ENABLED:
                print(f"false crc header detected {crc_header[i]}")
            return False
    return True

def Main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, PORT[0]))
    except Exception as e:
        print(e)
        s.bind((HOST, PORT[1]))
    print("Server started.")
    s.listen(1)

    c, addr = s.accept()
    print(f"Client connected ip: {addr}")
    RecvFile(c)
    s.close()

if __name__ == "__main__":
    Main()

