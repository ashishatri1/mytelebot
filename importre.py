import ntplib
from time import ctime
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# Synchronize time with an NTP server
def sync_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        print(f"Time synchronized: {ctime(response.tx_time)}")
    except Exception as e:
        print(f"Time synchronization failed: {e}")

# Regular expression pattern to match valid channel/user IDs
id_pattern = re.compile(r'^.\d+$')

# List of authorized channels for force subscription
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in ['-1002214768044']]

# Initialize the bot with your credentials
app = Client(
    "my_bot",
    api_id=28630913,
    api_hash="2a7fd7bd9995cd7a5416286e6ac420b6",
    bot_token="7018358870:AAFonX8JYsTf5PzK1o0lvFb8Qoyo5lxWsi8"
)

async def is_subscribed(bot, message, channels):
    btn = []
    for channel in channels:
        try:
            chat = await bot.get_chat(channel)
            await bot.get_chat_member(channel, message.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'My Channel', url=chat.invite_link)])
        except Exception as e:
            print(f"Error: {e}")
            pass
    return btn

@app.on_message(filters.private)
async def check_subscription(client, message):
    # Fetch the user's subscription status for all AUTH_CHANNELs
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                btn.append([InlineKeyboardButton("I joined it!", url=f"https://t.me/{username}?start=true")])
                
                # Send the join message
                join_msg = await message.reply_text(
                    text=f"HHuh-? you left my channel... :(\n\nYou need to join it to text here !",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                
                # Listen for the user joining the channel
                @app.on_message(filters.command("start") & filters.private)
                async def after_join(_, joined_message):
                    if message.from_user.id == joined_message.from_user.id:
                        try:
                            # Delete the previous message asking to join the channel
                            await join_msg.delete()
                        except:
                            pass

                        # Send thank you message after they join
                        await message.reply_text(
                            text=f"Thank you for joining! ✨\n\nPlease drop your questions or suggestions/feedback!"
                        )
                return
        except Exception as e:
            print(e)
            return

    # For new users, send a welcome message
    if message.chat.id:  # Check if this is the first message from this user (simple way)
        await message.reply_text(
            text=f"Hi Minerva this side.. I'll reply soon.. thank you for joining ✨\n\nPlease drop your questions or suggestions/feedback in the meantime\n\nThank you for waiting ✨"
        )

# Run the bot
app.run()
