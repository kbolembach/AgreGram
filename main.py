from pyrogram import filters, idle, Client
from pyrogram.raw import functions

app = Client("my_account")
target_channel = "jekoagregram"
subscribed_dialogs = []


async def main():
    async with app:
        dialogs = await app.invoke(
            functions.messages.GetDialogFilters()
        )
        dialogs = [d for d in dialogs if hasattr(d, "title")]
        dialogs_folder = [d for d in dialogs if d.title == "Memes"][0]
        global subscribed_dialogs
        subscribed_dialogs = [int("-100" + str(d.channel_id)) for d in dialogs_folder.include_peers]

        @app.on_message(filters.chat(subscribed_dialogs))
        async def fetch_feed(client, message):
            await message.forward(target_channel)

        await idle()


app.run(main())
