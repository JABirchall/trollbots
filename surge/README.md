![logo.gif](screens/logo.gif?raw=true "logo.gif")

A Socks5 clone flooder for the Internet Relay Chat (IRC) protocol.

##### Requirements
- [PySocks](https://pypi.python.org/pypi/PySocks)

The `socks.py` file is already included in the source, but new version may be released in the future.

You can `pip install` the library required or just download and copy `socks.py` into the same directory as `surge.py`.

##### Flood Attacks
- Action
- Color
- CTCP Channel / CTCP Nick *(PING, TIME, VERSION)*
- Cycle *(Join/Part)*
- Hilight
- Invite
- Message / Private Message
- Nick
- Notice
- Topic

The script uses IRC numeric detection and will stop a specific flood type if it becomes blocked.
If the channel becomes locked out due to a ban or specific mode, it will continue to flood the nicklist.

##### Configuration
Update your proxies list in `proxies.txt` frequently for better floods.

Make sure you edit the `config.py` file to change some of the surge settings.

You will have to tweak the throttle settings if you keep getting an excess flood kill.

##### Todo
- Add DCC flooding support.
- Detect channel modes on join to remove specific attack methods.
- Use a global variable for attack methods.
- Parse the nicklist on the first successful connection so clones are not CTCP/PM flooded.
- Calculate the message size subtracted from the max message length and make the rest random.
- Randomize the invite channel every 60 seconds.
- Use a main bot connection to recieve PM's from the bots when the channel is +i to invite / relay the nicklist.

##### Screens
![flood.png](screens/flood.png?raw=true "flood.png")
