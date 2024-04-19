async def handle_start(message,options,lockout):
    await message.channel.send('\n'.join([f"{i['name']}\t{i['points']}\t{i['url']}\t{i['solved_by']}" for i in lockout.start_lockout()]))

async def handle_list(message,options,lockout):
    if(lockout.has_started):
        await message.channel.send('\n'.join([f"{i['name']}\t{i['points']}\t{i['url']}\t{i['solved_by']}" for i in lockout.get_problems()]))
    else:
        await message.channel.send("lockout has not been started yet")

async def handle_join(message,options,lockout):
    response=lockout.join_user(message.author,options[1])
    await message.channel.send(response)

async def handle_leaderboard(message,options,lockout):
    await message.channel.send('\n'.join([f"{i[0]}\t{i[1]}" for i in lockout.get_leaderboard()]))

async def handle_commands(message,options,lockout):
    commands="""create a lockout:\n!create <initial rating> <number of problems> <duration(in hrs)>\n\nstart the lockout:\n!start\n\njoin the lockout:\n!join <cf handle>\n\nget list of problems:\n!list\n\nget leaderboard\n!leaderboard\n\nget list of commands:\n!commands"""
    await message.channel.send(commands)