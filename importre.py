import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import ntplib
from time import ctime

# Regular expression pattern to match valid channel/user IDs
id_pattern = re.compile(r'^.\d+$')

# List of authorized channels for force subscription
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in ['-1002214768044']]

# Initialize the bot with your credentials
app = Client(
    "my_bot",
    api_id=28630913,                       # Replace with your actual API ID
    api_hash="2a7fd7bd9995cd7a5416286e6ac420b6",  # Replace with your actual API Hash
    bot_token="7018358870:AAFonX8JYsTf5PzK1o0lvFb8Qoyo5lxWsi8"  # Replace with your actual Bot Token
)

# Function to synchronize time using ntplib
def sync_time():
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        print(f"Time synchronized: {ctime(response.tx_time)}")
    except Exception as e:
        print(f"Failed to sync time: {e}")

# Function to check if the user is subscribed to the authorized channels
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

# Handle all private messages
@app.on_message(filters.private)
async def check_subscription(client, message):
    # Force subscribe logic
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                btn.append([InlineKeyboardButton("I joined it!", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(
                    text=f"HHuh-? you left my channel... :(\n\nYou need to join it to text here !",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            print(e)
            return

    # If subscribed, respond normally
    await message.reply_text(
        text=f"Hi minerva this side.. I'll reply soon.. thank you for joining ✨\n\nPlease drop your questions or suggestions/feedback in the meantime\n\nThank you for waiting ✨"
    )

# Synchronize time before starting the bot
sync_time()

# Start the bot
app.run()
