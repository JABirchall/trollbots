#!/usr/bin/env python
# EFknockr (EFK)
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# config.py

# IRC Settings
nickname     = 'EFknockr'
part_message = 'Smell ya l8r'
proxy        = None # Proxy should be a Socks5 in IP:PORT format.
vhost        = None
servers      = {
    'irc.server1.com' : {'port':6667, 'ipv6':False, 'ssl':False, 'password':None, 'channels':['#channel1','#channel2','#channel3']},
    'irc.server2.com' : {'port':6667, 'ipv6':False, 'ssl':False, 'password':None, 'channels':['#channel1','#channel2','#channel3']},
    'irc.server3.com' : {'port':6667, 'ipv6':False, 'ssl':False, 'password':None, 'channels':None}, # Setting 'channels' to None will crawl the entire output of /list on the given server.
}

# Attack / Throttle Settings
exploit          = True # Send a DCC exploit after sending messages. (https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-8073)
join_throttle    = 3    # Delay between each channel join.
mass_hilite      = True # Toggle sending a mass hilite before parting a channel.
max_channels     = 3    # Maximum number of channels to be flooding at once.
max_threads      = 100  # Maximum number of threads running.
minimum_users    = 10   # When crawl is enabled, only join channels with this minimum amount of users or more.
message_throttle = 0.5  # Delay between each line sent to the channel.
timeout          = 10   # Timeout for all sockets.

# Bad IRC Events (DO NOT EDIT)
bad_msgs = (
    'Color is not permitted',
    'No external channel messages',
    'You need voice',
    'You must have a registered nick'
)

bad_numerics = {
    '471' : 'ERR_CHANNELISFULL',
    '473' : 'ERR_INVITEONLYCHAN',
    '474' : 'ERR_BANNEDFROMCHAN',
    '475' : 'ERR_BADCHANNELKEY',
    '477' : 'ERR_NEEDREGGEDNICK',
    '489' : 'ERR_SECUREONLYCHAN',
    '519' : 'ERR_TOOMANYUSERS',
    '520' : 'ERR_OPERONLY'
}