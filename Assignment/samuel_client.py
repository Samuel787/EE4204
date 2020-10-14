import socket
import time
import os

PORT = [5000, 5001]
HOST = "127.0.0.1"
FILE_TO_SENT = "sample.txt"
POSITIVE_ACK = "pack".encode("utf-8")
NEGATIVE_ACK = "nack".encode("utf-8")

def SendFile():
    s = socket.socket()
    try:
        s.connect((HOST, PORT[0]))
    except Exception as e:
        print(e)
        s.connect((HOST, PORT[1]))

    filesize = str(os.path.getsize(FILE_TO_SENT))
    filesize = filesize.encode("utf-8")
    file_size_correctly_sent = False
    while not file_size_correctly_sent:
        s.send(filesize)
        ack = s.recv(4)
        if ack == POSITIVE_ACK:
            print("Received Positive Ack")
            file_size_correctly_sent = True
        elif ack == NEGATIVE_ACK:
            print("Received Negative Ack")
            file_size_correctly_sent = False
        else:
            print("Should never enter this state")


    with open(FILE_TO_SENT, "rb") as f:
        bytesToSend = f.read(1024)
        while bytesToSend.decode("utf-8") != "":
            msg_correctly_sent = False
            while not msg_correctly_sent:
                print("Attempting to send data")
                s.send(bytesToSend)
                bytesToSend = f.read(1024)
                ACK = s.recv(4)
                if ACK == POSITIVE_ACK:
                    print("Received Positive Ack")
                    msg_correctly_sent = True
                elif ACK == NEGATIVE_ACK:
                    print("Received Negative Ack")
                    msg_correctly_sent = False
                else:
                    print("Should never enter this state")

    print("File successfully transferred")


def Main():
    SendFile()

if __name__ == "__main__":
    Main()