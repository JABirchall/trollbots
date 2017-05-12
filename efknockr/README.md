# efknockr
ASCII flooder for IRC channels.

##### Requirements
- [PySocks](https://pypi.python.org/pypi/PySocks)

The `socks.py` file is already included in the source, but new versions may be released in the future.

You can `pip install` the library required or just download and copy `socks.py` into the same directory as `efknockr.py`.

##### Configuration
The bot will connect to a list of  servers, join every channel defined in the config or all the channels on the server, send the lines in `msg.txt`, then part.

Make sure you edit the `config.py` file to change some of the efknockr settings.