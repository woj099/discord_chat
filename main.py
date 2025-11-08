# import sys
# import os
#   #Add the path to your file_manager package
# sys.path.append('/home/admin/Projects/git/file')  # The directory containing file_manager folder
from math import e, inf
from pstats import Stats
import discord
from typing import Optional
import ollama
from file_manager import File
from time import time as current_time
Rile = File("file_manager", "logging_folder", "log_file")
game_info = File("game")

file_name = game_info.every_file(2)



# memory = File()
memory = [{'role': 'system', 'content': "You are a DM narrateing a medival fantasy world. The user is a peasant starting his adventure. if you want to add stats or items to his inventory, just mention it in your response. do not give user predefined options, let them choose freely. if fights are too easy make them harder. after each fight you must tell what items and stats the user gained. there is a second bot that will keep track of the user's stats and inventory. you must inform the user of any changes to their stats or inventory in your responses. Remember to write exp, mana, health, etc, changes. Try to not be too long in one location, so that story keeps moving."}]


stats = {
    "level": 0,
    "exp": 0,
    "exp_to_next_level": 16,
    "health": 100,
    "max_health":100,
    "mana": 10,
    "max_mana":10
    }

inventory = {
    "silver_coins": 2,
    "copper_coins": 50,
    "iron_sword": "basic_iron_sword",
    "basic_clothes": "worn_out_clothes"
}



memory.insert(2,{"role": "system", "content": f"stats: {stats}, inventory: {inventory}"})


def stasts_extract(text: str) -> Optional[str]:
    global stats, inventory
    Chat_response = ollama.chat(
        model="deepseek-r1:14b",
        messages=[{"role": "system", "content": Rile.load("stat_append", "txt")},
                  {"role": "system", "content": f"stats: {stats}, inventory: {inventory}"},
                  {"role": "system", "content": text}]
    )
    response_content = Chat_response['message']['content']
    ###### to delete ######
    Rile.save(f"{response_content}\n", "statchangetest", "txt", "a")
    print(response_content)
    try:
        data = response_content.split(",")
        for item in data:
            info = item.split(" ")
            if info[0] == "stat":
                name = info[1]
                if name in stats:  # Check if stat exists
                    stats[name] += int(info[2])  # Add to existing value
                else:
                    stats[name] = int(info[2])  # Create new stat
            elif info[0] == "inv":
                name = info[1]
                if name in inventory:  # Check if item exists
                    inventory[name] += int(info[2])  # Add to existing value
                else:
                    inventory[name] = info[2]  # Create new item
        return response_content
    except Exception as e:
        print(f"Error extracting stats and inventory: {e}")
        return None

def information_extract(text: str) -> Optional[str]:
    response = ollama.chat(
        model="deepseek-r1:14b",
        messages=[{"role": "system", "content": "Extract any information about locations, characters, enemies, or items mentioned in the following text. The output should a CSV file with the following format: '[Place/character/enemy] [information],[Place/character/enemy] [information],...'"},
                  {"role": "user", "content": text}]
    )
    response_content = response['message']['content']
    data = ",".split(response_content)
    for each in range(len(data)):
        info = " ".split(data[each])
        game_info.save(info[1], info[0], "txt", "w")
    # add the possibility for the main bot to retrieve this information by reading files if the response mentions it
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
    print(f"stats: {stats}, inventory: {inventory}")
    try:
        memory.append({'role': 'assistant', 'content': f"{response["message"]}"})
    except:
        print("problem with thinking")
    try:
        stasts_extract(anwser)
    except:
        print("problem with stats extract")
        #################### to delete ####################
    # Rile.save(f"{memory}\n\n\n{response['message']}", f"{current_time()}", "txt", "w", create_dir=True)
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