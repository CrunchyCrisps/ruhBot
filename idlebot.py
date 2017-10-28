import config
import utility
import socket
import re

def main():
    s = socket.socket()
    s.connect((config.HOST, config.PORT))
    s.send("PASS {}\r\n".format(config.RUHFZY_OAUTH_TOKEN).encode('utf-8'))
    s.send("NICK {}\r\n".format(config.NICK).encode('utf-8'))
    s.send("JOIN #{}\r\n".format(config.CHANNEL).encode('utf-8'))

    chat_message = re.compile(r'^:\w+!\w+@\w+.tmi\.twitch\.tv PRIVMSG #\w+ :')

    while True:
        response = s.recv(1024).decode('utf-8')
        if response == 'PING :tmi.twitch.tv\r\n':
            s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
        else:
            username = re.search(r'\w+', response).group(0)
            message = chat_message.sub('', response)
            m_c = message.strip()

            if m_c.__contains__('LUL'):
                utility.chat(s, 'LUL'.format(username))

    #stalking = False
    
    #while True:
    #    if not stalking:
    #        print('Now stalking {}.'.format(config.CHANNEL))
    #        stalking = True

if __name__ == '__main__':
    main()
