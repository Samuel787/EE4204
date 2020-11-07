import socket
import time
import os
import random
from string import ascii_letters
import copy

PORT = [i for i in range(5000, 5050, 1)]
HOST = "127.0.0.1"
FILE_TO_SENT = "final.txt"
POSITIVE_ACK = "pack"
NEGATIVE_ACK = "nack"
ACK_SIZE = 5
PACKET_SIZE = 256
CRC = "10110100101011111011010010101111"
CORRUPT_INTENSITY = 0.05 # fix this at 0.05
ERROR_PROBABILITY = 0
PACKET_LOSS_PROBABILITY = 0

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

def encodeData(data, key): 
    l_key = len(key)  
    appended_data = data + '0'*(l_key-1) 
    remainder = mod2div(appended_data, key) 
    codeword = data + remainder 
    return codeword

def SendFile():
    global_counter = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(True)
    try:
        s.connect((HOST, PORT[0]))
    except Exception as e:
        print(e)
        s.connect((HOST, PORT[1]))

    ack_num = 0
    file_size_correctly_sent = False
    while not file_size_correctly_sent:
        file_size = os.path.getsize(FILE_TO_SENT)
        filesize = str(file_size)
        filesize = encodeData(filesize, CRC)
        if PRINT_ENABLED:
            print(f"Sending file size msg: {filesize}")
        filesize = pre_process_before_send(filesize, CORRUPT_INTENSITY, ERROR_PROBABILITY)
        filesize = filesize.encode("utf-8")
        s.send(filesize)
        while True:
            ack = s.recv(ACK_SIZE)
            ack = ack.decode("utf-8")
            ack_num_received = int(ack[-1])
            ack = ack[0:4]
            if ack == POSITIVE_ACK and ack_num_received == (ack_num % 10):
                if PRINT_ENABLED:
                    print("Received Positive Ack")
                file_size_correctly_sent = True
                ack_num += 1
                break
            elif ack == NEGATIVE_ACK and ack_num_received == (ack_num % 10):
                if PRINT_ENABLED:
                    print("Received Negative Ack")
                file_size_correctly_sent = False
                ack_num += 1
                break
            else:
                print(f"Should never enter this state. Ack num: {ack_num}")
        global_counter += 1
        if PRINT_ENABLED:
            print(str(global_counter))

    sent_size = 0
    with open(FILE_TO_SENT, "rb") as f:
        while sent_size < file_size:
            file_content_correctly_sent = False
            bytesToSend = f.read(PACKET_SIZE - len(CRC) + 1)
            if PRINT_ENABLED:
                print(f"bytesToSend: {bytesToSend}")
            temp = copy.copy(bytesToSend)
            while not file_content_correctly_sent:
                if temp == "":
                    break
                bytesToSend = encodeData(temp.decode("utf-8"), CRC)
                if PRINT_ENABLED:
                    print(f"Sending file content msg: {bytesToSend}")
                bytesToSend = pre_process_before_send(bytesToSend, CORRUPT_INTENSITY, ERROR_PROBABILITY)
                bytesToSend = bytesToSend.encode("utf-8")
                if random.random() >= PACKET_LOSS_PROBABILITY:
                    s.send(bytesToSend)
                else:
                    if PRINT_ENABLED:
                        print("Simulating packet loss")
                while True:
                    s.settimeout(0.1)
                    try:
                        ack = s.recv(ACK_SIZE)
                        ack = ack.decode("utf-8")
                        ack_num_received = int(ack[-1])
                        ack = ack[0:4]
                        print(f"Ack num received: {ack_num_received}")
                        if ack == POSITIVE_ACK and ack_num_received == (ack_num % 10):
                            ack_num += 1
                            sent_size += (PACKET_SIZE - len(CRC) + 1)
                            if PRINT_ENABLED:
                                print("Received positive Ack for content")
                            file_content_correctly_sent = True
                            break
                        elif ack == NEGATIVE_ACK and ack_num_received == (ack_num % 10):
                            ack_num += 1
                            if PRINT_ENABLED:
                                print("Received negative Ack for content")
                            file_content_correctly_sent = False
                            break
                        else:
                            print(f"Should never enter this state. Ack num: {ack_num}")
                    except Exception as e:
                        print(e)
                        print("acknowledgement time out")
                        file_content_correctly_sent = False
                        break;
                global_counter += 1
                if PRINT_ENABLED:
                    print(str(global_counter))

    print("File successfully transferred")

def pre_process_before_send(message, corrupt_intensity, error_probability):
    val = random.random()
    if val <= error_probability:
        message = corrupt_data(message, corrupt_intensity)
    return message

def corrupt_data(message, corrupt_intensity):
    new_message = ""
    for i in range(len(message)):
        if i % 10 == 0:
            new_message += random.choice(ascii_letters)
        else:
            new_message += message[i]
    return new_message

def Main():
    if(CORRUPT_INTENSITY > 1 or CORRUPT_INTENSITY < 0):
        print("CORRUPT_INTENSITY Should be between 0 and 1")
    if(ERROR_PROBABILITY > 1 or ERROR_PROBABILITY < 0):
        print("ERROR PROBABILITY shoudl be between 0 and 1")
    random.seed(time.time())
    SendFile()

if __name__ == "__main__":
    Main()