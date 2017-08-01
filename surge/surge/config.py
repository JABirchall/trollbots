#!/usr/bin/env python
# Surge
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# config.py

class connection:
	server    = 'irc.server.com'
	port      = 6667
	ipv6      = False
	ssl       = False
	password  = None
	channel   = '#chats'
	key       = None

class attacks:
	channel  = ['action','color','ctcp','msg','nick','notice','part','topic']
	message  = 'SURGE SURGE SURGE SURGE SURGE'
	nicklist = ['ctcp','invite','notice','private']

class throttle:
	attack      = 3   # Delay between each attack method sent.
	concurrency = 3   # Number of concurrent connections per-proxy.
	threads     = 100 # Maximum number of threads running at one time.
	rejoin      = 3   # Delay to rejoin a channel after kick.
	timeout     = 15  # Seconds before timing out on a connection.