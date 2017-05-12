#!/usr/bin/env python
# BadParent IRC Nicklist Flooder
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# config.py

# Connection
server    = 'irc.server.com'
port      = 6667
use_ipv6  = False
use_ssl   = False
proxy     = None # Proxy should be a Socks5 in IP:PORT format.
vhost     = None
password  = None
channel   = '#chat'
key       = None
message   = 'I have bad parents and was raised to flood on IRC.'

# Identity
nickname = 'BadParent'
username = 'badparent'
realname = 'BadParent IRC Bot'

# Attack Types
dcc     = True
ctcp    = True
invite  = True
private = True

# Throttle
attack_delay           = 1.5 # Delay between each attack method sent.
concurrent_connections = 3   # Number of concurrent connections per-proxy.
max_threads            = 100 # Maximum number of threads running at one time.
timeout                = 15  # Seconds before timing out on a connection.

# DO NOT EDIT
nicklist = list()