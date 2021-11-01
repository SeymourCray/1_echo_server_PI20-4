#!/usr/bin/env python3

import socket
import getpass
import re


DEF_HOST = '127.0.0.1'  # The server's hostname or IP address
DEF_PORT = 65432        # The port used by the server


def user_conf():
    ip = re.search(r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', getpass.getpass(
        prompt='enter ip u want to connect: '))
    ip = ip.group() if ip else DEF_HOST
    port = getpass.getpass(
        prompt='enter port u want to connect: ')
    port = int(port) if port != '' else DEF_PORT
    port = port if -1 < port < 65537 else DEF_PORT
    return ip, port


def send_(sock, message):
    text = bytearray(f'{message}\t({len(message)})'.encode('utf-8'))
    sock.send(text)


def recv_(sock):
    text = sock.recv(1024)
    if text:
        return text.decode('utf-8')
    else:
        return False


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    ip, port = user_conf()
    try:
        s.connect((ip, port))  # connect to server
        print('connection with server was successfull')
    except:
        print('Connection can not be complete')
        exit()
    try:
        while True:
            sign = s.recv(1024).decode()
            if 'check' in sign:
                s.send(
                    input(f'Enter your password user {sign.split()[1]}: ').encode())
            elif 'name' in sign:
                s.send(input('Enter your name: ').encode())
            elif 'password' in sign:
                s.send(input('Enter your password: ').encode())
            else:
                print(sign)
                break
        while True:
            # enter the text we want to send to server
            text = str(input('write text: '))
            if text == 'exit':
                s.send('exit'.encode())
                break

            send_(s, text)
            print('we are sending data!')           # encode text to bytes
            data = recv_(s)             # get data in bytes from server
            print('we are received data!')
            # decode and output data from server
            print(data)
    except:
        print('connection was lost')
