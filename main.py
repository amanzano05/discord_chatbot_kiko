import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'hello {ctx.author.name}')

if __name__ == "__main__":
    if not TOKEN or TOKEN == "your_token_here":
        print("Error: DISCORD_TOKEN not found in .env file or is still the default value.")
    else:
        bot.run(TOKEN)
