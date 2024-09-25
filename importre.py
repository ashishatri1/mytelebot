import ntplib 
from time import ctime
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import json

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

# Load admin IDs (you should replace these with real admin user IDs)
ADMINS = [7073941551]  # Add the user_id(s) of the admin(s)

# Initialize the bot with your credentials
app = Client(
    "my_bot",
    api_id=28630913,
    api_hash="2a7fd7bd9995cd7a5416286e6ac420b6",
    bot_token="7490788125:AAE9VjvI4GV9NmPyqnXVMFHMvFzAUo0c9-c"
)

# Load or initialize the subscribers list
try:
    with open("subscribers.json", "r") as f:
        subscribers = json.load(f)
except FileNotFoundError:
    subscribers = []

# Function to save subscribers
def save_subscribers():
    with open("subscribers.json", "w") as f:
        json.dump(subscribers, f)

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

# Middleware to check subscription before processing any other message or command
@app.on_message(filters.private & ~filters.command("start"))
async def check_subscription(client, message):
    user_id = message.from_user.id
    
    # Check if the user is subscribed to the required channels
    is_user_subscribed = await is_subscribed(client, user_id, AUTH_CHANNEL)
    
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
            text="HHuh-? you left my channel.. 😕\n\nYou need to join it then click\n'I joined it' button!",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    else:
        # Add user to the subscribers list if not already present
        if user_id not in subscribers:
            subscribers.append(user_id)
            save_subscribers()

# Callback query handler for checking subscription status when the "I joined it!" button is clicked
@app.on_callback_query(filters.regex("check_subscription"))
async def check_subscription_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    
    # Check if the user is now subscribed
    is_user_subscribed = await is_subscribed(client, user_id, AUTH_CHANNEL)
    
    # Store the message ID of the "You did not join it!" message
    if not hasattr(callback_query, 'not_joined_message_id'):
        callback_query.not_joined_message_id = None
    
    if is_user_subscribed:  # User is subscribed
        try:
            # Delete the "Please join" message
            await callback_query.message.delete()
            
            # If the "You did not join it!" message exists, delete it
            if callback_query.not_joined_message_id:
                await client.delete_messages(chat_id=user_id, message_ids=callback_query.not_joined_message_id)
                # Reset not_joined_message_id after deletion
                callback_query.not_joined_message_id = None
            
            # Send a thank-you message
            await client.send_message(
                chat_id=user_id,
                text="Thank you for joining! ✨\nYou can send your question now.."
            )
        except Exception as e:
            print(f"Error while deleting join message: {e}")
    else:
        # Notify the user that they still need to join
        if callback_query.not_joined_message_id:
            await client.delete_messages(chat_id=user_id, message_ids=callback_query.not_joined_message_id)
        
        not_joined_message = await client.send_message(
            chat_id=user_id,
            text="You did not join it!"
        )
        callback_query.not_joined_message_id = not_joined_message.id
# Run the bot
app.run()
