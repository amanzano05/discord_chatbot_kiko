import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Mock discord and openai before importing main
sys.modules["discord"] = MagicMock()
sys.modules["discord.ext"] = MagicMock()
sys.modules["discord.ext.commands"] = MagicMock()
sys.modules["openai"] = MagicMock()

# Import main after mocking
import main

class TestDeepAsk(unittest.IsolatedAsyncioTestCase):
    async def test_get_channel_history_limit(self):
        print("Testing get_channel_history with limit 500...")
        
        # Mock channel and history
        mock_channel = MagicMock()
        
        # Create 600 mock messages
        mock_messages = []
        for i in range(600):
            msg = MagicMock()
            msg.id = i
            msg.content = f"Message {i}"
            msg.author.name = "User" if i % 2 == 0 else "Kiko"
            # bot.user needs to match "Kiko" for role assignment logic in main.py
            # In main.py: role = "assistant" if msg.author == bot.user else "user"
            mock_messages.append(msg)
            
        # Mock bot.user
        main.bot.user = MagicMock()
        main.bot.user.name = "Kiko"
        
        # Async iterator mock for channel.history
        async def history_iterator(limit=None, oldest_first=False):
            count = 0
            # Return last 'limit' messages, reversed because history gives newest first usually
            # But the mock generator just yields them.
            # in main.py: async for msg in channel.history(limit=limit, oldest_first=False):
            messages_to_yield = mock_messages[:limit] if limit else mock_messages
            for msg in messages_to_yield:
                yield msg

        mock_channel.history = history_iterator
        
        # Note: main.py reverses the history at the end: return history[::-1]
        history = await main.get_channel_history(mock_channel, limit=500, exclude_ids=[])
        
        print(f"Retrieved {len(history)} messages.")
        self.assertEqual(len(history), 500)
        
        # Verify specific content
        # Since we yielded 0 to 499, and main.py appends then reverses...
        # history[0] should be the last appended? No, history[::-1] means last appended is first?
        # main.py: history.append(...) -> [msg0, msg1, ...]
        # return history[::-1] -> [..., msg1, msg0]
        # So history[0] should be the LAST cached message (msg 499), which corresponds to oldest if the iterator yields newest first.
        # But our mock yields 0..499.
        # Let's just check count for now.

    @patch("main.client.chat.completions.create")
    async def test_perplexity_call_large_context(self, mock_create):
        print("Testing Perplexity API call with large context...")
        
        # Create a large history
        large_history = [{"role": "user", "content": f"msg {i}"} for i in range(500)]
        query = "[User]: Summary of all this?"
        
        # Set API key to pass check
        main.PERPLEXITY_API_KEY = "test_key"
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Summary: A lot of messages."
        mock_create.return_value = mock_response
        
        response = await main.get_perplexity_response(query, large_history)
        
        print("Response received:", response)
        self.assertEqual(response, "Summary: A lot of messages.")
        
        # Check that the messages list passed to API is reasonable logic-wise
        # It merges messages so length won't be 501 (system + 500 + query) if roles repeat
        # In our mock, roles repeat "user", "user"... so it should merge into one GIANT user message?
        # main.py:
        # for msg in history:
        #   if merged_history and merged_history[-1]["role"] == msg["role"]:
        #       merged_history[-1]["content"] += ...
        
        # So yes, 500 user messages become 1 big message.
        call_args = mock_create.call_args
        messages_arg = call_args.kwargs['messages']
        
        # System prompt + 1 merged history + 1 current query (merged or new)
        # In main.py: if messages and messages[-1]["role"] == "user": merge query
        # So System + 1 giant user blob (history + query)
        
        self.assertLessEqual(len(messages_arg), 3) 
        print(f"Final messages structure length: {len(messages_arg)}")

if __name__ == "__main__":
    unittest.main()
