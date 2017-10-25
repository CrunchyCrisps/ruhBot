import discord
import asyncio
import urlfetch
import requests
import json
import config
import os.path
import sys
import random
import discord.ext.commands.bot
from discord import opus
from youtube import getYoutubeURL, getTitleForURL, getIdForURL, checkVideoDuration

client = discord.Client()

# players
player = None
idle_player = None

# player status
playing = False
play_idle = False

# lists for songs
playlist = config.KPOP_PLAYLIST
idle_songs = []
queue = []

# current volume
volume = 0.4

def songDone():
    global playing
    playing = False
    if len(queue) > 0:
        coro = playNextSong()
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except:
            pass
    else:
        global play_idle
        play_idle = True
        coro = playIdle()
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except:
            pass

def nextInPlaylist():
    if play_idle is True:
        coro = playIdle()
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except:
            pass

def updateIdleSongs(title):
    if len(idle_songs) >= 10:
        del idle_songs[0]
    idle_songs.append(title)

def chooseRandomFileFromDir(dir):
    song_name_ext = random.choice(os.listdir(dir))
    song_path = '{}/{}'.format(dir,song_name_ext)
    song_name = song_name_ext[:-4]
    return [song_name,song_path]

def findLastRequestByUser(user_id):
    for index, request in enumerate(queue):
        if request[1] == user_id:
            request_index = index
            request_title = getTitleForURL(request[0])
    return [request_index,request_title]

async def playIdle():
    if client.is_voice_connected(client.get_server('332678368837369857')) is False:
        sr_channel = client.get_channel('360852377344933900')
        await client.join_voice_channel(sr_channel)
    song_info = chooseRandomFileFromDir(playlist)
    while song_info[0] in idle_songs:
        song_info = chooseRandomFileFromDir(playlist)
    song_title = song_info[0]
    song_path = song_info[1]
    updateIdleSongs(song_title)
    await createIdlePlayer(song_path,song_title)
    await client.change_presence(game=discord.Game(name=song_title))

async def playSong(url):
    for voice_client in client.voice_clients:
        global playing
        global player
        if voice_client.server.id == '332678368837369857' and playing is False:
            player = await voice_client.create_ytdl_player(url, after=songDone)
            player.volume = volume
            player.start()
            playing = True
            song = player.title
            await client.change_presence(game=discord.Game(name=song))
            await client.send_message(client.get_channel('360860040602583041'), 'Now playing: {}'.format(song))
            await client.edit_channel(client.get_channel('360860040602583041'), topic='Now playing: {}'.format(song))

async def playNextSong():
    next_song = queue[0][0]
    del queue[0]
    await playSong(next_song)

async def createIdlePlayer(file,song):
    for voice_client in client.voice_clients:
        global idle_player
        if voice_client.server.id == '332678368837369857':
            idle_player = voice_client.create_ffmpeg_player(file, after=nextInPlaylist)
            idle_player.volume = volume
            idle_player.start()
            await client.edit_channel(client.get_channel('360860040602583041'), topic='Now playing: {}'.format(song))

@client.event
async def on_ready():
    print('Ruh DJ ready to disc the jogs')

@client.event
async def on_error(event, arg1):
    await client.send_message(await client.get_user_info('120143205751586819'), '```{} used\n\n{}\n\nin {} on {}\n\n{}\n```'.format(arg1.author, arg1.content, arg1.channel, arg1.server, sys.exc_info()))

@client.event
async def on_message(message):
    global play_idle
    author = message.author
    content = message.content
    channel = message.channel

    if content == '!play':
        if author.id == '120143205751586819':
            play_idle = True
            await playIdle()

    elif content == '!stop':
        if player is not None and player.is_playing():
            play_idle = False
            player.stop()
            await client.change_presence(game=None)
            await client.edit_channel(client.get_channel('360860040602583041'), topic='Request a song using !sr or listen to random songs using !play')
        elif idle_player is not None and idle_player.is_playing():
            play_idle = False
            idle_player.stop()
            await client.change_presence(game=None)
            await client.edit_channel(client.get_channel('360860040602583041'), topic='Request a song using !sr or listen to random songs using !play')
        else:
            await client.send_message(channel, 'Da fuk bruh im not even jamming out')

    elif content == '!skip':
        if author.id == '120143205751586819' or author.id == '106558668912205824':
            if player is not None and player.is_playing():
                player.stop()
                await client.send_message(channel, 'Skipped {}.'.format(player.title))
            elif idle_player.is_playing():
                idle_player.stop()

    elif content == '!queue':
        if len(queue) > 0:
            song_list = []
            for request in queue:
                song_list.append(request[2])
            songs = ', '.join(song_list)
            await client.send_message(channel, 'Current queue: {}'.format(songs))
        else:
            await client.send_message(channel, 'There are no songs in queue.')

    elif content == '!wrongsong':
        discord_id = author.id
        last_request = findLastRequestByUser(discord_id)
        index = last_request[0]
        title = last_request[1]
        del queue[index]
        await client.send_message(channel, 'Removed {} from the queue.'.format(title))

    elif content.startswith('!sr'):
        # checks if bot is already connected to voice
        if client.is_voice_connected(client.get_server('332678368837369857')) is False:
            sr_channel = client.get_channel('360852377344933900')
            await client.join_voice_channel(sr_channel)

        # checks if request was made in the songrequest channel
        if channel.id == '360860040602583041':
            # gets url and title for requested song
            if 'www.youtube.com' not in content:
                search_term = content[4:]
                video_info = getYoutubeURL(search_term)
                url = video_info[0]
                title = video_info[1]
            else:
                url = content.split()[1]
                title = getTitleForURL(url)

            # checks if video fits the maximum duration
            video_id = getIdForURL(url)
            if checkVideoDuration(video_id,config.MAX_VIDEO_LENGTH) is True:
                # checks if a requested song is currently being played
                if playing is False:
                    # checks if idle playlist is being played and stops the idle player if it is
                    if idle_player is not None and idle_player.is_playing():
                        play_idle = False
                        idle_player.stop()
                    await playSong(url)
                else:
                    queue.append([url,author.id,title])
                    await client.send_message(channel,'{} was added to the queue.'.format(title))
            else:
                await client.send_message(channel,'The requested song is too long.')
        else:
            await client.send_message(channel, 'Try again in the songrequest channel.')

    elif content.startswith('!vol'):
        if author.id == '120143205751586819' or author.id == '106558668912205824':
            global volume
            new_volume = float(content.split()[1])
            if player is not None and player.is_playing():
                player.volume = new_volume
            elif idle_player.is_playing():
                idle_player.volume = new_volume
            volume = new_volume
            await client.send_message(channel, 'Volume set to {}'.format(volume))

    elif content.startswith('!playlist'):
        global playlist
        if content.split()[1].lower() == 'metal':
            playlist = config.METAL_PLAYLIST
            await client.send_message(channel, 'Changed playlist to Metal.')
        elif content.split()[1].lower() == 'kpop':
            playlist = config.KPOP_PLAYLIST
            await client.send_message(channel,'Changed playlist to K-Pop.')

    elif content == '?vol':
        await client.send_message(channel, 'Volume: {}'.format(volume))

client.run(config.DJToken)
