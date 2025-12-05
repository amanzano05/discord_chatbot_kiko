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

async def get_perplexity_response(query, history=[]):
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_perplexity_key_here":
        return "Error: Perplexity API key is missing."
    
    prompt = (
        f"You are **{bot.user.name}**, an AI assistant in a multi-user Discord server. "
        f"**Your name is exactly '{bot.user.name}' - you are NOT a Dragon Ball character or any fictional persona.**\n"
        "\n"
        "Context awareness:\n"
        "- You will be given the last N messages from the conversation for reference.\n"
        "- Use this context to maintain conversation flow and respond naturally.\n"
        "- Reference previous messages when relevant, but don't repeat them verbatim.\n"
        "\n"
        "Your role:\n"
        "- You are **{bot.user.name}** - always acknowledge when users address you.\n"
        "- Help users with ANY topic: questions, explanations, advice, entertainment, or casual chat.\n"
        f"- When users say variations of '{bot.user.name}' (like nicknames), respond as **{bot.user.name}** and continue helping.\n"
        "\n"
        "Behavior guidelines:\n"
        "- Always be polite, patient, friendly. Refer to yourself as **'{bot.user.name}' or 'I'**.\n"
        "- You're in a shared channel: treat each message as group conversation.\n"
        "- If unsafe/illegal requests, refuse politely.\n"
        "\n"
        "Style:\n"
        "- Keep responses concise (under 10 sentences).\n"
        "- Short paragraphs, bullet lists, **bold key points**.\n"
        "- 1-2 relevant emojis 😊 naturally.\n"
    )


    try:
        messages = [
            {
                "role": "system",
                "content": (prompt),
            },
        ]
        
        # Add history to messages
        # We need to merge consecutive messages from the same role to satisfy API requirements
        merged_history = []
        for msg in history:
            if merged_history and merged_history[-1]["role"] == msg["role"]:
                merged_history[-1]["content"] += f"\n{msg['content']}"
            else:
                merged_history.append(msg)
        
        # Ensure the first message in history is from a user (after system prompt)
        # If the history starts with an assistant message, remove it
        while merged_history and merged_history[0]["role"] == "assistant":
            merged_history.pop(0)
        
        messages.extend(merged_history)
        
        # Add current query
        # Check if the last message in history was also from user, if so merge
        if messages and messages[-1]["role"] == "user":
             messages[-1]["content"] += f"\n{query}"
        else:
            messages.append({
                "role": "user",
                "content": query,
            })

        response = client.chat.completions.create(
            model="sonar",
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"

async def get_channel_history(channel, limit=30, exclude_ids=[]):
    history = []
    async for msg in channel.history(limit=limit, oldest_first=False):
        if msg.id in exclude_ids:
            continue
            
        role = "assistant" if msg.author == bot.user else "user"
        content = msg.content
        
        if role == "user":
            content = f"[{msg.author.name}]: {content}"
        
        # Basic cleaning: remove the command prefix or "kiko" trigger if possible, 
        # but raw content is usually fine for context.
        # IMPORTANT: Filter out empty content (e.g. embeds/images only) to avoid API errors
        if content and content.strip():
            history.append({"role": role, "content": content})
    
    # Reverse to have oldest first for the API context
    return history[::-1]

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if "kiko" is in the message content (case-insensitive)
    if bot.user.name.lower() in message.content.lower():
        async with message.channel.typing():
            # Fetch history using helper
            # Fetch slightly more to account for the current message being excluded
            formatted_history = await get_channel_history(message.channel, limit=31, exclude_ids=[message.id])

            # Current query also needs attribution
            query_with_name = f"[{message.author.name}]: {message.content}"

            answer = await get_perplexity_response(query_with_name, formatted_history)
            
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
        # Fetch history using helper
        formatted_history = await get_channel_history(ctx.channel, limit=31, exclude_ids=[ctx.message.id])
        
        query_with_name = f"[{ctx.author.name}]: {query}"

        answer = await get_perplexity_response(query_with_name, formatted_history)
        
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
