import config
import utility
import socket
import time
import re
from time import sleep

def main():
    s = socket.socket()
    s.connect((config.HOST, config.PORT))
    s.send("PASS {}\r\n".format(config.RUHFZY_OAUTH_TOKEN).encode('utf-8'))
    s.send("NICK {}\r\n".format(config.NICK).encode('utf-8'))
    s.send("JOIN #{}\r\n".format(config.CHANNEL).encode('utf-8'))

    chat_message = re.compile(r'^:\w+!\w+@\w+.tmi\.twitch\.tv PRIVMSG #\w+ :')
    psama_amount = 0

    while True:
        response = s.recv(1024).decode('utf-8')
        if response == 'PING :tmi.twitch.tv\r\n':
            s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
        else:
            username = re.search(r'\w+', response).group(0)
            message = chat_message.sub('', response)
            m_c = message.strip()

            if 'LUL' in m_c:
                psama_amount += 1
                if psama_amount % 5 == 0:
                    print('Amount of Psamas: {}'.format(psama_amount))
                    print('Last Psama by {}'.format(username))
                    print('-------------------')

if __name__ == '__main__':
    main()
