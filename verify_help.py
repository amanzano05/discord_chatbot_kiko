import unittest
from unittest.mock import MagicMock, AsyncMock
import sys

# Mock discord
sys.modules["discord"] = MagicMock()
sys.modules["discord.ext"] = MagicMock()
commands_mock = MagicMock()
sys.modules["discord.ext.commands"] = commands_mock
# Crucial: Link it so 'from discord.ext import commands' finds it
sys.modules["discord.ext"].commands = commands_mock
sys.modules["openai"] = MagicMock()

# Manual mock class to ensure decorators work
class MockBot:
    def __init__(self, *args, **kwargs):
        self.user = MagicMock()
    def command(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def event(self, func):
        return func
    def process_commands(self, *args, **kwargs):
        pass

# Assign the CLASS to the module
commands_mock.Bot = MockBot

import main

class TestHelpCommand(unittest.IsolatedAsyncioTestCase):
    async def test_help_output(self):
        print(f"DEBUG: Type of main.help is {type(main.help)}")
        print(f"DEBUG: main.help is {main.help}")
        print("Testing help command...")
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        await main.help(ctx)
        
        # Check that send was called
        self.assertTrue(ctx.send.called)
        
        # Get the argument passed to send
        args, _ = ctx.send.call_args
        help_message = args[0]
        
        print(f"Help message sent:\n{help_message}")
        
        # Verify key parts are present
        self.assertIn("Kiko Bot Help", help_message)
        self.assertIn("!deep_ask", help_message)
        self.assertIn("DM me", help_message)
        self.assertIn("!ask", help_message)

if __name__ == "__main__":
    unittest.main()
