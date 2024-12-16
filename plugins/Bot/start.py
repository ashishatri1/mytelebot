from telethon import events, Button

from bot import app


@app.on(events.NewMessage(pattern="^/start", func=lambda e: e.is_private))
@app.on(events.CallbackQuery(pattern=r"home"))
async def start(event):
    message = """Hello {user} 👋,
I am an {me} 🤖. I can give reactions to posts in your channel! 🎉

To learn how to use me or how to set me up, click the button below for my usage instructions 📜👇.
    """
    sender = await event.get_sender()
    me = await event.client.get_me()
    user_name = f"{sender.first_name} {sender.last_name or ''}".strip()
    me_mention = f"[{me.first_name}](tg://user?id={me.id})"
    mention = f"[{user_name}](tg://user?id={sender.id})"
    button = [[Button.inline("How to set me up! 💛", data=b"setup")]]

    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(message.format(user=mention, me=me_mention), buttons=button)
    elif isinstance(event, events.NewMessage.Event):
        await event.respond(message.format(user=mention, me=me_mention), buttons=button)


@app.on(events.CallbackQuery(pattern=r"setup"))
async def setup(event):
    txt = "Below are some bots. Add these to your channel [make sure to promote them as admins but without any rights. If you don't promote them, they will still work]:\n"
    for client in app.clients:
        txt += f"@{(await client.get_me()).username}\n"
    button = [[Button.inline("Back", data=b"home")]]
    await event.edit(txt, buttons=button)

