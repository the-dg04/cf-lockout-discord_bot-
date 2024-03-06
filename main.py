import discord
import os
from discord.ext import tasks
from db import *
import asyncio
import time
from dotenv import load_dotenv
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
    if message.author == client.user:
        return
    print(message.content)
    if message.content.startswith('!'):
        global lockout
        options=message.content.split(' ')
        if(options[0]=="!create"):
            lockout=Lockout(options[1],int(options[2]),int(options[3]),float(options[4]))
            client.loop.create_task(on_interval(client))
            await message.channel.send("lockout created")
        elif(options[0]=="!start"):
            await message.channel.send('\n'.join([f"{i['name']}\t{i['points']}\t{i['url']}\t{i['solved_by']}" for i in lockout.start_lockout()]))
        elif(options[0]=="!list"):
            if(lockout.has_started):
                await message.channel.send('\n'.join([f"{i['name']}\t{i['points']}\t{i['url']}\t{i['solved_by']}" for i in lockout.get_problems()]))
            else:
                await message.channel.send("lockout has not been started yet")
        elif(options[0]=="!join"):
            response=lockout.join_user(message.author,options[1])
            await message.channel.send(response)
            # print(f"{options[1]} joined!")
        elif(options[0]=="!leaderboard"):
            await message.channel.send('\n'.join([f"{i[0]}\t{i[1]}" for i in lockout.get_leaderboard()]))
        elif(options[0]=="!commands"):
            commands="""create a lockout:\n!create <lockout name> <initial rating> <number of problems> <duration(in hrs)>\n\nstart the lockout:\n!start\n\njoin the lockout:\n!join <cf handle>\n\nget list of problems:\n!list\n\nget leaderboard\n!leaderboard\n\nget list of commands:\n!commands"""
            await message.channel.send(commands)


client.run(os.getenv("BOT_ID"))