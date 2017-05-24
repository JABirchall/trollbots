#!/usr/bin/env python
# SAJOIN Flood IRC Bot
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# 5000.py

import random
import socket
import ssl
import threading
import time

# Connection
server   = 'irc.server.com'
port     = 6667
use_ipv6 = False
use_ssl  = False
vhost    = None
password = None
channel  = '#chats'
key      = None

# Identity
nickname = 'FUCKYOU'
username = '5000'
realname = 'I CAN SHOW YOU THE WORLD'

# Login
nickserv    = None
oper_passwd = 'CHANGEME'

# Flood Control
cmd_throttle    = 3    # Delay between command usage.
max_nicks       = 5    # Maximum number of nicks that can be 5000'd at once.
sajoin_throttle = 0.03 # Delay between each SAJOIN.

# Other
admin_hosts = ('admin.host','another.admin.host')

def debug(msg):
    print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
    if reason:
        print(f'{get_time()} | [!] - {msg} ({reason})')
    else:
        print(f'{get_time()} | [!] - {msg}')

def error_exit(msg):
    raise SystemExit(f'{get_time()} | [!] - {msg}')

def get_time():
    return time.strftime('%I:%M:%S')

def random_int(min, max):
    return random.randint(min, max)

def random_str(size):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', size))

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

class IRC(object):
    def __init__(self):
        self.nicklist  = list()
        self.kills     = 0
        self.last_time = 0
        self.sock      = None

    def attack(self, nick):
        try:
            if nick not in self.nicklist:
                self.nicklist.append(nick)
            self.sendmsg(channel, f'I am fucking the shit out of {nick} right now...')
            self.kills += 1
            for i in range(5000):
                if nick not in self.nicklist:
                    break
                self.raw(f'SAJOIN {nick} #{random_str(random_int(5,10))}')
                time.sleep(sajoin_throttle)
            self.kick('#5000', nick)
        except Exception as ex:
            error(f'Failed to fuck {nick}.', ex)
        finally:
            if nick in self.nicklist:
                self.nicklist.remove(nick)

    def color(self, msg, foreground, background=None):
        if background:
            return f'\x03{foreground},{background}{msg}{reset}'
        else:
            return f'\x03{foreground}{msg}{reset}'

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((server, port))
            if password:
                self.raw('PASS ' + password)
            self.raw(f'USER {username} 0 * :{realname}')
            self.raw('NICK ' + nickname)
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
        if nickserv:
            self.identify(username, nickserv)
        self.oper(username, oper_passwd)
        self.join(channel)
        self.join('#5000')

    def event_disconnect(self):
        self.nicklist = list()
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_join(self, nick, host, chan):
        if host not in admin_hosts and chan == '#5000' and len(self.nicklist) <= max_nicks:
            threading.Thread(target=self.attack,args=(nick,)).start()

    def event_message(self, nick, host, chan, msg):
        if chan.lower() == channel.lower():
            if msg == '.kills':
                if time.time() - self.last_time < cmd_throttle and host not in admin_hosts:
                    pass
                else:
                    self.sendmsg(chan, '{0}: {1}'.format(self.color('KILLS', red), self.kills))

    def event_nick_in_use(self):
        self.error_exit('5000 is already running!')

    def event_no_such_nick(self, nick):
        if nick in self.nicklist:
            self.nicklist.remove(nick)

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '401':
            nick = args[3]
            self.event_no_such_nick(nick)
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == 'JOIN':
            nick = args[0].split('!')[0][1:]
            host = args[0].split('!')[1].split('@')[1]
            if nick != nickname:
                chan = args[2][1:]
                self.event_join(nick, host, chan)
        elif args[1] == 'PRIVMSG':
            nick = args[0].split('!')[0][1:]
            host = args[0].split('!')[1].split('@')[1]
            chan = args[2]
            msg  = data.split(f'{args[0]} PRIVMSG {chan} :')[1]
            self.event_message(nick, host, chan, msg)

    def identify(self, username, password):
        self.sendmsg('nickserv', f'recover {nickname} {password}')
        self.sendmsg('nickserv', f'identify {nickname} {password}')

    def join(self, chan, key=None):
        if key:
            self.raw(f'JOIN {chan} {key}')
        else:
            self.raw('JOIN ' + chan)

    def kick(self, channel, nick, reason):
        self.raw(f'KICK {channel} {nick} {reason}')

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in (line for line in data.split('\r\n') if line):
                        debug(line)
                        if line.startswith('ERROR :Closing Link:'):
                            raise Exception('Connection has closed.')
                        elif len(line.split()) >= 2:
                            self.handle_events(line)
                else:
                    error('No data recieved from server.')
                    break
            except (UnicodeDecodeError,UnicodeEncodeError) as ex:
                pass
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def oper(self, nick, password):
        self.raw(f'OPER {nick} {password}')

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw(f'PRIVMSG {target} :{msg}')

IRC().connect()