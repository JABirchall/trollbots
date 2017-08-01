#!/usr/bin/env python
# EFknockr (EFK)
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# config.py

class connection:
	proxy = None
	vhost = None

class ident:
	nickname = 'EFknockr'
	username = 'efk'
	realname = 'EFknockr IRC Bot'

class settings:
	mass_hilite = True
	part_msg    = 'Smell ya l8r'

class throttle:
	join     = 3   # Delay between each channel join.
	channels = 3   # Maximum number of channels to be flooding at once.
	threads  = 100 # Maximum number of threads running.
	users    = 10  # When crawl is enabled, only join channels with this minimum amount of users or more.
	message  = 0.5 # Delay between each line sent to the channel.
	timeout  = 10  # Timeout for all sockets.

targets = {
	'irc.server1.com' : {'port':6667, 'ipv6':False, 'ssl':False, 'password':None, 'channels':['#channel1','#channel2','#channel3:keyhere']},    # Channels can be read from a list. (Keys places after channel name.)
	'irc.server3.com' : {'port':6667, 'ipv6':False, 'ssl':False, 'password':None, 'channels':open('/home/acidvegas/channels.txt').readlines()}, # Channels can be read from a text file.
	'irc.server4.com' : {'port':6667, 'ipv6':False, 'ssl':False, 'password':None, 'channels':None}                                              # Setting channels to None will crawl all channels.
}