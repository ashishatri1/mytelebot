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
    bot_token="7506256133:AAH5WcD86_vbrHKYyRSUnejEAOfiGL8oKpA"
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
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                btn.append([InlineKeyboardButton("I joined it!", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(
                    text=f"Huh-? you left my channel.. why?😕\n\nYou need to join it to text me here !",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            print(e)
            return

    await message.reply_text(
        text=f"Hi minerva this side.. I'll reply soon.. thank you for joining ✨\n\nPlease drop your questions or suggestions/feedback in the meantime\n\nThank you for waiting ✨"
    )

# Synchronize time before starting the bot
sync_time()

# Start the bot
app.run()
