from tango import *

from tornado import ioloop


def main():
    """Starts up our test Chatango Bot (class: bots.TrolltangoWebSocketClient).
    """

    host = "http://nba-stream.chatango.com"
    client = bots.TrolltangoWebSocketClient()
    client.account = tango.Account(host, "YOURCHATANGOUSERNAME", "YOURCHATANGOPASSWORD")
    client.connect(host)

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
