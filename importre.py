import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Regular expression pattern to match valid channel/user IDs
id_pattern = re.compile(r'^.\d+$')

# List of authorized channels for force subscription
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in ['-1002214768044']]

# Initialize the bot with your credentials
API_TOKEN = "7018358870:AAFonX8JYsTf5PzK1o0lvFb8Qoyo5lxWsi8"  # Replace with your actual Bot Token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def is_subscribed(user_id, channels):
    btn = []
    for channel in channels:
        try:
            # Check if the user is a member of the channel
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                chat = await bot.get_chat(channel)
                btn.append([InlineKeyboardButton(f'My Channel', url=chat.invite_link)])
        except ChatNotFound:
            continue
        except Exception as e:
            print(f"Error: {e}")
            pass
    return btn

@dp.message_handler(lambda message: message.chat.type == 'private')  # Handles all private messages
async def check_subscription(message: types.Message):
    # Force subscribe logic
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(message.from_user.id, AUTH_CHANNEL)
            if btn:
                username = (await bot.me).username
                btn.append([InlineKeyboardButton("I joined it!", url=f"https://t.me/{username}?start=true")])
                await message.answer(
                    text="HHuh-? you left my channel... :(\n\nYou need to join it to text here !",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            print(e)
            return

    # If subscribed, respond normally (or handle other logic here)
    await message.answer(
        text="Hi minerva this side.. I'll reply soon.. thank you for joining ✨\n\nPlease drop your questions or suggestions/feedback in the meantime\n\nThank you for waiting ✨"
    )

if __name__ == '__main__':
    # Start polling to receive updates
    executor.start_polling(dp, skip_updates=True)
