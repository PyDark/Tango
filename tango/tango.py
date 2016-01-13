from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket
# contains python code that emulates Chatango obfuscated JavaScript code
import emulation
# import all example bots
import bots
# for use in Session() class
import requests
# built-ins
import functools
import random
import json
import time


__author__ = "Frowdo"
__description__ = "Connects to Chatango's WebSocket using the Tornado framework."
__requirements__ = ["tornado", "requests"]
__version__ = "2.0"

# Http headers sent to WebSocket server
HTTPHEADERS = {
    "Content-Type": "text/html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
    "Origin": "http://st.chatango.com",
}

DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60


class Session(object):
    """Generates a temporary login session (cookie) for the specified Chatango account.
    """

    def __init__(self, host, username, password):
        self.host = host
        self.sid = username
        self.pwd = password
        self.login_url = "{0}/login?user_id={1}&password={2}&storecookie=on&checkerrors=yes"
    def authenticate(self):
        d = None
        page = self.login_url.format(
            self.host,
            self.sid,
            self.pwd
        )
        sess = requests.Session()
        r = sess.get(page)
        if r.status_code == 200:
            d = sess.cookies.get_dict()
            # Verify user logged in successfully
            if not d.has_key("auth.chatango.com") or len(d["auth.chatango.com"]) <= 1:
                d = None
        return d


class Account(object):
    """Holds a Bot account together and logs him in to generate a auth.chatango.com cookie.
    """

    def __init__(self, host, username, password):
        self.host = host
        self.sid = username
        self.pwd = password
    def login(self):
        return Session(self.host, self.sid, self.pwd).authenticate()


class Message(object):
    """Temporary object that encapsulates messages received on the Chatango chat room (website).
    """

    def __init__(self, timestamp=None, ip=None, font=None, username=None, text=None, channel=None):
        self.timestamp = timestamp
        self.channel = channel
        self.username = username
        self.valid = False
        self.text = text
        self.font = font
        self.ip = ip
    def parse(self, text):
        """Parse given text and populate all of this objects attributes."""
        dissected = text.split("::")
        dissected_first = dissected[0].split(":")
        dissected = dissected_first + dissected[1:]
        try:
            self.timestamp = dissected[1]
            self.username = dissected[2]
            self.ip = dissected[3]
            self.font = dissected[4]
            self.channel = dissected[5]
            self.text = dissected[6]
            self.valid = True
        except ValueError:
            pass
    def __repr__(self):
        return "{0} ({1}): {2}".format(
            self.username,
            self.ip,
            self.text
        )


class Channel(object):
    """Red, Blue or White channel.
    """

    def __init__(self, color="WHITE"):
        self.color = color
        self.choices = {
            "WHITE": 0, # 0
            "BLUE": 2048, # 2048
            "RED": 256, # 256
        }
    def get_id(self):
        return self.choices.get(self.color.upper())

 
class WebSocketClient():
    """Base class for Chatango WebSocket clients
    """
 
    def __init__(self, connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        #
        self.port = None
        self.auth = None
        self.url = None
        self.uid = None
        self.host = None
        # access token required to send messages (sent by server periodically) (important) [ensure your bot retrieves this from the server]
        # look at bots.TrolltangoWebSocketClient for an example of how to retrieve the access token
        self.access_token = None
        self.web_socket_endpoint = None
        #
        self.account = None

    def connect(self, url, port=8080):
        """Connect to the server.
        :param str url: complete website url.
        :param int port: websocket server port (default: 8080)
        """
          
        # save url and port in global variables
        self.port = port
        self.url = url
        # return the website URLs hostname, i.e.: if self.url was "http://nba-stream.chatango.com" self.host would be "nba-stream"
        self.host = emulation.get_chatroom_name(self.url)
        # generate WebSocket endpoint address
        self.web_socket_endpoint = "ws://{0}:{1}".format(
            emulation.get_server_id(url),
            self.port,
        )
        # generate random 16-character unique id (required)
        self._generate_uid()
        # verify that a valid Account() instances has been passed to the global variable self.account
        #if isinstance(self.account, Account):
        if self.account:
            self.auth = self.account.login()
        else:
            raise ValueError, "You must set the global variable self.account to an Account() instance!"
        # update http-headers with authentication token(s)
        http_headers = HTTPHEADERS
        http_headers.update(self.auth)
        headers = httputil.HTTPHeaders(http_headers)
        request = httpclient.HTTPRequest(url=self.web_socket_endpoint,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(ioloop.IOLoop.current(),
                                                      request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def _generate_uid(self, length=16):
        """Generate a UID with length characters. Required to send messages."""
        self.uid = str(random.randrange(10 ** 15, 10 ** 16))

    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')

        self._ws_connection.write_message(data)

    def close(self):
        """Close connection.
        """

        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break

            self._on_message(msg)

    def _on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message
        """

        data = escape.utf8(msg)
        header = None
        payload = None

        try:
            header, payload = data.split(":", 1)
        except ValueError:
            self.on_unrecognized_message(data)

        if header and payload:
            self.on_message(header, payload)

    def on_unrecognized_message(self, msg):
        """Override this to create a callback when the websocket receives an unrecognized packet (message).
        Chatango's WebSocket protocol (usually) sends messages to clients in the format of  "header:payload".
        This class-method (function) is called when we receive a message from the server that is not in that format.
        """

        pass

    def on_message(self, header, msg):
        """You can overidde this to parse server messages in your own manner.
        :param str header: message header (type)
        :param str msg: server message
        """

        pass

    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """

        self.on_connection_success()

    def on_connection_success(self):
        """Override this to create a callback when the websocket connects successfully.
        """

        pass

    def _on_connection_close(self):
        """This is called when server closed the connection.
        """
        
        self.on_connection_close()

    def on_connection_close(self):
        """Override this to create a callback when the websocket connection closes.
        """

        pass

    def _on_connection_error(self, exception):
        """This is called in case if connection to the server could
        not established.
        """

        self.on_connection_error(exception)

    def on_connection_error(self, exception):
        """Override this to create a callback when the websocket encounters an error.
        """

        pass

    def create_planned_timeout(self, call_after, func, **kwargs):
        """Create an interval that calls func every deadline and passes **kwargs to the func.
        :param time.time() callafter: time.time() instance that defines when this function should execute (in seconds)
        :param reference func: Pass reference to the function (func) that should be executed
        :param dict() kwargs: Contains dictionary composed of parameters to pass to function (func)

        i.e.: self.create_planned_timeout(3, self.func_to_call) # calls the self.func_to_call function after 3 seconds
        """

        deadline =  time.time() + call_after
        ioloop.IOLoop().instance().add_timeout(
            deadline, functools.partial(func, **kwargs))