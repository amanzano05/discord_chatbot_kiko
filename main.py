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

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'hello {ctx.author.name}')

@bot.command(name='ask')
async def ask(ctx, *, query):
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        await ctx.send("Error: Perplexity API key is missing.")
        return

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant and you need to "
                    "engage in a helpful, detailed, polite conversation with a user."
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
        answer = response.choices[0].message.content
        
        # Discord has a 2000 char limit, split if necessary or just send first chunk for now
        if len(answer) > 2000:
            for i in range(0, len(answer), 2000):
                await ctx.send(answer[i:i+2000])
        else:
            await ctx.send(answer)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if not TOKEN or TOKEN == "your_token_here":
        print("Error: DISCORD_TOKEN not found in .env file or is still the default value.")
    else:
        bot.run(TOKEN)
