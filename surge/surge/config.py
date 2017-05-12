#!/usr/bin/env python
# Surge IRC Channel Flooder
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/trollbots
# config.py

# Connection
server    = 'irc.server.com'
port      = 6667
use_ipv6  = False
use_ssl   = False
password  = None
channel   = '#chats'
key       = None

# Attack
message     = 'SURGE SURGE SURGE SURGE SURGE' # Use 'random' for randomized messages.
use_unicode = True
use_color   = True

# Throttle
attack_delay           = 3   # Delay between each attack method sent.
concurrent_connections = 3   # Number of concurrent connections per-proxy.
max_threads            = 100 # Maximum number of threads running at one time.
rejoin_delay           = 1   # Delay to rejoin a channel after kick.
timeout                = 15  # Seconds before timing out on a connection.

# Bad IRC Numerics
bad_numerics = (
    '465', # ERR_YOUREBANNEDCREEP
    '471', # ERR_CHANNELISFULL
    '473', # ERR_INVITEONLYCHAN
    '474', # ERR_BANNEDFROMCHAN
    '475', # ERR_BADCHANNELKEY
    '477', # ERR_NEEDREGGEDNICK
    '519'  # ERR_TOOMANYUSERS
)