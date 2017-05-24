#!/usr/bin/env python
# SpiderWeb
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# spiderweb.py

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
channel  = '#spiderweb'
key      = None

# Identity
nickname = 'spider'
username = 'spider'
realname = 'CAUGHT IN THE WEB'

# Login
nickserv    = None
oper_passwd = 'CHANGEME'

# Other
admin_host = 'admin.host'

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
        self.sock = None

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

    def event_disconnect(self):
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_nick_in_use(self):
        self.error_exit('spiderweb is already running!')

    def event_part(self, nick, host, chan):
        self.raw(f'SAJOIN {nick} {chan}')
        self.sendmsg(chan, self.color(f'HA HA HA! IM A BIG ASSHOLE SPIDER AND {nick} IS CAUGHT IN MY SPIDER WEB!!!', red))

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == 'PART':
            nick = args[0].split('!')[0][1:]
            if nick != nickname:
                host = args[0].split('!')[1].split('@')[1]
                chan = args[2]
                if chan == channel and host != admin_host:
                    self.event_part(nick, host, chan)

    def identify(self, username, password):
        self.sendmsg('nickserv', f'recover {nickname} {password}')
        self.sendmsg('nickserv', f'identify {nickname} {password}')

    def join(self, chan, key=None):
        if key:
            self.raw(f'JOIN {chan} {key}')
        else:
            self.raw('JOIN ' + chan)

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