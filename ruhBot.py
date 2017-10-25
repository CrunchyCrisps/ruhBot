import config
import utility
from utility import sliceDetails, multiplyString, checkRuneList
import socket
import re
import time
import os.path
import json
import requests
import ast
from time import sleep

def main():
    s = socket.socket()
    s.connect((config.HOST, config.PORT))
    s.send("PASS {}\r\n".format(config.BOT_OAUTH_TOKEN).encode('utf-8'))
    s.send("NICK {}\r\n".format(config.NICK).encode('utf-8'))
    s.send("JOIN #{}\r\n".format(config.CHANNEL).encode('utf-8'))

    chat_message = re.compile(r'^:\w+!\w+@\w+.tmi\.twitch\.tv PRIVMSG #\w+ :')

    while True:
        response = s.recv(1024).decode('utf-8')
        if response == 'PING :tmi.twitch.tv\r\n':
            s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
        #else:
        #    print('Hi')
        #     username = re.search(r'\w+', response).group(0)
        #     message = chat_message.sub('', response)
        #     m_c = message.strip()
        #     print(response)
        #
        #     if m_c.startswith('!skill'):
        #         monster = sliceDetails(m_c)[0].title()
        #         skill = sliceDetails(m_c)[1]
        #         skill_nr = int(skill) - 1
        #
        #         path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster)
        #         if os.path.isfile(path):
        #             # load file
        #             with open(path) as data_file:
        #                 data = json.load(data_file)
        #
        #             # set variables
        #             skill_name = data['skills'][skill_nr]['name']
        #             if data['skills'][skill_nr]['cooltime'] is None:
        #                 cooltime = 0
        #             else:
        #                 cooltime = data['skills'][skill_nr]['cooltime']
        #             hits = data['skills'][skill_nr]['hits']
        #             skillups = data['skills'][skill_nr]['max_level'] - 1
        #             if skillups == 0:
        #                 progress = '-'
        #             else:
        #                 progress_raw = data['skills'][skill_nr]['level_progress_description']
        #                 still_raw = progress_raw.replace('\r\n', ', ')
        #                 if still_raw[-1] == '\n':
        #                     progress = still_raw.replace('\n', ', ')[:-2]
        #                 else:
        #                     progress = still_raw.replace('\n', ', ')
        #             if data['skills'][skill_nr]['multiplier_formula_raw'] == '[]':
        #                 multiplier = '-'
        #             else:
        #                 mult = ast.literal_eval(data['skills'][skill_nr]['multiplier_formula_raw'])
        #                 multiplier = ''
        #                 for part in mult:
        #                     if len(part) > 1:
        #                         piece = '({})'.format(' '.join(map(str, part)))
        #                     else:
        #                         piece = ' '.join(map(str, part))
        #                     multiplier += piece
        #
        #                 mult_dict = {'ATTACK_LOSS_HP': 'Lost HP', 'TARGET_TOT_HP': 'Enemy MAX HP',
        #                              'TARGET_CUR_HP_RATE': 'Enemy HP %', 'ATTACK_TOT_HP': 'MAX HP',
        #                              'ATTACK_SPEED': 'SPD',
        #                              'TARGET_SPEED': 'Enemy SPD'}
        #
        #                 for word in ['ATTACK_LOSS_HP', 'TARGET_TOT_HP', 'TARGET_CUR_HP_RATE', 'ATTACK_TOT_HP',
        #                              'ATTACK_SPEED', 'TARGET_SPEED']:
        #                     multiplier = multiplier.replace(word, mult_dict[word])
        #
        #             effect_list = []
        #             for effect in data['skills'][skill_nr]['skill_effect']:
        #                 effect_list.append(effect['name'])
        #             effects = ' - '.join(effect_list)
        #             desc = data['skills'][skill_nr]['description']
        #             result1 = skill_name
        #             result2 = 'Multiplier: {}, Hits: {}, Cooltime: {}, Skillups: {} ({}) '.format(multiplier,hits,cooltime,skillups,progress)
        #             result3 = 'Effects: {}'.format(effects)
        #             result4 = desc
        #             #utility.chat(s,result1)
        #             #utility.chat(s,result2)
        #             #utility.chat(s,result3)
        #             utility.whisper(s,username,result1)
        #             utility.whisper(s,username,result2)
        #             utility.whisper(s,username,result3)
        #             sleep(1.1)
        #             utility.whisper(s,username,result4)
        #             utility.chat(s,'I wispered you the information, {}.'.format(username))
        #         else:
        #             result = 'Monster not found.'
        #             utility.chat(s, result)
        #
        #     elif m_c.startswith('!info'):
        #         monster = m_c[6:]
        #         monster_formatted = monster.title()
        #
        #         if 'Wind ' in monster_formatted or 'Fire ' in monster_formatted or 'Water ' in monster_formatted or 'Dark ' in monster_formatted or 'Light ' in monster_formatted:
        #             tmp_path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster_formatted)
        #             if os.path.isfile(tmp_path):
        #                 with open(tmp_path) as data_file_tmp:
        #                     data_tmp = json.load(data_file_tmp)
        #                 monster_formatted = data_tmp['awakens_to']['name']
        #
        #         path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster_formatted)
        #         if os.path.isfile(path):
        #             with open(path) as data_file:
        #                 data = json.load(data_file)
        #             name = data['name']
        #             element = data['element']
        #             awaken = data['awaken_bonus']
        #             if data['leader_skill'] is None:
        #                 leader = '-'
        #             else:
        #                 leader = '{0}% {1} [{2}]'.format(data['leader_skill']['amount'],
        #                                                  data['leader_skill']['attribute'],
        #                                                  data['leader_skill']['area'])
        #             stats = 'HP: {0}, Attack: {1}, Defense: {2}, SPD: {3}'.format(data['max_lvl_hp'],
        #                                                                           data['max_lvl_attack'],
        #                                                                           data['max_lvl_defense'],
        #                                                                           data['speed'])
        #             skills = []
        #             for skill in data['skills']:
        #                 if skill['cooltime'] is None:
        #                     cooldown = ''
        #                 else:
        #                     cooldown = '(Reusable in {} turns)'.format(skill['cooltime'])
        #                 if skill['hits'] is None:
        #                     hits = ''
        #                 else:
        #                     if skill['hits'] == 1:
        #                         hitter = 'Hit'
        #                     else:
        #                         hitter = 'Hits'
        #                     hits = '[{} {}]'.format(skill['hits'],hitter)
        #                 if skill['max_level']-1 == 1:
        #                     skillz = '1 Skillup'
        #                 else:
        #                     skillz = '{} Skillups'.format(skill['max_level']-1)
        #                 info = '{0}: {1} {2} {3}[{4}]'.format(skill['name'],
        #                                                                skill['description'],
        #                                                                cooldown,
        #                                                                hits, skillz)
        #                 skills.append(info)
        #
        #             if '(' in monster:
        #                 awaken_from = 'Unicorn'
        #             else:
        #                 awaken_from = '{}'.format(data['awakens_from']['name'])
        #
        #             result_name = '{} ({} {})'.format(name,element,awaken_from)
        #             result_stats = '{}'.format(stats)
        #             result_lead = 'Leader Skill: {}'.format(leader)
        #             result_awaken = 'Awakening Bonus: {}'.format(awaken)
        #
        #             utility.whisper(s, username, result_name)
        #             utility.whisper(s, username, result_stats)
        #             utility.whisper(s, username, result_lead)
        #             sleep(1.1)
        #             utility.whisper(s, username, result_awaken)
        #             sleep(1.1)
        #             for skill in skills:
        #                 utility.whisper(s, username, skill)
        #             utility.chat(s, 'I wispered you the information, {}.'.format(username))
        #         else:
        #             result = 'Monster not found. Try again.'
        #             utility.chat(s, result)
        # sleep(1)

if __name__ == '__main__':
    main()