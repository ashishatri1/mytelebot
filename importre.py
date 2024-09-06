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

# Function to check if the user is subscribed
async def is_subscribed(bot, user_id, channels):
    for channel in channels:
        try:
            await bot.get_chat_member(channel, user_id)
        except UserNotParticipant:
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    return True

# Welcome message that should only be sent on `/start`
@app.on_message(filters.command("start") & filters.private)
async def send_welcome(client, message):
    # Send the welcome message
    await message.reply_text(
        text="Hi, Minerva here! I'll reply soon.. thank you for joining ✨\n\nPlease drop your questions or suggestions/feedback in the meantime\n\nThank you for waiting ✨"
    )

# Middleware to check subscription before processing any other message or command
@app.on_message(filters.private & ~filters.command("start"))
async def check_subscription(client, message):
    # Check if the user is subscribed to the required channels
    is_user_subscribed = await is_subscribed(client, message.from_user.id, AUTH_CHANNEL)
    
    if not is_user_subscribed:
        # If the user is not subscribed, prompt them to join the channel
        btn = []
        for channel in AUTH_CHANNEL:
            try:
                chat = await client.get_chat(channel)
                btn.append([InlineKeyboardButton(f'My Channel', url=chat.invite_link)])
            except Exception as e:
                print(f"Error: {e}")
                return
        
        # Add "I joined it!" button
        btn.append([InlineKeyboardButton("I joined it!", callback_data="check_subscription")])
        
        # Send join prompt message
        await message.reply_text(
            text="HHuh-? you left my channel.. 😕\n\nYou need to join it to text here!",
            reply_markup=InlineKeyboardMarkup(btn)
        )

# Callback query handler for checking subscription status when the "I joined it!" button is clicked
@app.on_callback_query(filters.regex("check_subscription"))
async def check_subscription_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    
    # Check if the user is now subscribed
    is_user_subscribed = await is_subscribed(client, user_id, AUTH_CHANNEL)
    
    if is_user_subscribed:  # User is subscribed
        try:
            # Delete the "Please join" message
            await callback_query.message.delete()
            
            # Send a thank-you message
            await client.send_message(
                chat_id=user_id,
                text="Thank you for joining! ✨\nNow drop your feedback/suggestion.."
            )
        except Exception as e:
            print(f"Error while deleting join message: {e}")
    else:
        # Notify the user that they still need to join
        await callback_query.answer("You still need to join the channel.", show_alert=True)

# Run the bot
app.run()
