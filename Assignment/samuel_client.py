import socket
import time
import os
import random
from string import ascii_letters

PORT = [5000, 5001]
HOST = "127.0.0.1"
FILE_TO_SENT = "sample.txt"
POSITIVE_ACK = "pack".encode("utf-8")
NEGATIVE_ACK = "nack".encode("utf-8")
ACK_SIZE = 4
PACKET_SIZE = 256
CRC = "101101001000111"
CORRUPT_INTENSITY = 0.25
ERROR_PROBABILITY = 0.05

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
    s.setblocking(1)
    try:
        s.connect((HOST, PORT[0]))
    except Exception as e:
        print(e)
        s.connect((HOST, PORT[1]))

    file_size_correctly_sent = False
    while not file_size_correctly_sent:
        filesize = str(os.path.getsize(FILE_TO_SENT))
        filesize = encodeData(filesize, CRC)
        print(f"Sending file size msg: {filesize}")
        filesize = pre_process_before_send(filesize, CORRUPT_INTENSITY, ERROR_PROBABILITY)
        filesize = filesize.encode("utf-8")
        s.send(filesize)
        ack = s.recv(ACK_SIZE)
        if ack == POSITIVE_ACK:
            print("Received Positive Ack")
            file_size_correctly_sent = True
        elif ack == NEGATIVE_ACK:
            print("Received Negative Ack")
            file_size_correctly_sent = False
        else:
            print("Should never enter this state")
        global_counter += 1
        print(str(global_counter))

    with open(FILE_TO_SENT, "rb") as f:
        bytesToSend = "dummy".encode("utf-8")
        while bytesToSend.decode("utf-8") != "":
            bytesToSend = f.read(PACKET_SIZE - len(CRC) + 1)
            msg_correctly_sent = False
            while not msg_correctly_sent:
                print("Attempting to send data")
                bytesToSend = encodeData(bytesToSend.decode("utf-8"), CRC)
                bytesToSend = (pre_process_before_send(bytesToSend, CORRUPT_INTENSITY, ERROR_PROBABILITY).encode("utf-8"))
                s.send(bytesToSend)
                print(f"Sent: {bytesToSend.decode('utf-8')}")
                # bytesToSend = f.read(PACKET_SIZE - len(CRC) + 1)
                while True:
                    ACK = s.recv(ACK_SIZE)
                    if ACK:
                        if ACK == POSITIVE_ACK:
                            print("Received Positive Ack")
                            msg_correctly_sent = True
                            break
                        elif ACK == NEGATIVE_ACK:
                            print("Received Negative Ack")
                            msg_correctly_sent = False
                            break
                        else:
                            print("Should never enter this state")
                            continue
                global_counter += 1
                print(str(global_counter))
                print("\n")
                time.sleep(1)
    print("File successfully transferred")

def corrupt_data(message, corrupt_intensity):
    corrupt_intensity = 1 - corrupt_intensity
    new_message = ""
    for i in range(len(message)):
        val = random.random()
        if val >= corrupt_intensity:
            #print("Corrupting data")
            new_message += random.choice(ascii_letters)
        else:
            new_message += message[i]
    return new_message

def pre_process_before_send(message, corrupt_intensity, error_probability):
    val = random.random()
    if val <= error_probability:
        message = corrupt_data(message, corrupt_intensity)
    return message

def Main():
    if(CORRUPT_INTENSITY > 1 or CORRUPT_INTENSITY < 0):
        print("CORRUPT_INTENSITY Should be between 0 and 1")
    if(ERROR_PROBABILITY > 1 or ERROR_PROBABILITY < 0):
        print("ERROR PROBABILITY shoudl be between 0 and 1")
    random.seed(time.time())
    SendFile()

if __name__ == "__main__":
    Main()