# Tango

> A modern, fast, headerless, object-oriented, adn scalable Chatango botting library

**Requirements:** Python 2.7.x, requests, tornado (web framework)

### Installation

1. Install Python 2.7.x
2. Install requests via 'pip install requests'
3. Install tornado (web framework) via 'pip install tornado'
4. Extract tango module folder to your desired location

### Foreword

> The Tango (Chatango.com) botting library was created by myself (Frowdo) and was created to replace the now obsolete ch.py module. It's built to be quick, scalable and object-oriented so you can focus on bot building and not repairing bad code.

### Usage

> To begin, the tango module (tango.py), contains the base class for building your Chatango bots. Think of it as the protocol that you build your bots upon. The bots module (bots.py), contains a fully-featured Chatango bot that you can use or get examples from. This bot is called *TrolltangoWebSocketClient* and works out of the box. Run the example.py file to see it in action!

**Building new bots:**

Your bots should inherit the **tango.WebSocketClient** base class (unless you feel the need to build your own base class). 

Here's an example:

```
from tango import tango

class MyBot(tango.WebSocketClient):
    def __init__(self):
        tango.WebSocketClient.__init__(self)
        # self.headers contains a list of packet handlers.
        # These packet handlers define how the bot should
        # process the information given to it by knowning its
        # type (or header).
        self.headers = {
            "ok": self.on_auth_response,
        }
    def initial_auth_data(self):
        """Sends initial login (auth) request to Chatango WebSocket server."""
        self.send(b'v\r\n\x00')
            self.send(
                b'bauth:{0}:{1}:{2}:{3}\r\n\x00'.format(
                    self.host,
                    self.uid,
                    self.account.sid,
                    self.account.pwd
                )
            )
    def on_auth_response(self, msg):
        """Called when an authentication reponse is returned by the Chatango WebSocket server."""
        print msg
    def on_message(self, header, msg):
        """Called when we receive a message from the Chatango WebSocket server."""
        if self.headers.has_key(header):
            func = self.headers[header]
            func(msg)
        else:
            print "Unrecognized header received:", header, "with payload", payload
    def on_connection_success(self):
        print "Connected to Chatango WebSocket server!"
        self.initial_auth_data()
    def on_connection_close(self):
        print "Lost connection to Chatango WebSocket server!"
    def on_connection_error(self, exception):
        print "Experienced error in Chatango WebSocket server:", exception



def main():
    """Starts up our test Chatango Bot (class: bots.TrolltangoWebSocketClient).
    """

    # Direct http URL address to target Chatango website (important: must be in the format of "http://target.chatango.com").
    # You can get the direct http URL address by navigating to a website that contains a Chatango chat room, and clicking on # the widgets header area. It should redirect you to the direct http URL address for that chatroom. When in doubt,
    # use the following example: suppose you visit http://website.com. You notice theres a Chatango chat room there. 
    # Try navigating to "http://website.chatango.com" and see if it works. If so, then use that as the direct http URL
    # address!
    host = "http://nba-stream.chatango.com"
    client = MyBot()
    client.account = tango.Account(host, "YOURCHATANGOUSERNAME", "YOURCHATANGOPASSWORD")
    client.connect(host)

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        client.close()


if __name__ == "__main__":
    main()
```

The example above is an rough example of a Chatango Bot that connects to the specified Chatango website, logs in, and does nothing afterwards. You should really use the **bots.TrolltangoWebSocketClient()** class as a real-world example of how you should create your bots.

**Note:** Be mindful of what you name your bots global instance variables. As overwriting key variables will cause problems. Refer to class: tango.WebSocketClient to view the naming conventions of its global instance variables.

