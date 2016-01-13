from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket
# contains python code that emulates Chatango obfuscated JavaScript code
import emulation
# contains base WebSocketClient class
import tango
# for use in Session() class
import requests
# built-ins
import functools
import operator
import random
import json
import time


__author__ = "Frowdo"
__description__ = """\
This file contains a premade Chatango Bot called TrolltangoWebSocketClient(). 
Feel free to modify the file itself, inherit from it, or build a new bot by
copying its code. Also, please take a loook at example.py on how to run a bot
once you've created one."
"""

# List of words the bot will spam
DEFAULT_WORDS = [
    "HI",
    "I",
    "LOVE",
    "BLACK",
    "COCK",
    "SHOVE",
    "IT",
    "UP",
    "MY",
    "ASS",
    "PLEASE",
    "DONT",
    "HESISTATE",
    "TO",
    "EAT",
    "OUT",
    "WITH",
    "YOUR",
    "TOUNGE",
    "LEBRON",
    "TOLD",
    "ME",
    "THAT",
    "HE"
    "WOULD",
    "FUCK",
    "TIGHT",
    "ASSHOLE",
    "HAIRY",
    "ASIAN",
    "PENIS",
    "CUM",
    "SKEET",
    "MOUTH",
    "MOAN",
    "FUCK ME",
    "LEBRON",
    "WESTBROOK",
    "KOBE",
    "PENETRATION",
    "RAT",
    "KEVIN",
    "MOIST",
    "WET"
]

# List of phrases the bot will mention
DEFAULT_PHRASES = [
    "I really wish i met you so i could bend you over and drill your hairy asshole",
    "Am i the only horny one in here right now?",
    "My ass is so wet and moist",
    "Is your ass moist too?",
    "Please baby boo, let me cuddle fuck you while fingering your asshole",
    "I so want to eat out your hairy asshole",
    "I shoved my XBOX up my ass",
    "My ass makes most guys come in like 3 minutes",
    "Are you moist?",
    "I'd run a train on that ass",
    "If we ever met, id eat out your asshole and cum in it afterwards",
    "I'd suck your dick better than any chick",
    "Lets stop talking about chicks and start talking about dicks",
    "I bought Call of Booty Black Cocks 3",
    "My XBOX is full of gay porn",
    "My homepage is set to gay porn",
    "I fucked my pet rat in the asshole",
    "Want to exchange dick pics? PM me for my number baby",
    "I'm clapping my ass cheeks",
    "I can clap my ass cheeks for you baby boo",
    "I'm jerking off to your messages, keep them coming baby",
    "I just came on my monitor, right on your profile picture",
    "Get the Trolltango Unchained (Python) script (source code) at: pastie[dot]org/10684698 [Know how to run Python scripts before downloading this]",
    "Get a copy of this new 'Trolltango Unchained' bot at hackforums[dot]net (The difference is that Trolltango Unchained is headerless, smarter, faster, switches between channels (red, blue and white) based on whatever channel is more active, and you can run more than one bot on your PC! (requires you to make a new account per bot instance). So if you have 5 bots running on your computer, make sure that each one is using a unique individual account.",
    "Get a copy of the old 'Trolltango' bot at hackforums[dot]net/showthread[dot]php?tid=5126827 (This is the old version that limits you to 1 bot per computer)",
]


class TrolltangoWebSocketClient(tango.WebSocketClient):
    """An example Chatango Bot built on-top of the base tango.WebSocketClient class.
    """

    def __init__(self):
        tango.WebSocketClient.__init__(self)
        # define class-methods that will handle different types of server messages
        self.headers = {
            "v": self.on_version_response,
            "ok": self.on_auth_response,
            "i": self.on_chat_response,
            "b": self.on_chat_response,
            "n": self.on_access_token_response,
        }
        # server version
        self.version = None
        # are we logged in?
        self.logged_in = False
        # list of chat messages received from the server
        self.messages = []
        # maximum allowed messages to be stored in the list self.messages
        self.max_messages = 300
        # should the bot spam blocks of text?
        self.blocks_of_text = False
        # should the bot just randomly switch in between the red, blue and white channels? 
        # if this value is set to False, the bot will still switch between channels, but
        # only if the bot detects higher chat activity in the other channels.
        self.random_channel_switching = False

    def spam(self):
        msg = self.generate_smart_message()
        # spam blocks of text (?)
        if self.blocks_of_text:
            msg = self.generate_block_of_text() + "<br/><br/>" + msg
        # random channel switching enabled (?)
        if self.random_channel_switching:
            # choose a random chat channel [white, red, blue]
            channel_id = random.choice([0, 256, 2048])
        # otherwise, find the most active chat channel (red, blue, white)
        else:
            channel_id = self.find_active_channel()
        # send chat message to server
        self.send_chat_message(channel_id, msg)
        # loop through this function indefinetly
        self.create_planned_timeout(3, self.spam)

    def generate_smart_message(self):
        phrase = random.choice(DEFAULT_PHRASES)
        # If we have received more than 0 messages that were not sent out by this bot
        if len(self.messages) > 0:
            # Get the last message (that wasn't send out by this bot)
            last_message = self.messages[-1]
            # If the last message is from this bot
            if last_message.username == self.account.sid:
                # Only message the phrase
                message = phrase
            # If the last message was NOT from this bot
            else:
                # Tag the last messages author in the phrase
                message = "@{0} {1}".format(
                    last_message.username,
                    phrase,
                )
        # If noone else besides the bot is chatting
        else:
            # Only message the phrase
            message = phrase
        return message

    def generate_block_of_text(self, words=50):
        msg = ""
        for x in xrange(DEFAULT_WORDS):
            msg += random.choice(WORDS) + "<br/>"
        return msg

    def send_chat_message(self, channel_id, msg):
        """Attempt to send a chat message to the Chatango WebSocket server.
        """

        if self.access_token:
            #print 'bm:u{0}:{1}:{2}\r\n\x00'.format(
            #    self.access_token,
            #    channel_id,
            #    msg
            #)
            self.send(
                b'bm:u{0}:{1}:{2}\r\n\x00'.format(
                    self.access_token,
                    channel_id,
                    msg
                )
            )
            print "[!] Send message successfully."
        else:
            raise ValueError, "You must parse the access token from the server in order to send a chat message! Look at bots.TrolltangoWebSocketClient() for an example."

    def send_initial_data(self):
        """Send version (v) request and login (bauth) request to Chatango WebSocket server.
        """

        if self.host and self.uid and self.account:
            self.send(b'v\r\n\x00')
            self.send(
                b'bauth:{0}:{1}:{2}:{3}\r\n\x00'.format(
                    self.host,
                    self.uid,
                    self.account.sid,
                    self.account.pwd
                )
            )
        else:
            print "[!] Could not send initial data because self.host or self.uid or self.account is None"

    def find_active_channel(self):
        """Finds the most active channel (white, red, blue) and switches focus to it.
        """
        channels = {
            0: 0, # White
            2048: 0, # Blue
            256: 0, # Red
        }
        for m in self.messages:
            key = int(m.channel)
            if channels.has_key(key):
                new_value = channels[key] + 1
                channels[key] = new_value
        print channels
        return max(channels.iteritems(), key=operator.itemgetter(1))[0]

    def on_chat_response(self, msg):
        """Process chat messages received from Chatango WebSocket server.
        """

        msg = "i:" + msg
        msg_obj = tango.Message()
        msg_obj.parse(msg)
        if msg_obj.valid:
            # if we have 'room' to add the message to the list self.messages
            if len(self.messages) < self.max_messages:
                self.messages.append(
                    msg_obj
                )
            # maximum amount of messages reached; remake self.messages list and add the last message received to it
            else:
                self.messages = []
                self.messages.append(
                    msg_obj
                )
            print msg_obj

    def on_access_token_response(self, msg):
        """Update the self.access_token whenver the server sends us a new one. (important) [required to send chat messages]
        """

        self.access_token = msg
        print "[!] Access token updated:", msg

    def on_version_response(self, msg):
        self.version = msg
        print "[!] Version verified as {version}".format(
            version=self.version,
        )

    def on_auth_response(self, msg):
        print "[!] Received auth response:", msg
        self.create_planned_timeout(3, self.spam)

    def on_message(self, header, msg):
        if self.headers.has_key(header):
            f = self.headers[header]
            f(msg)
        else:
            print "[!] Could not parse the packet: {0}:{1}".format(
                header,
                msg
            )

    def on_unrecognized_message(self, msg):
        print "[!] Received server message:", msg

    def on_connection_success(self):
        print('[!] Connected!')
        self.send_initial_data()

    def on_connection_close(self):
        print('[!] Connection closed!')

    def on_connection_error(self, exception):
        print('[!] Connection error: %s', exception)