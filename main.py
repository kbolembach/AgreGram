from pyrogram import filters, idle, Client, enums
from pyrogram.raw import functions
import json

DEBUG = True
app = Client("my_account")
unique_ids_messages = {}
recent_message_id = 0


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

    # TODO: not every channel has a username - do as above
    if message.forward_from_chat is not None:
        caption += "\nForwarded from [{title}](t.me/{link})".format(title=message.forward_from_chat.title,
                                                                    link=message.forward_from_chat.username)
    if DEBUG:
        print(caption)
    return caption


async def main():
    async with app:
        global unique_ids_messages, recent_message_id
        json_file = open("data.json").read()
        json_contents = json.loads(json_file)
        target_channel = json_contents["target_channel"]
        subscribed_dialogs = json_contents["manual_subscribed_dialogs"]
        media_group_ids = []
        unique_ids_file = open("unique_ids.txt").read()

        @app.on_message(filters.outgoing, group=1)
        async def update_recent_id(client, message):
            global recent_message_id
            print("\noutgoing")
            # print(message)
            if message.chat.username != target_channel:
                return
            recent_message_id = message.id
            print(("Yippie!", recent_message_id, message.id))
            print('\n')

        # await app.send_message(target_channel, "Bot started.")

        if DEBUG:
            print(unique_ids_file)
        if unique_ids_file != "":
            unique_ids_messages = dict([s.split(' ') for s in unique_ids_file.split('\n')])
        if DEBUG:
            print(unique_ids_messages)

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

        if DEBUG:
            print(json_contents)
            print("Target channel: {target}".format(target=target_channel))
            print("Number of subscribed dialogs: {count}".format(count=len(subscribed_dialogs)))

        @app.on_message(filters.chat(subscribed_dialogs))
        async def fetch_feed(client, message):
            global unique_ids_messages, recent_message_id
            if message.media_group_id is not None:
                if message.media_group_id not in media_group_ids:
                    if DEBUG:
                        print(message)
                        print("\n")
                    media_group_ids.append(message.media_group_id)
                    caption = format_message(message)
                    await app.copy_media_group(target_channel, message.sender_chat.id, message.id, caption)
            else:
                unique_id = None
                if message.photo is not None:
                    unique_id = message.photo.file_unique_id
                if message.video is not None:
                    unique_id = message.video.file_unique_id
                if message.animation is not None:
                    unique_id = message.animation.file_unique_id
                if unique_id in unique_ids_messages:
                    print(message)
                    print("Media already in message with id {id}".format(id=unique_ids_messages[unique_id]))

                    return # TODO: edit existing message
                if unique_id is not None:
                    unique_ids_messages[unique_id] = recent_message_id + 1

                    # if len(unique_ids) > 2 * 20000:
                    #     unique_ids = unique_ids[0:(20000 - 1)]
                    #     message_ids = message_ids[0:(20000 - 1)]

                caption = format_message(message)

                # TODO: get these manually or via json
                message.chat.id = -1002088236455
                message.chat.title = "Jeko's Aggregate"
                message.chat.username = "jekoagregram"

                if DEBUG:
                    print(message)
                    print("\n")
                    print(caption)
                    print("\n")

                if message.media == enums.MessageMediaType.STICKER:
                    print("sticker!")
                    await app.forward_messages(target_channel, message.sender_chat.id, message.id)
                elif message.media is not None and message.media != enums.MessageMediaType.WEB_PAGE:
                    print("media!")
                    await app.copy_message(target_channel, message.sender_chat.id, message.id, caption)
                else:
                    print("no media or web page!")
                    await app.send_message(target_channel, caption)

        await idle()
        await app.stop()

        f_ids = open("unique_ids.txt", "w")
        contents = [str(uid) + " " + str(mid) for uid, mid in zip(unique_ids_messages.keys(), unique_ids_messages.values())]
        f_ids.write('\n'.join(contents))
        f_ids.close()

app.run(main())
