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
memory = [{'role': 'system', 'content': Rile.load("master_prompt", "txt")}]

stats = {
    "level": 0,
    "exp": 0,
    "exp_to_next_level": 16,
    "health": 100,
    "max_health":100,
    "mana": 10,
    "max_mana":10,
    "hp_regeneration_per_hour": 10,
    "movement_speed_meter_per_second": 6,
    "attack_damage": 10,
    "attack_speed_per_second": 0.5,
    "physical_defense": 1,
    "magic_defense": 1,
    "mana_regeneration_per_hour": 1,
    "mana_output_per_second": 1,
    "mana_control_in_%": 5,
    "iq_score": 80,
    "divinity_rating": 0
    }

# - Health Points (HP): 100/100 maximum
# - HP Regeneration: 10/hour
# - Movement Speed: 6 meters/second
# - Attack Damage: 10
# - Attack Speed: 0.5 per second
# - Physical Defense: 1
# - Magic Defense: 1
# - Mana Pool: 10/10
# - Mana Regeneration: 1/hour
# - Mana Output: 1/second
# - Mana Control: 5% (logarithmic scale 10% novice 100% above god)
# - IQ Score: 80
# - Divinity Rating: 0

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
        model="gpt-oss:20b",
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
        model="gpt-oss:20b",
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
    memory.insert(1,{"role": "system", "content": f"Current stats: {stats}, current inventory: {inventory}"})
    memory.append({'role': 'user', 'content': message})
    response = ollama.chat(
        model="gpt-oss:20b",
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
                elif response:
                    await message.reply(response)
                else:
                    await message.reply("I'm sorry, I couldn't generate a response at this time.")  





intents = discord.Intents.default()
intents.message_content = True
bot = BasicDiscordBot(intents=intents)
bot.run(Rile.load(".discord", "txt"))
print("Bot has stopped running.")