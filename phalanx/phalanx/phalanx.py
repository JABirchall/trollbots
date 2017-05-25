#!/usr/bin/env python
# Phalanx (Clone PM Flooder)
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# phalanx.py

'''
For people using UnrealIRCd, change the follow for however many clones you want connected at most:
    - maxclients in the class block for <ip_address>
    - maxperip   in the allow block for <ip_address>
    - maxlogins  in the oper  block for the clones.
    Note: Replace <ip_address> with the IP address of the clones.

For people using Anope services, do /msg operserv exception add <ip_address> <max> Phalanx
Note: Replace <ip_address> with the IP address of the clones and <max> to however many clones you want to connected at most.
'''

import random
import socket
import ssl
import string
import threading
import time

# Connection
server   = 'irc.server.com'
port     = 6667
use_ipv6 = False
use_ssl  = False
vhost    = None
password = None

# Admin
oper_username = 'CHANGEME'
oper_password = 'CHANGEME'

# Other
clones = 50
target = 'CHANGEME' # The target nickname to PM flood.

def debug(msg):
    print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
    if reason:
        print(f'{get_time()} | [!] - {msg} ({reason})')
    else:
        print(f'{get_time()} | [!] - {msg}')

def get_time():
    return time.strftime('%I:%M:%S')

def random_int(min, max):
    return random.randint(min, max)

def random_str(size):
    return ''.join(random.sample((string.ascii_letters), size))

class IRC(threading.Thread):
    def __init__(self):
        self.nickname = None
        self.username = None
        self.realname = None
        self.sock     = None
        threading.Thread.__init__(self)

    def run(self):
        self.connect()

    def connect(self):
        try:
            self.nickname = random_str(random_int(5,6))
            self.username = random_str(random_int(5,6))
            self.realname = random_str(random_int(5,6))
            self.create_socket()
            self.sock.connect((server, port))
            if password:
                self.raw('PASS ' + password)
            self.raw(f'USER {self.username} 0 * :{self.realname}')
            self.nick(self.nickname)
        except socket.error as ex:
            error('Failed to connect to IRC server.', ex)
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if use_ipv6:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if vhost:
            self.sock.bind((vhost, 0))
        if use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def event_connect(self):
        self.oper(oper_username, oper_password)

    def event_disconnect(self):
        time.sleep(random_int(3,5))
        self.sock.close()
        self.connect()

    def event_nick_in_use(self):
        self.nickname = random_str(random_int(5,6))
        self.nick(self.nickname)

    def event_oper(self):
        self.raw('SETHOST ' + random_str(random_int(5,10)))
        time.sleep(1)

    def event_sethost():
        self.sendmsg(target, random_str(random_int(2,5)))
        debug(f'Sent a private message to {target}!')
        self.event_disconnect()

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '381':
            self.event_oper()
        elif args[1] == '396':
            self.event_sethost()
        elif args[1] == '433':
            self.event_nick_in_use()

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in (line for line in data.split('\r\n') if line):
                        if len(line.split()) >= 2:
                            if line.startswith('ERROR :Closing Link:'):
                                raise Exception('Connection has closed.')
                            else:
                                self.handle_events(line)
                else:
                    error('No data recieved from server.')
                    break
            except (UnicodeDecodeError,UnicodeEncodeError):
                pass
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def oper(self, nick, password):
        self.raw(f'OPER {nick} {password}')

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw(f'PRIVMSG {target} :{msg}')

# Main
for i in range(clones):
    clone().start()
    time.sleep(0.5)
try:
    while True:
        input('')
except KeyboardInterrupt:
    sys.exit()
