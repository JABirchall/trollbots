# badparent
A script to PM flood nicks in a channel on IRC.

##### Requirements
- [PySocks](https://pypi.python.org/pypi/PySocks)

The `socks.py` file is already included in the source, but new versions may be released in the future.

You can `pip install` the library required or just download and copy `socks.py` into the same directory as `badparent.py`.

##### Information
The parent bot will join a channel, parse the entire nicklist, and maintain it during joins, quits, nick changes, etc.

The child bot clones will use either proxies or virtual hosts to connect and PM the nicklist.

Nicks that have the usermode +g *(callerid)*, +D *(privdeaf)*, and +R *(regonlymsg)* will be removed from the nicklist.

##### Configuration
Make sure you edit the `config.py` file to change some of the badparent settings.

You will have to tweak the throttle settings if you keep getting an excess flood kill.