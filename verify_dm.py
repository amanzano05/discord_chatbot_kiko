import unittest
from unittest.mock import MagicMock, Mock
import sys

# Mock discord
sys.modules["discord"] = MagicMock()
sys.modules["discord.ext"] = MagicMock()
sys.modules["discord.ext.commands"] = MagicMock()
sys.modules["openai"] = MagicMock() # Mock openai to avoid import error

import main
from main import should_reply_to, bot

# Helper to mock DMChannel class for isinstance
class MockDMChannel:
    pass

main.discord.DMChannel = MockDMChannel

class TestDMResponse(unittest.TestCase):
    def setUp(self):
        # Reset bot user name for each test
        bot.user = MagicMock()
        bot.user.name = "Kiko"

    def test_reply_in_dm_no_keyword(self):
        print("Testing DM with NO keyword...")
        # Mock message in DM channel
        msg = MagicMock()
        # Use our dummy class instance
        msg.channel = MockDMChannel() 
        
        msg.content = "hello" # No "kiko"
        
        should = should_reply_to(msg)
        print(f"Should reply: {should}")
        self.assertTrue(should, "Bot should reply in DM without keyword")

    def test_reply_in_text_channel_with_keyword(self):
        print("Testing Guild Channel WITH keyword...")
        msg = MagicMock()
        # Make it NOT a DM channel (just a different mock class)
        msg.channel.__class__ = MagicMock() 
        msg.content = "hey kiko help"
        
        should = should_reply_to(msg)
        print(f"Should reply: {should}")
        self.assertTrue(should, "Bot should reply in Guild if keyword present")

    def test_ignore_in_text_channel_no_keyword(self):
        print("Testing Guild Channel WITHOUT keyword...")
        msg = MagicMock()
        msg.channel.__class__ = MagicMock()
        msg.content = "hello world"
        
        should = should_reply_to(msg)
        print(f"Should reply: {should}")
        self.assertFalse(should, "Bot should NOT reply in Guild without keyword")

if __name__ == "__main__":
    unittest.main()
