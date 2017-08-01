#!/usr/bin/env python
# SpiderWeb
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# spiderweb.py

import socket
#import socks
import ssl
import threading
import time

# Connection
server     = 'irc.server.com'
port       = 6667
proxy      = None
use_ipv6   = False
use_ssl    = False
ssl_verify = False
vhost      = None
channel    = '#spiderweb'
key        = None

# Certificate
cert_key  = None
cert_file = None
cert_pass = None

# Identity
nickname  = 'spider'
username  = 'spider'
realname  = 'CAUGHT IN THE WEB'

# Login
nickserv_password = None
network_password  = None
operator_password = None

# Other
admin_host = 'admin.host'
user_modes = None

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	print(f'{get_time()} | [!] - {msg} ({reason})')

def get_time():
	return time.strftime('%I:%M:%S')

class IRC(object):
	def __init__(self):
		self.sock = None

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((server, port))
			self.register()
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			self.event_disconnect()
		else:
			self.listen()

	def create_socket(self):
		family = socket.AF_INET6 if use_ipv6 else socket.AF_INET
		if proxy:
			proxy_server, proxy_port = proxy.split(':')
			self.sock = socks.socksocket(family, socket.SOCK_STREAM)
			self.sock.setblocking(0)
			self.sock.settimeout(15)
			self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
		else:
			self.sock = socket.socket(family, socket.SOCK_STREAM)
		if vhost:
			self.sock.bind((vhost, 0))
		if use_ssl:
			self.sock = ssl.wrap_socket(self.sock, keyfile=cert_key, certfile=cert_file)

	def event_connect(self):
		if user_modes:
			self.mode(nickname, '+' + user_modes)
		if nickserv_password:
			self.identify(username, nickserv_password)
		self.oper(username, operator_password)

	def event_disconnect(self):
		self.sock.close()
		time.sleep(10)
		self.connect()

	def event_nick_in_use(self):
		raise SystemExit(f'{get_time()} | [!] - spiderweb is already running!')

	def event_oper(self):
		self.join(channel)

	def event_part(self, nick, host, chan):
		if chan == channel and host != admin_host:
			self.raw(f'SAJOIN {nick} {chan}')
			self.sendmsg(chan, 'HA HA HA! IM A BIG ASSHOLE SPIDER AND {nick} IS CAUGHT IN MY SPIDER WEB!!!')

	def handle_events(self, data):
		args = data.split()
		if line.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			self.event_connect()
		elif args[1] == '381':
			self.event_oper()
		elif args[1] == '433':
			self.event_nick_in_use()
		elif args[1] == 'PART':
			nick = args[0].split('!')[0][1:]
			host = args[0].split('!')[1].split('@')[1]
			chan = args[2]
			self.event_part(nick, host, chan)

	def identify(self, nickname, password):
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
				for line in (line for line in data.split('\r\n') if line):
					debug(line)
					if len(line.split()) >= 2:
						self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		self.event_disconnect()

	def oper(self, username, password):
		self.raw(f'OPER {username} {password}')

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def register(self):
		if network_password:
			self.raw('PASS ' + network_password)
		self.raw(f'USER {username} 0 * :{realname}')
		self.nick(nickname)

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

IRC().connect()