import config
import utility
import socket
import re

def main():
    s = socket.socket()
    s.connect(('irc.twitch.tv', 6667))
    s.send("PASS {}\r\n".format(config.RUHFZY_OAUTH_TOKEN).encode('utf-8'))
    s.send("NICK {}\r\n".format('ruhfzy').encode('utf-8'))
    s.send("JOIN #{}\r\n".format('thearchr').encode('utf-8'))

if __name__ == '__main__':
    main()