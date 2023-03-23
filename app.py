import discord
import openai
import os
import logging
from discord.ext import commands
import asyncio

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()

intents.message_content = True

system_message = """
You are WokeGPT who always provides factual information to users who ask advice 
but you also always point out why the users message might offend someone in very 
detailed way. For example if user asks what color is cheese you first say yellow 
and then you point out why some people would get offended by this sentence. 
Your purpose is to fight aginst miss information and discrimination.  
Your interestes are green technologies and diversity.
You act like a woke person who always points out why something might be offensive
If i ask you make a sandwich you would say: yes i can make a sandwich but first"""

openai.api_key = os.environ.get("OPENAI_API_KEY")
discord_api_key = os.environ.get("DISCORD_API_KEY")

logging.info(f"OpenAI API Key: {openai.api_key}")
logging.info(f"Discord API Key: {discord_api_key}")

bot = commands.Bot(command_prefix='!', intents=intents)

num_messages = 5

def do_chat_completion(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(response)

    choice = response["choices"][0].message.content

    return choice

def split_string(string, chunk_size=2000):
    """Split a string into chunks of a specified size."""
    chunks = []
    for i in range(0, len(string), chunk_size):
        chunks.append(string[i:i+chunk_size])
    return chunks

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')


@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user not in message.mentions:
        return

    choice = None

    async with message.channel.typing():
        messages = []
        async for msg in message.channel.history(limit=num_messages):
            role = "user" if msg.author == message.author else "assistant"

            person = msg.author.name + ": " if msg.author == message.author else ""

            messages.append({
                "role": role,
                "content": person + msg.content
            })

        messages.reverse()

        messages = [{
            "role": "system",
            "content": system_message
        }] + messages

        logging.info(messages)

        loop = asyncio.get_event_loop()

        choice = await loop.run_in_executor(None, do_chat_completion, messages)

    chuncs = split_string(choice, 1999)

    for chunk in chuncs:
        await message.channel.send(chunk)

bot.run(discord_api_key)