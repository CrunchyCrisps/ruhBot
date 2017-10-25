import discord
import asyncio
import urlfetch
import requests
import json
import sqlite3
import config
import datetime
import os.path
import random
import time
import ast
from discord import opus
from time import sleep
from decimal import Decimal
from utility import sliceDetails, multiplyString, checkRuneList, endingChecker, getMonsterInfo

client = discord.Client()
conn = sqlite3.connect('C:\\Users\\Raffael\\Documents\\ruhBot\\users.db')
c = conn.cursor()

command_list = ("```Markdown\nGeneral\n-------\n* hello\n* joined\n* created\n* credits\n* roll\n* messages [amount]\n* help [command]\n* eliminate [options]\n* gamble [amount]\n* ? [question]\n\n"
                "Twitch\n------\n* live [channel]\n* preview [channel] [size]\n* topstreams [language]\n\n"
                "Stream Elements\n---------------\n* points [channel] [user]\n* top [amount] [channel]\n\n"
                "Swarfarm\n--------\n* set [swarfarm name]\n* my [monster]\n* mon [monster]\n* skill [number] [monster]\n* add [summons] [lightnings]\n* rates```")

@client.event
async def on_ready():
    print("I'm charged and ready")
    print('----------')
    #await client.send_message(client.get_channel('332678368837369857'), "I'm charged and ready :robot:")

def is_my(message):
    return message.author == client.user and message.content == 'Waiting for Swarfarm to respond <:ResidentSleeper:346295911502053386>'

@client.event
async def on_message(message):
    # random discord stuff
    content = message.content
    channel = message.channel
    author = message.author

    c.execute('SELECT id,credits FROM usernames WHERE id=?', (author.id,))
    exist = c.fetchone()
    if exist is None:
        c.execute('INSERT INTO usernames (id, credits) VALUES (?,?)', (author.id,1))
    else:
        new_credits = exist[1] + 1
        c.execute('UPDATE usernames SET credits = ? WHERE id = ?', (new_credits,author.id))
    conn.commit()

    if content.startswith('!messages'):
        if len(content) == 9:
            limit = 100
        else:
            limit = int(content[9:])
        counter = 0
        tmp = await client.send_message(channel, 'Calculating messages...')
        async for log in client.logs_from(channel, limit):
            if log.author == author:
                counter += 1
        percentage = (counter/limit) * 100
        await client.edit_message(tmp, 'You wrote {0}/{1} messages. ({2}%)'.format(counter, limit, str(percentage)[:4]))

    elif content.startswith('!delete'):
        if author.permissions_in(channel).manage_messages:
            amount = content.split()[1]
            await client.purge_from(channel,limit=int(amount)+1)
            await client.send_message(channel, amount + ' messages have been deleted.')
        else:
            await client.send_message(channel, 'You do not have permission to use that command.')

    elif content.lower().startswith('hello') and author != client.user:
        await client.send_message(channel, 'Hello ' + author.mention + ' :yum:')

    elif content.startswith('!commands'):
        await client.send_message(channel, command_list)

    elif content.startswith('!joined'):
        await client.send_message(channel, 'You joined ' + str(author.joined_at)[:19] + ".")

    elif content == '!binds':
        response = ("```Markdown\nBinds\n-----\n"
                    "* F1 - [toggle] com_maxfps 125 250 333\n"
                    "* F2 - [toggle] player_sustainammo 0 1\n"
                    "* F3 - [toggle] jump_slowdownenable 0 1\n"
                    "* F4 - [toggle] god\n"
                    "* F5 - [toggle] cl_avidemo 0 300\n"
                    "* F6 - [toggle] r_detail 0 1\n"
                    "* F7 - [toggle] r_fullbright 0 1\n"
                    "* F8 - give rpg_mp```")
        await client.send_message(channel, response)

    elif content == '!roll':
        result = random.randint(1,6)
        await client.send_message(channel, 'You rolled a {}'.format(result))

    elif content.startswith('!eliminate'):
        choices = content[11:].split()
        while (len(choices) > 1):
            choice = random.choice(choices)
            choices.remove(choice)
            result = ' '.join(choices)

            await client.send_message(channel, result)

    elif content == '!credits':
        c.execute('SELECT credits FROM usernames WHERE id=?', (author.id,))
        result = c.fetchone()
        conn.commit()
        await client.send_message(channel, 'You have {} credits.'.format(result[0]))

    elif content.startswith('!gamble'):
        discord_id = author.id
        c.execute('SELECT credits FROM usernames WHERE id=?', (discord_id,))
        result = c.fetchone()
        conn.commit()
        bet_amount = int(content.split()[1])
        current_credits = result[0]
        if current_credits < bet_amount:
            await client.send_message(channel, "You don't have enough credits.")
        else:
            number = random.randint(1,100)
            if number <= 60:
                new_credits = current_credits - bet_amount
                gz_msg = 'You rolled {} so you lose {} {} <:FeelsRageMan:352057470618697738>'.format(
                    number, bet_amount, endingChecker(bet_amount,'credit'))
            elif number > 96 and number < 100:
                new_credits = current_credits + (3 * bet_amount)
                gz_msg = 'You rolled {} so you win {} credits <:PogChamp:352059261502881792>'.format(
                    number, 3 * bet_amount)
            elif number == 100:
                new_credits = current_credits + (5 * bet_amount)
                gz_msg = '<:PogChamp:352059261502881792> GRAND PRIZE BOYZ <:PogChamp:352059261502881792> YOU ROLLED A 100 SO YOU WIN {} CREDITS WOOOOOO <:PogChamp:352059261502881792>'.format(
                    bet_amount * 5)
            else:
                new_credits = current_credits + bet_amount
                gz_msg = 'You rolled {} so you win {} {} :sunglasses:'.format(
                    number, bet_amount, endingChecker(bet_amount,'credit'))
            c.execute('UPDATE usernames SET credits = ? WHERE id = ?', (new_credits, discord_id))
            conn.commit()
            await client.send_message(channel, '{} You now have {} {}.'.format(gz_msg,new_credits,endingChecker(new_credits,'credit')))

    elif content.startswith('!joke'):
        if content.split()[1] == 'chuck':
            url = 'http://api.icndb.com/jokes/random'
            r = requests.get(url,headers={'Accept': 'application/json',
                                                'Content-Type': 'application/json', })
            response = r.json()
            joke = response['value']['joke']
        elif content.split()[1] == 'dad':
            url = 'https://icanhazdadjoke.com/'
            r = requests.get(url, headers={'Accept': 'application/json',
                                           'Content-Type': 'application/json', })
            response = r.json()
            joke = response['joke']
        await client.send_message(channel,joke)

    # twitch stuff
    elif content.startswith('!live'):
        name = content[6:]
        url = 'https://api.twitch.tv/kraken/streams/{}'.format(name)
        r = requests.get(url, headers={'Client-ID':config.TWITCH_CLIENT_ID})
        response = r.json()

        if response['stream'] is None:
            msg = '{} is currently offline.'.format(name)
        else:
            viewers = response['stream']['viewers']
            game = response['stream']['game']
            msg = '{} is currently streaming @ https://www.twitch.tv/{} [{}][{} Viewers]'.format(name,name,game,viewers)

        await client.send_message(channel, msg)

    elif content.startswith('!preview'):
        msg = content.split()
        name = msg[1]
        if 'small' in content:
            size = 'small'
        elif 'large' in content:
            size = 'large'
        else:
            size = 'medium'

        url = 'https://api.twitch.tv/kraken/streams/{}'.format(name)
        r = requests.get(url, headers={'Client-ID':config.TWITCH_CLIENT_ID})
        response = r.json()

        if response['stream'] is None:
            preview = '{} is currently offline.'.format(name)
        else:
            preview = response['stream']['preview'][size]

        await client.send_message(channel, preview)

    elif content.startswith('!streams'):
        url = 'https://api.twitch.tv/kraken/streams/followed'
        r = requests.get(url, headers={'Accept':'application/vnd.twitchtv.v5+json',
                                    'Client-ID':config.TWITCH_CLIENT_ID,
                                    'Authorization':config.OAUTH_TOKEN})
        response = r.json()
        streamers = []
        if response['_total'] == 0:
            result = 'No streams you are following are currently online.'
        else:
            for stream in response['streams']:
                name = stream['channel']['display_name']
                game = stream['game']
                viewers = stream['viewers']
                info = '{0} [{1}][{2} Viewers]'.format(name,game,viewers)
                streamers.append(info)

            result = ", ".join(streamers)
        await client.send_message(channel, result)

    elif content.startswith('!topstreams'):
        if len(content.split()) == 2:
            language_code = content.split()[1]
            if any(x == language_code for x in ['german','ger','de','deu','deutsch','germany']):
                language_code = 'de'
            elif any(x == language_code for x in ['korea','kor','ko','korean']):
                language_code = 'ko'


            url = 'https://api.twitch.tv/kraken/streams?language={}&limit=5'.format(language_code)
        else:
            url = 'https://api.twitch.tv/kraken/streams/?limit=5'
        r = requests.get(url, headers={'Client-ID':config.TWITCH_CLIENT_ID})
        response = r.json()
        streamers =[]
        i = 0
        for stream in response['streams']:
            display_name = stream['channel']['display_name']
            name = stream['channel']['name']
            if name.lower() != display_name.lower():
                name_result = '{} ({})'.format(display_name, name)
            else:
                name_result = display_name
            game = stream['game']
            viewers = stream['viewers']
            i += 1
            info = '#{0} {1} [{2}][{3} Viewers]'.format(i,name_result,game,viewers)
            streamers.append(info)

        result = "\n".join(streamers)
        await client.send_message(channel, 'Current top five streams on Twitch:\n\n{}'.format(result))

    # streamelements stuff
    elif content.startswith('!points'):
        msg = content.split()
        channel = msg[1]
        user = msg[2]
        url = 'https://api.streamelements.com/kappa/v1/points/{}/{}'.format(channel,user)
        r = requests.get(url, headers={'Authorization' : '{}'.format(config.JWT_TOKEN)})
        response = r.json()
        if 'statusCode' in response:
            result = '{} was not found. Try again.'.format(user)
        else:
            points = response['points']
            rank = response['rank']
            result = 'You have {0} points. [#{1}]'.format(points,rank)
        await client.send_message(channel, result)

    elif content.startswith('!top'):
        msg = content.split()
        amount = int(msg[1])
        channel = msg[2]
        if amount > 20:
            result = 'Please enter a number <= 20 and try again.'
        else:
            url = 'https://api.streamelements.com/kappa/v1/points/{}/top/{}'.format(channel,amount)
            r = requests.get(url, headers={'Authorization' : '{}'.format(config.JWT_TOKEN)})
            response = r.json()
            users = []
            for x in range(0,amount):
                u_name = response['users'][x]['username']
                u_points = response['users'][x]['points']
                u_info = '{}. {} [{} Points]'.format(x+1,u_name,u_points)
                users.append(u_info)
            users_formatted = '\n'.join(users)
            result = '```Markdown\nCurrent top {} viewers:\n-----------------------\n\n{}```'.format(amount,users_formatted)
        await client.send_message(channel, result)

    # sw stuff
    elif content.startswith('!set'):
        swarfarm = content.split()[1]
        discord_id = author.id
        c.execute('SELECT id FROM usernames WHERE id=?', (discord_id,))
        result = c.fetchone()
        if result is None:
            c.execute('INSERT INTO usernames VALUES (?,?)', (discord_id, swarfarm))
            msg = '{} was added as your Swarfarm account.'.format(swarfarm)
        else:
            c.execute('UPDATE usernames SET swarfarm = ? WHERE id = ?', (swarfarm, discord_id))
            msg = 'Successfully updated your Swarfarm account.'.format(swarfarm)
        conn.commit()
        await client.send_message(channel, msg)

    elif content.startswith('!mon'):
        monster = content[5:]
        monster_formatted = monster.title()
        result = ''
        if any(x in monster_formatted for x in ['Wind','Water','Fire','Dark','Light']):
            tmp_path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster_formatted)
            if os.path.isfile(tmp_path):
                with open(tmp_path) as data_file_tmp:
                    data_tmp = json.load(data_file_tmp)
                monster_formatted = data_tmp['awakens_to']['name']

        path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster_formatted)
        if os.path.isfile(path):
            result = getMonsterInfo(monster_formatted,path)
        else:
            found = False
            mon_dir = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters'
            for file in os.listdir(mon_dir):
                if monster_formatted.lower() in file.lower() and found is False:
                    result = getMonsterInfo(file[:-5],'{}\\{}'.format(mon_dir,file))
                    found = True
            if result == '':
                result = 'Monster not found. Try again.'
        await client.send_message(channel, result)

    elif content.startswith('!my'):
        discord_id = author.id
        c.execute('SELECT id,swarfarm FROM usernames WHERE id=?', (discord_id,))
        result = c.fetchone()

        if result is None:
            msg = "You haven't linked your Swarfarm account yet, use !set to do so."
            await client.send_message(channel, msg)
        else:
            swarfarm_id = result[1]
            monster_name = content[4:]
            monster_formatted = monster_name.title()
            path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster_formatted)

            if os.path.isfile(path):
                await client.send_message(channel,
                                          'Waiting for Swarfarm to respond <:ResidentSleeper:346295911502053386>')
                # load file
                with open(path) as data_file:
                    data = json.load(data_file)

                monster_id = data['pk']
                stat_url = 'https://swarfarm.com/api/v2/profiles/{}/monsters/'.format(swarfarm_id)
                r1 = requests.get(stat_url, headers={'Accept': 'application/json',
                                            'Content-Type': 'application/json', })
                response = r1.json()
                result = ''
                for monster in response['results']:
                    if monster['monster'] == monster_id:
                        instance_id = monster['id']

                        url2 = 'https://swarfarm.com/api/instance/{}'.format(instance_id)
                        r2 = requests.get(url2, headers={'Accept': 'application/json',
                                                    'Content-Type': 'application/json', })
                        monster_info = r2.json()

                        if monster_info['monster']['is_awakened'] is True:
                            awaken_star = '<:star_icon:346033737659580426>'
                        else:
                            awaken_star = '<:star_icon_y:346034828824674305>'
                        stars = multiplyString(awaken_star, monster_info['stars'])
                        level = monster_info['level']
                        hp = monster_info['hp']
                        attack = monster_info['attack']
                        defense = monster_info['defense']
                        speed = monster_info['speed']
                        crit_rate = monster_info['crit_rate']
                        crit_damage = monster_info['crit_damage']
                        resistance = monster_info['resistance']
                        accuracy = monster_info['accuracy']

                        if not monster_info['runeinstance_set']:
                            final_sets = 'Missing Runes'
                            slots = '?/?/?'
                        else:
                            rune_sets = []
                            slot_two = ''
                            slot_four = ''
                            slot_six = ''
                            for rune in monster_info['runeinstance_set']:
                                rune_sets.append(rune['get_type_display'])
                            final_sets = checkRuneList(rune_sets)
                            for rune in monster_info['runeinstance_set']:
                                if rune['slot'] == 2:
                                    slot_two = rune['get_main_stat_rune_display']
                                elif rune['slot'] == 4:
                                    slot_four = rune['get_main_stat_rune_display']
                                elif rune['slot'] == 6:
                                    slot_six = rune['get_main_stat_rune_display']
                            slot_list = []
                            for slot in [slot_two,slot_four,slot_six]:
                                slot_abbreviation = slot.replace('Accuracy', 'ACC').replace('CRI Dmg', 'CDMG').replace('CRI Rate', 'CR')
                                if slot_abbreviation == '':
                                    slot_list.append('?')
                                else:
                                    slot_list.append(slot_abbreviation)
                            slots = '{}'.format('/'.join(slot_list))

                        result = '{} {} Level {} - {} - {}\nHP: {} Attack: {} Def: {} SPD: {} CR: {}% CDMG: {}% Res: {}% Acc: {}% '.format(
                            monster_formatted, stars, level, final_sets, slots, hp, attack, defense, speed, crit_rate,
                            crit_damage, resistance, accuracy)
                        await client.purge_from(channel, limit=5, check=is_my)
                        await client.send_message(channel, result)

                if result == '':
                    await client.purge_from(channel, limit=5, check=is_my)
                    if monster_formatted[0] == 'A' or monster_formatted[0] == 'E' or monster_formatted[0] == 'O' or \
                                    monster_formatted[0] == 'I' or monster_formatted[0] == 'U':
                        artikel = 'an'
                    else:
                        artikel = 'a'
                    await client.send_message(channel, "You don't have {} {} <:FeelsThinkMan:346082076287565824>".format(
                        artikel, monster_formatted))
            else:
                await client.send_message(channel, 'Monster not found.')

    elif content.startswith('!skill'):
        monster = sliceDetails(content)[0].title()
        skill = sliceDetails(content)[1]
        skill_nr = int(skill)-1

        path = 'C:\\Users\\Raffael\\Documents\\ruhBot\\monsters\\{}.json'.format(monster)
        if os.path.isfile(path):
            # load file
            with open(path) as data_file:
                data = json.load(data_file)

            # set variables
            skill_name = data['skills'][skill_nr]['name']
            if data['skills'][skill_nr]['cooltime'] is None:
                cooltime = 0
            else:
                cooltime = data['skills'][skill_nr]['cooltime']
            hits = data['skills'][skill_nr]['hits']
            skillups = data['skills'][skill_nr]['max_level']-1
            if skillups == 0:
                progress = '-'
            else:
                progress_raw = data['skills'][skill_nr]['level_progress_description']
                still_raw = progress_raw.replace('\r\n', ', ')
                if still_raw[-1] == '\n':
                    progress = still_raw.replace('\n',', ')[:-2]
                else:
                    progress = still_raw.replace('\n',', ')
            if data['skills'][skill_nr]['multiplier_formula_raw'] == '[]':
                multiplier = '-'
            else:
                mult = ast.literal_eval(data['skills'][skill_nr]['multiplier_formula_raw'])
                multiplier = ''
                for part in mult:
                    if len(part) > 1:
                        piece = '({})'.format(' '.join(map(str, part)))
                    else:
                        piece = ' '.join(map(str, part))
                    multiplier += piece

                mult_dict = {'ATTACK_LOSS_HP': 'Lost HP', 'TARGET_TOT_HP': 'Enemy MAX HP',
                             'TARGET_CUR_HP_RATE': 'Enemy HP %', 'ATTACK_TOT_HP': 'MAX HP', 'ATTACK_SPEED': 'SPD',
                             'TARGET_SPEED': 'Enemy SPD'}

                for word in ['ATTACK_LOSS_HP','TARGET_TOT_HP','TARGET_CUR_HP_RATE','ATTACK_TOT_HP','ATTACK_SPEED','TARGET_SPEED']:
                    multiplier = multiplier.replace(word,mult_dict[word])

            effect_list = []
            for effect in data['skills'][skill_nr]['skill_effect']:
                effect_list.append(effect['name'])
            effects = ' - '.join(effect_list)
            desc = data['skills'][skill_nr]['description']

            result = '**{0}**\n\nMultiplier: {7}, Hits: {2}, Skillups: {3}, Cooltime: {1}\nProgress: {4}\nEffects: {5}\n\nDescription: {6}'.format(
                skill_name, cooltime, hits, skillups, progress, effects, desc, multiplier)
        else:
            result = 'Monster not found.'

        await client.send_message(channel, result)

    elif content.startswith('!add'):
        a_amount = int(content.split()[1])
        a_lightnings = int(content.split()[2])
        if a_lightnings > a_amount:
            await client.send_message(channel,"You can't have more lightnings than summons <:FeelsTastyMan:349279377646682115>")
        else:
            if a_lightnings == 0:
                a_streak = a_amount
            else:
                a_streak = 0
            c.execute('SELECT user,streak FROM summons WHERE user=?', (author.id,))
            exist = c.fetchone()
            if exist is None:
                c.execute('INSERT INTO summons (user, amount, lightnings, streak) VALUES (?,?,?,?)', (author.id, a_amount, a_lightnings, a_streak))
            else:
                if a_lightnings > 0:
                    a_streak = exist[1] * -1
                c.execute('UPDATE summons SET amount = amount+?, lightnings = lightnings+?, streak = streak+? WHERE user = ?', (a_amount,a_lightnings,a_streak, author.id))
            conn.commit()
            summon_word = endingChecker(a_amount,'summon')
            lightning_word = endingChecker(a_lightnings,'lightning')
            await client.send_message(channel,'Successfully added {} {} with {} {}.'.format(a_amount,summon_word,a_lightnings,lightning_word))

    elif content == '!rates':
        c.execute('SELECT user,amount,lightnings,streak FROM summons WHERE user=?', (author.id,))
        exist = c.fetchone()
        if exist is None:
            await client.send_message(channel,"You haven't added any summons yet.")
        else:
            lightning_rate = str((exist[2] / exist[1]) * 100)
            if lightning_rate[2] == '.':
                lightning_rate_formatted = lightning_rate[:5]
            else:
                lightning_rate_formatted = lightning_rate[:4]
            result = "You have done {} summons and had {} lightnings. That's a lightning rate of {}%. Your current no-lightning streak is {}.".format(
                exist[1], exist[2], lightning_rate_formatted, exist[3])
            conn.commit()
            await client.send_message(channel,result)

    elif content == '!saved':
        c.execute('SELECT mystical,water,fire,wind,ld,ls,ss FROM saves WHERE user=?', (author.id,))
        result = c.fetchone()
        ms = result[0]
        water = result[1]
        fire = result[2]
        wind = result[3]
        ld = result[4]
        ls = result[5]
        ss = result[6]
        stone_summons = int(ss/50)
        overall = ms+water+fire+wind+ld+ls

        msg = 'You have saved {} Mystical Scrolls, {} Water scrolls, {} Fire Scrolls, {} Wind Scrolls, {} L/D Scrolls, {} Legendary Scrolls and {} Summoning Stones. ({} Scrolls & {} {})'.format(
            ms, water, fire, wind, ld, ls, ss, overall, stone_summons, endingChecker(stone_summons,"Stone Summon"))
        await client.send_message(channel,msg)

    elif content.startswith('!save'):
        discord_id = author.id
        amount = content.split()[1]
        scroll_raw = content.split()[2].lower()
        if scroll_raw == 'ms' or scroll_raw == 'mystical':
            scroll = 'mystical'
            full_scroll_name = 'Mystical Scroll'
        elif scroll_raw == 'stones' or scroll_raw == 'ss' or scroll_raw == 'stone':
            scroll = 'ss'
            full_scroll_name = 'Summoning Stone'
        elif scroll_raw == 'ld':
            scroll = 'ld'
            full_scroll_name = 'L/D Scroll'
        elif scroll_raw == 'ls' or scroll_raw == 'legendary':
            scroll = 'ls'
            full_scroll_name = 'Legendary Scroll'
        elif any(x == scroll_raw for x in ['wind','water','fire']):
            scroll = scroll_raw
            full_scroll_name = '{} Scroll'.format(scroll_raw)

        c.execute('SELECT user FROM saves WHERE user=?', (discord_id,))
        exist = c.fetchone()
        if exist is None:
            c.execute('INSERT INTO saves (user, ' + scroll + ') VALUES (?,?)', (discord_id,amount))
        else:
            c.execute(
                'UPDATE saves SET ' + scroll + ' = ' + scroll
             + ' + ?  WHERE user = ?',
                (amount, author.id))
        conn.commit()
        await client.send_message(channel,'Successfully added {} {}.'.format(amount,endingChecker(int(amount),full_scroll_name)))

    elif content.startswith('!remove'):
        discord_id = author.id
        amount = int(content.split()[1])
        scroll_raw = content.split()[2].lower()
        if scroll_raw == 'ms' or scroll_raw == 'mystical':
            scroll = 'mystical'
            full_scroll_name = 'Mystical Scroll'
        elif scroll_raw == 'stones' or scroll_raw == 'ss':
            scroll = 'ss'
            full_scroll_name = 'Summoning Stone'
        elif scroll_raw == 'ld':
            scroll = 'ld'
            full_scroll_name = 'L/D Scroll'
        elif scroll_raw == 'ls' or scroll_raw == 'legendary':
            scroll = 'ls'
            full_scroll_name = 'Legendary Scroll'
        elif any(x == scroll_raw for x in ['wind', 'water', 'fire']):
            scroll = scroll_raw
            full_scroll_name = '{} Scroll'.format(scroll_raw)

        c.execute('SELECT user,'+scroll+' FROM saves WHERE user=?', (discord_id,))
        exist = c.fetchone()
        if exist is None:
            msg = "You haven't added any summons yet <:FeelsThinkMan:346082076287565824>"
        else:
            new_amount = exist[1] - amount
            if new_amount <= 0:
                new_amount = 0

            c.execute(
                'UPDATE saves SET ' + scroll + ' = ? WHERE user = ?',(new_amount, author.id))
            msg = 'Successfully removed {} {}.'.format(amount, endingChecker(amount, full_scroll_name))
        conn.commit()
        await client.send_message(channel,msg)

@client.event
async def on_member_join(member):
    server = member.server
    msg = 'Welcome {0.mention} to {1.name}!'
    await client.send_message(server, msg.format(member,server))

@client.event
async def on_reaction_add(reaction, user):
    emoji = str(reaction.emoji)
    await client.send_message(reaction.message.channel, emoji)

client.run(config.DISCORD_TOKEN)