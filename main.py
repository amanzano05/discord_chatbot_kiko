import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Setup OpenAI client for Perplexity
client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

async def get_perplexity_response(query):
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        return "Error: Perplexity API key is missing."

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant and you need to "
                    "engage in a helpful, detailed, polite conversation with a user. Your name is Kiko."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        response = client.chat.completions.create(
            model="sonar",
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if "kiko" is in the message content (case-insensitive)
    if "kiko" in message.content.lower():
        async with message.channel.typing():
            answer = await get_perplexity_response(message.content)
            
            # Discord has a 2000 char limit
            if len(answer) > 2000:
                for i in range(0, len(answer), 2000):
                    await message.channel.send(answer[i:i+2000])
            else:
                await message.channel.send(answer)

    # Important: Process commands so !hello and !ask still work
    await bot.process_commands(message)

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'hello {ctx.author.name}')

@bot.command(name='ask')
async def ask(ctx, *, query):
    async with ctx.typing():
        answer = await get_perplexity_response(query)
        
        if len(answer) > 2000:
            for i in range(0, len(answer), 2000):
                await ctx.send(answer[i:i+2000])
        else:
            await ctx.send(answer)

if __name__ == "__main__":
    if not TOKEN or TOKEN == "your_token_here":
        print("Error: DISCORD_TOKEN not found in .env file or is still the default value.")
    else:
        bot.run(TOKEN)
