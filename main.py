# import sys
# import os
#   #Add the path to your file_manager package
# sys.path.append('/home/admin/Projects/git/file')  # The directory containing file_manager folder
from math import e, inf
import discord
from typing import Optional
import ollama

# from git.file import file_manager
# ['qwen3:4b',"deepseek-r1:14b"][0]

from file_manager import File


Rile = File("file_manager", "logging_folder", "log_file")
game_info = File("game")



# Rile.save("data", "dataname", "txt", "a")

Rile.save("", "stat_append", "txt")

file_name = game_info.every_file(2)



# memory = File()
memory = [{'role': 'system', 'content': "You are a DM in a medival fantasy world. The user is a peasant starting his adventure. if you want to add stats or items to his inventory, just mention it in your response. do not give user predefined options, let them choose freely. if fights are too easy make them harder."}]



stats = [
    {"level": 0},
    {"exp_now": 0},
    {"exp_max": 1},
    {"class": None},
    {"health": 100},
    {"max_health":100},
    {"mana": 10},
    {"max_mana":10}
    ]
inventory = [
    {"platinum": 0},
    {"gold": 0},
    {"silver": 1},
    {"bronze": 34},
    {"iron sword": "basic iron sword"}
    ]


memory.insert(2,{"role": "system", "content": f"stats: {stats}, inventory: {inventory}"})


def stasts_extract(text: str) -> Optional[str]:
    global stats, inventory
    Chat_response = ollama.chat(
        model="deepseek-r1:14b",
        messages=[{"role": "system", "content": Rile.load("stat_append", "txt")},
                  {"role": "user", "content": f"stats: {stats}, inventory: {inventory}"}]
    )
    response_content = Chat_response['message']['content']
    try:
        data = ",".split(response_content)
        for item in data:
            info = " ".split(item)
            for each in stats:
                if info[0] == "stat":
                    for each in range(len(stats)):
                        name = info[1]
                        if name == stats[each][name]:
                            stats[each][name] = stats[each][name] + int(info[2])
                if info[0] == "inv":
                    for each in inventory:
                        name = info[1]
                        if name == inventory[each][name]:
                            inventory[each][name] = inventory[each][name] + int(info[2])
                        else:
                            inventory.append({name: info[2]})
        return response_content
    except Exception as e:
        print(f"Error extracting stats and inventory: {e}")
        return None


def ask_ai(message):
    if len(memory) > 20:
        memory.pop(2)
    memory.pop(1)
    memory.insert(1,{"role": "system", "content": f"stats: {stats}, inventory: {inventory}"})
    memory.append({'role': 'user', 'content': message})
    response = ollama.chat(
        model="deepseek-r1:14b",
        messages=memory
    )
    anwser = response['message']['content']
    # print(response["message"]["thinking"])

    try:
        memory.append({'role': 'assistant', 'content': f"{response["message"]}"})
    except:
        print("problem with thinking")
    try:
        stasts_extract(anwser)
    except:
        print("problem with stats extract")
    return anwser

# Set up logging

class BasicDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author.id == self.user.id:
            return

        # Check if the bot is mentioned or if we're in a DM
        is_mentioned = self.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)
        
        # Respond to direct messages or when mentioned
        if is_dm or is_mentioned:
            async with message.channel.typing():
                #####################################################
                # Asking AI to generate a response and send it back #
                #####################################################
                response = ask_ai(message.content)
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                if response:
                    await message.reply(response)
                else:
                    await message.reply("I'm sorry, I couldn't generate a response at this time.")  





intents = discord.Intents.default()
intents.message_content = True
bot = BasicDiscordBot(intents=intents)
bot.run(Rile.load(".discord", "txt"))
print("Bot has stopped running.")