# badparent
A Socks5 clone flooder for the Internet Relay Chat (IRC) protocol.

##### Requirements
- [PySocks](https://pypi.python.org/pypi/PySocks)

The `socks.py` file is already included in the source, but new versions may be released in the future.

You can `pip install` the library required or just download and copy `socks.py` into the same directory as `badparent.py`.

##### Information
The main bot will join a channel and parse the entire nicklist / maintain it during quits and nick changes.

That parent bot will create children bot clones using proxies that just connect and flood the nicks from the list.

The floods include CTCP *(PING, TIME, VERSION)*, Invite, and Private Message attacks.

Clones will join a random channel and invite the nicklist. After an amount of invites defined in `config.py`, it will part that channel and join another random channel.

##### Configuration
Update your proxies list in `proxies.txt` frequently for better floods.

Make sure you edit the `config.py` file to change some of the badparent settings.

You will have to tweak the throttle settings if you keep getting an excess flood kill.

##### Todo
Look at the following lines to handle floods more precisely.
```
:irc.server.com 482 CHILD #radnom :You're not channel operator
:irc.server.com 486 CHILD :You must identify to a registered nick to private message NICK
:irc.server.com 492 CHILD :NICK does not accept CTCPs
:irc.server.com 518 CHILD :Cannot invite (+V) at channel #random
:irc.server.com 716 CHILD NICK :is in +g mode (server-side ignore.)
```