from telethon.tl.types import PeerChannel
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telethon import events
import asyncio
import logging
from random import choice
from bot import app

# Weighted list of reactions to reflect probabilities
reactions = ["💋"] * 8 + ["💔"] * 1 + ["❤‍🔥"] * 1

# Sequential reaction handler
@app.on(events.NewMessage(func=lambda e: isinstance(e.message.peer_id, PeerChannel)))
async def react(event):
    for idx, client in enumerate(app.clients):  # Iterate over all clients sequentially
        await asyncio.sleep(2)
        try:
            reaction = [ReactionEmoji(emoticon=choice(reactions))]
            await client(SendReactionRequest(
                peer=await event.get_chat(),
                msg_id=event.id,
                reaction=reaction,
            ))
            print(f"Reaction sent by bot {idx + 1}: {(await client.get_me()).username}")
        except Exception as e:
            print(f"Bot {idx + 1}: {(await client.get_me()).username} failed to send reaction: {e}")
        
        # Wait before the next bot sends its reaction
        await asyncio.sleep(5)  # Adjust the wait time as needed
