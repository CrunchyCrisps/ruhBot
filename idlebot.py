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
    response_amount = 0
    last_lul = time.time()
    while True:
        response = s.recv(1024).decode('utf-8')
        if response == 'PING :tmi.twitch.tv\r\n':
            s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
        else:
            username = re.search(r'\w+', response).group(0)
            message = chat_message.sub('', response)
            m_c = message.strip()

            #if m_c == 'LUL' and username != 'ruhfzy' and round(time.time() - last_lul) >= 31:
            if m_c == 'LUL':
                #last_lul = time.time()
                response_amount += 1
                print('Amount of LULs: {}'.format(response_amount))
                #print('Total Amount of Responses: {}'.format(response_amount))
                #print('Responding to {}'.format(username))
                print('-------------------')
                #sleep(1)
                #utility.chat(s, 'LUL')

    #stalking = False
    
    #while True:
    #    if not stalking:
    #        print('Now stalking {}.'.format(config.CHANNEL))
    #        stalking = True

if __name__ == '__main__':
    main()
