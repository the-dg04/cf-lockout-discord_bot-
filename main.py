import discord
import os
from discord.ext import tasks
from lockout_funcs import *
import asyncio
import time
from dotenv import load_dotenv
import events
load_dotenv()

intent=discord.Intents.default()
intent.presences=True
intent.message_content=True
lockout=""
client = discord.Client(intents=intent)

async def on_interval(clt):
    interval=5
    channel = clt.get_channel(int(os.getenv("CHANNEL_ID")))
    print(channel)
    global lockout


    while True:
        try:
            if(((lockout.has_ended) or (time.time()-lockout.start_time>=lockout.lockout_length) or (lockout.max_points>=lockout.maximum_attainable_points))):
                    await channel.send("lockout ended")
                    leaderboard=lockout.get_leaderboard()
                    await channel.send('\n'.join([f"{i[0]}\t{i[1]}" for i in leaderboard]))
                    if(leaderboard):
                        await channel.send(f"Winner : {leaderboard[0][1]} with {leaderboard[0][0]} points!")
                    lockout.end_lockout()
                    break
        except:
            pass
        try:
            if(lockout.has_started):
                message_queue=lockout.update()
                for i in message_queue:
                    await channel.send(f"{i} has been solved by {message_queue[i]}!")
        except:
            pass
        await asyncio.sleep(interval)

@client.event
async def on_ready():
    channel = client.get_channel(int(os.getenv("CHANNEL_ID")))
    await channel.send('bot ready')

@client.event
async def on_message(message):
    # print(message.author)
    if message.author == client.user:
        return
    if message.content.startswith('!'):
        global lockout
        options=message.content.split(' ')
        if(options[0]=="!create"):
            lockout=Lockout(options[1],int(options[2]),int(options[3]),float(options[4]))
            client.loop.create_task(on_interval(client))
            await message.channel.send("lockout created")
        elif(options[0]=="!start"):
            await events.handle_start(message,options,lockout)
        elif(options[0]=="!list"):
            await events.handle_list(message,options,lockout)
        elif(options[0]=="!join"):
            await events.handle_join(message,options,lockout)
        elif(options[0]=="!leaderboard"):
            await events.handle_leaderboard(message,options,lockout)
        elif(options[0]=="!commands"):
            await events.handle_commands(message,options,lockout)

client.run(os.getenv("BOT_ID"))