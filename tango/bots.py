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
    "Get the Trolltango Unchained (Python) script (source code) at: github.com/PyDark/Tango [know how to run Python scripts before downloading this]",
    #"Get a copy of this new 'Trolltango Unchained' bot at UNDEFINED (The difference is that Trolltango Unchained is headerless, smarter, faster, switches between channels (red, blue and white) based on whatever channel is more active, and you can run more than one bot on your PC! (requires you to make a new account per bot instance). So if you have 5 bots running on your computer, make sure that each one is using a unique individual account.",
    "Get a copy of the old 'Trolltango' bot at hackforums[dot]net/showthread[dot]php?tid=5126827 (This is the old version that limits you to 1 bot per computer)",
]


class TrolltangoWebSocketClient(tango.WebSocketClient):
    """An example Chatango Bot built on-top of the base tango.WebSocketClient class.

    Behavior: This bot spits gay words and phrases onto the target Chatango chat room (website).
    It also has the ability to switch channels (red, blue, white) if it detects activity in 
    other channels or if the global instance variable self.random_channel_switching (boolean) is set to True
    the bot randomly switches between the aforementioned channels.
    It also reponses to the last person to send a message in the Chatango chat room (website) (if any).
    The bot does NOT repond to itself.
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
            "msglexceeded": self.on_msglength_exceeded_response,
        }
        # server version
        self.version = None
        # are we logged in?
        self.logged_in = False
        # list of chat messages received from the server
        self.messages = []
        # maximum allowed messages to be stored in the list self.messages
        self.max_messages = 300
        # stores the index of the last used phrase in the DEFAULT_PHRASES list
        self.last_phrase_used = None
        # should the bot remove the self.last_phrase_used if it exceeds the maximum chat message length? 
        # (use if you keep getting msglexeeded responses from the Chatango WebSocket server)
        self.remove_phrases_that_exceed_length = False
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
        self.last_phrase_used = phrase
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
        for x in xrange(words):
            msg += random.choice(DEFAULT_WORDS) + "<br/>"
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
        #print channels
        return max(channels.iteritems(), key=operator.itemgetter(1))[0]

    def on_msglength_exceeded_response(self, msg):
        """We attempted to send a message that exceeded the maximum length defined by the parameter 'msg'.
        Remove the last used phrase from the DEFAULT_PHRASES list. 
        """

        global DEFAULT_PHRASES
        try:
            limit = int(msg)
        except ValueError:
            limit = None
        if limit:
            print "[!] The last message sent exceeded the maximum chat message length of {0}".format(
                limit
            )
            if self.remove_phrases_that_exceed_length:
                DEFAULT_PHRASES.remove(self.last_phrase_used)
                print "[!] Removed a phrase for exceeding the maximum chat message length"


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


class TrolltangoEchoClient(TrolltangoWebSocketClient):
    """An example Chatango Bot built on-top of the existing TrolltangoWebSocketClient bot class.

    Behavior: This bot copies the last message received in the Chatango chat room (website)
    and echo's it back to the person whom sent it. If nobody is speaking, the bot stays silent
    until someone sends a message. 
    """

    def __init__(self):
        TrolltangoWebSocketClient.__init__(self)

        # TO DO


class TrolltangoQuizClient(tango.WebSocketClient):
    """An example Chatango Bot built on-top of the existing TrolltangoWebSocketClient bot class.

    Behavior: This bot selects a random Question() object from the global QUIZ_QUESTIONS list
    and asks the question in the Chatango chat room (website). When someone sends a message,
    the bot reads (parses) the response, and determines if it is the correct answer or wrong
    answer; then the bot sends a message stating if the answer is 'correct' or 'incorrect'.
    """

    def __init__(self):
        TrolltangoWebSocketClient.__init__(self)

        # TO DO


class TrolltangoRacismDetectorClient(tango.WebSocketClient):
    """An example Chatango Bot built on-top of the existing TrolltangoWebSocketClient bot class.

    Behavior: This bot remains silent but continuously reads (parses) the chat messages until
    it detects a racist term send by another user. Once it detects racism, it will begin
    flooding the chat room with random phrases from the global STOP_RACISM list. The bot will
    continue reading (parsing) the chat messages, until someone says "!STOPBOT". If the command
    is read from any chat message. The bot will stop spamming and repeat the sequence.
    """

    def __init__(self):
        TrolltangoWebSocketClient.__init__(self)

        # TO DO