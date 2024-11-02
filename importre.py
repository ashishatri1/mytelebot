import ntplib
from time import ctime
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient
import asyncio

# MongoDB URI (replace with your actual URI)
MONGO_URI = "mongodb+srv://cluster0:cluster0@cluster0.lpcw7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client and select the database and collection
client = MongoClient(MONGO_URI)
db = client["telegram_bot_db"]
subscribers_collection = db["subscribers"]

# Synchronize time with an NTP server
def sync_time():
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
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
    bot_token="7506256133:AAF506w0z6Tw7ugvtJYdTGm-X9AtLCugz94"
)

# Function to save subscribers to MongoDB
def save_subscriber(user_id):
    if not subscribers_collection.find_one({"user_id": user_id}):
        subscribers_collection.insert_one({"user_id": user_id})

# Function to get all subscribers from MongoDB
def get_all_subscribers():
    return [doc["user_id"] for doc in subscribers_collection.find()]

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

# Function to send broadcast message
@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client, message):
    # Check if the user is an admin
    if message.from_user.id not in ADMINS:
        await message.reply_text("You are not authorized to use this command.")
        return
    
    # Extract the message to broadcast
    broadcast_text = message.text.split(maxsplit=1)
    
    if len(broadcast_text) < 2:
        await message.reply_text("Please provide a message to broadcast.")
        return
    
    broadcast_text = broadcast_text[1]
    
    # Send the message to all subscribers
    sent_count = 0
    failed_count = 0
    subscribers = get_all_subscribers()
    
    for user_id in subscribers:
        try:
            await client.send_message(chat_id=user_id, text=broadcast_text)
            sent_count += 1
            await asyncio.sleep(1 / 15)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")
            failed_count += 1
    
    await message.reply_text(f"Broadcast complete! Sent: {sent_count}, Failed: {failed_count}")

# Welcome message that should only be sent on `/start`
@app.on_message(filters.command("start") & filters.private)
async def send_welcome(client, message):
    user_id = message.from_user.id
    
    # Add user to the subscribers list if not already present
    save_subscriber(user_id)
    
    # Send the welcome message
    await message.reply_text(
        text="Hi I am owner of the channel this is an automated reply\n\n\Please drop your questions or suggestions/feedback i'll try to reply asap"
    )

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
            text="You left the channel\n\nYou need to join channel to send the message",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    else:
        # Add user to the subscribers list if not already present
        save_subscriber(user_id)

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
                text="Thank you for joining!\nYou can send your question now.."
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
