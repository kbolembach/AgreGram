from pyrogram import filters, idle, Client
from pyrogram.raw import functions
import json

app = Client("my_account")


async def main():
    async with app:
        json_file = open("data.json").read()
        json_contents = json.loads(json_file)
        print(json_contents)
        target_channel = json_contents["target_channel"]
        subscribed_dialogs = json_contents["manual_subscribed_dialogs"]

        print("Target channel: {target}".format(target=target_channel))

        if not subscribed_dialogs:
            dialogs = await app.invoke(
                functions.messages.GetDialogFilters()
            )
            dialogs = [d for d in dialogs if hasattr(d, "title")]
            dialogs_folder = [d for d in dialogs if d.title == json_contents["target_folder"]][0]
            included_peers = dialogs_folder.include_peers + dialogs_folder.pinned_peers
            subscribed_dialogs = [int("-100" + str(d.channel_id)) for d in included_peers]
        else:
            print("Target folder: {folder}".format(foler=json_contents["target_folder"]))

        print("Number of subscribed dialogs: {count}".format(count=len(subscribed_dialogs)))

        @app.on_message(filters.chat(subscribed_dialogs) & ~filters.media_group)
        async def fetch_feed(client, message):
            caption = ""
            print(message.caption)
            if message.caption is not None:
                caption += message.caption + "\n\n"

            caption += "From [{title}](t.me/{link})".format(caption=message.caption,
                                                            title=message.sender_chat.title,
                                                            link=message.sender_chat.username)
            if hasattr(message, "forward_from_chat"):
                caption += "\nForwarded from [{title}](t.me/{link})".format(title=message.forward_from_chat.title,
                                                                            link=message.forward_from_chat.username)

            await app.copy_message(target_channel, message.sender_chat.id, message.id, caption)
            print(message)

        await idle()


app.run(main())
