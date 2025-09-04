import discord
import requests
from get_gas_prices import get_gas_prices, get_eia_ny_weekly
#importing important libraries to make the bot send me updates
from discord.ext import tasks
import asyncio #enables bot to wait
from datetime import datetime, time
from dotenv import load_dotenv
load_dotenv()
import os


#connecting to discord
intents = discord.Intents.default()
intents.message_content=True
client = discord.Client(intents=intents)



#function to know bot is connected to discord
@client.event
async def on_ready():
    print(f" Logged in as {client.user}")
    schedule_gas_update.start()
   # debug_clock.start()

#adding function to create a reminder/update loop
@tasks.loop(minutes=1)#runs every minute
async def schedule_gas_update():
    tNow= datetime.now().time()#.strftime("%H:%M:%S")
    targeted_times = [time(12,52), time(23,16)]
    #if any(abs((datetime.combine(datetime.today(),t)-datetime.combine(datetime.today(),tNow)).total_seconds())<60 for t in targeted_times):
    if(tNow.hour,tNow.minute) in targeted_times:
        channel = client.get_channel(1395789959553749206)
        if channel:
            result = get_gas_prices("New York")
            
            #fallback if collectAPI fails
            if result.lower().startswith("error"):
                result = get_eia_ny_weekly()
            await channel.send(f"**Scheduled Gas Prices Update:**\n{result}")
   # print(f"[DEBUG] The time is now {tNow}")

@schedule_gas_update.before_loop
async def before_schedule():
    await client.wait_until_ready()

#function for the bot to "hear" the message of the users 
#params = message that the function will read
@client.event
async def on_message(message):
    #instance so that the bot doesnt talk to itself
    if message.author == client.user:
        return #returns nothing
    
    #check if the message is !gas
    if message.content.startswith("!gas"):
        parts = message.content.split(maxsplit=1)# split into !gas and state name
        if len(parts) == 1:
            await message.channel.send("Please specify a state, e.g., '!gas new york'.")
            return
        
        state = parts[1]
        result = get_gas_prices(state)

        if result.lower().startswith("error"):
            result = get_eia_ny_weekly()

        await message.channel.send(result)



#bot token
token = os.getenv("DISCORD_BOT_TOKEN")
print("DISCORD TOKEN LOADED:", (token[:10]+ "...")if token else "missing")
client.run(token)
