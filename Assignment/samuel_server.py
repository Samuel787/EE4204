import socket
import threading
import os
import time

POSITIVE_ACK = "pack".encode("utf-8")
NEGATIVE_ACK = "nack".encode("utf-8")
PORT = [5000, 5001]
HOST = "127.0.0.1"

def RecvFile(sock):
    file_size_correctly_received = False
    while not file_size_correctly_received:
        file_size = sock.recv(1024)
        try:
            file_size = int(file_size.decode("utf-8"))
            if file_size < 0:
                raise Exception("file size cannot be negative")
            file_size_correctly_received = True
            sock.send(POSITIVE_ACK)
            print("Sent positive ack for file size")
        except Exception as e:
            print("Exception in receiving file size")
            print(e)
            sock.send(NEGATIVE_ACK)
            print("Sent negative ack for file size")

    received_size = 0
    f = open("Received_file", "wb")
    while received_size < file_size:
        msg_correctly_received = False
        while not msg_correctly_received:
            data = sock.recv(1024)
            # do some checking of the message
            msg_correctly_received = True
            if msg_correctly_received:
                received_size += len(data)
                f.write(data)
                print("Sending Positive Ack")
                sock.send(POSITIVE_ACK)
            else:
                print("Sending Negative Ack")
                sock.send(NEGATIVE_ACK)
    print("File successfully received complete")
    f.close()

def Main():
    s = socket.socket()
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
