#!/usr/bin/env python3
import os
import socket
import getpass
import csv


class Server():

    key = 'sglypa'

    filename = 'log.txt'

    for_users = 'saved_users.csv'

    log_text = {1: 'server is starting', 2: 'port is listened',
                3: 'connection was successfull', 4: 'i got data!',
                5: 'client was disconnected', 6: 'server was turned off', 7: 'I changed port'}

    Def_HOST = '127.0.0.1'  # Standard loopback interface address (localhost)

    Def_PORT = 65432    # Port to listen on (non-privileged ports are > 1023)

    all_commands = ['listen', 'off', '?']

    def __init__(self, open_port, host):
        self.open_port = open_port
        self.host = host

    def change_port(self, port):
        self.open_port = port

    @staticmethod
    def log(code):
        with open(Server.filename, 'a') as file:
            file.write(Server.log_text[code]+'\n')

    @staticmethod
    def ident(ip, sock):
        table = []
        with open(Server.for_users) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                table.append(row)
        for i, row in enumerate(table):
            if row[0] == ip:
                if row[3] == 'True':
                    sock.send(f'Hello user {row[1]}'.encode())
                    break
                else:
                    while True:
                        sock.send(f'check {row[1]}'.encode())
                        answer = sock.recv(1024).decode()
                        data = Server.vernam_enc_dec(
                            Server.key, answer)
                        if data == row[2]:
                            sock.send(f'Hello user {row[1]}'.encode())
                            table[i][3] = 'True'
                            break
                    break
        else:
            sock.send('name'.encode())
            name = sock.recv(1024).decode()
            sock.send('password'.encode())
            answer = sock.recv(1024).decode()
            password = Server.vernam_enc_dec(
                Server.key, answer)
            sock.send(f'Hello user {name}'.encode())
            table.append([ip, name, password, 'True'])
        with open(Server.for_users, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(table)

    @staticmethod
    def vernam_enc_dec(k, m):
        k = k*(len(m)//len(k)) + k[-(len(m) % len(k)):]
        return ''.join(map(chr, [i ^ x for i, x in zip(map(ord, m), map(ord, k))]))

    def run(self):
        Server.log(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    # bind our socket to the given host and port
                    s.bind((Server.Def_HOST, self.open_port))
                    break
                except:
                    self.change_port(self.open_port+1)
                    Server.log(7)
            while True:
                command = input('enter the command: ')
                if command == 'off':
                    Server.log(6)
                    raise SystemExit
                elif command == '?':
                    print(' '.join(Server.all_commands))
                elif command == 'listen':
                    s.listen()
                    Server.log(2)
                    print(f'listen {self.open_port}')
                    conn, addr = s.accept()  # new socket and client address
                    Server.log(3)
                    Server.ident(addr[0], conn)
                    with conn:
                        while True:
                            text = Server.recv_(conn)
                            if text == 'exit':
                                table = []
                                with open(Server.for_users, 'r') as file:
                                    reader = csv.reader(file, delimiter=',')
                                    for i, row in enumerate(reader):
                                        table.append(row)
                                        if row[0] == addr[0]:
                                            table[i][3] = 'False'
                                            break
                                with open(Server.for_users, 'w') as file:
                                    writer = csv.writer(file, delimiter=',')
                                    writer.writerows(table)
                            elif text:
                                Server.send_(conn, text)
                            else:
                                break

    @staticmethod
    def start_program():
        if Server.for_users in os.listdir(os.getcwd()):
            pass
        else:
            a = open(Server.for_users, 'w')
            a.close()
        user_port = getpass.getpass(
            prompt="Enter port u want to use: ", stream=None)
        user_port = int(user_port) if user_port != '' else Server.Def_PORT
        user_port = user_port if 1 < user_port < 65537 else Server.Def_PORT
        a = Server(user_port, Server.Def_HOST)
        a.run()

    @staticmethod
    def send_(sock, message):
        text = bytearray(f'{message}\t({len(message)})'.encode('utf-8'))
        sock.send(text)

    @staticmethod
    def recv_(sock):
        text = sock.recv(1024)
        if text:
            Server.log(4)
            print(text.decode('utf-8'))
            text = text.decode('utf-8').split('\t')[0]
            return text
        else:
            Server.log(5)
            return False


if __name__ == '__main__':
    Server.start_program()
