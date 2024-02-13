import json

from pyrogram import filters, idle, Client, enums
from pyrogram.raw import functions

DEBUG = False
app = Client("my_account")
unique_ids = []


def format_message(message):
    if message is None:
        return ""
    caption = ""
    if message.caption is not None:
        caption += message.caption + "\n\n"

    if message.text is not None:
        caption += message.text + "\n\n"

    if message.sender_chat.username is not None:
        caption += "From [{title}](t.me/{link})".format(title=message.sender_chat.title,
                                                        link=message.sender_chat.username)
    else:
        caption += "From {title}".format(title=message.sender_chat.title)

    if message.forward_from_chat is None:
        if DEBUG:
            print(caption)
        return caption

    if message.forward_from_chat.link is not None:
        caption += "\nForwarded from [{title}](t.me/{link})".format(title=message.forward_from_chat.title,
                                                                    link=message.forward_from_chat.username)
    else:
        caption += "\nForwarded from title".format(title=message.forward_from_chat.title)

    if DEBUG:
        print(caption)
    return caption


def get_unique_id(message):
    unique_id = None
    if message.photo is not None:
        unique_id = message.photo.file_unique_id
    if message.video is not None:
        unique_id = message.video.file_unique_id
    if message.animation is not None:
        unique_id = message.animation.file_unique_id
    return unique_id


async def main():
    async with app:
        global unique_ids
        json_file = open("data.json").read()
        json_contents = json.loads(json_file)
        target_channel = json_contents["target_channel"]
        subscribed_dialogs = json_contents["manual_subscribed_dialogs"]
        media_group_ids = []
        unique_ids_file = open("unique_ids.txt").read()

        if DEBUG:
            print(unique_ids_file)
        if unique_ids_file != "":
            unique_ids = unique_ids_file.split('\n')
        if DEBUG:
            print(unique_ids)

        @app.on_message(filters.me, group=1)
        async def update_recent_id(client, message):
            global unique_ids
            if message.chat.username != target_channel:
                return
            unique_id = get_unique_id(message)
            if unique_id is not None:
                unique_ids = [unique_id] + unique_ids

        if not subscribed_dialogs:
            dialogs = await app.invoke(
                functions.messages.GetDialogFilters()
            )
            dialogs = [d for d in dialogs if hasattr(d, "title")]
            dialogs_folder = [d for d in dialogs if d.title == json_contents["target_folder"]][0]
            included_peers = dialogs_folder.include_peers + dialogs_folder.pinned_peers
            subscribed_dialogs = [int("-100" + str(d.channel_id)) for d in included_peers]
        elif DEBUG:
            print("Target folder: {folder}".format(folder=json_contents["target_folder"]))

        async for dialog in app.get_dialogs():
            if dialog.chat.username == target_channel:
                target_channel_title = dialog.chat.title
                target_channel_id = dialog.chat.id

        if DEBUG:
            print(json_contents)
            print("Target channel: {target}, {title}, {id}".format(target=target_channel, title=target_channel_title,
                                                                   id=target_channel_id))
            print("Number of subscribed dialogs: {count}".format(count=len(subscribed_dialogs)))

        @app.on_message(filters.chat(subscribed_dialogs))
        async def fetch_feed(client, message):
            global unique_ids

            message.chat.id = target_channel_id
            message.chat.title = target_channel_title
            message.chat.username = target_channel

            if message.media_group_id is not None:
                if message.media_group_id not in media_group_ids:
                    if DEBUG:
                        print(message)
                        print("\n")
                    media_group_ids.append(message.media_group_id)
                    caption = format_message(message)
                    await app.copy_media_group(target_channel, message.sender_chat.id, message.id, caption)
            else:
                unique_id = get_unique_id(message)
                if unique_id in unique_ids:
                    if DEBUG:
                        print(message)
                        print("Media already exists.")
                    return

                if len(unique_ids) > 2 * 20000:
                    unique_ids = unique_ids[0:(20000 - 1)]

                caption = format_message(message)

                if DEBUG:
                    print(message)
                    print("\n")
                    print(caption)
                    print("\n")

                if message.media == enums.MessageMediaType.STICKER:
                    await app.forward_messages(target_channel, message.sender_chat.id, message.id)
                elif message.media is not None and message.media != enums.MessageMediaType.WEB_PAGE:
                    await app.copy_message(target_channel, message.sender_chat.id, message.id, caption)
                else:
                    await app.send_message(target_channel, caption)

        await app.send_message(target_channel, "Bot started.")

        await idle()
        await app.stop()

        f_ids = open("unique_ids.txt", "w")
        contents = [str(uid) for uid in unique_ids]
        f_ids.write('\n'.join(contents))
        f_ids.close()

app.run(main())
