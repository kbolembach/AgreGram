# AgreGram (WIP)
___
## Overview
AgreGram is a Telegram userbot used to aggregate posts and media from channels 
you subscribe to and post them in your dedicated feed channel, without
repeating media. 

AgreGram is based on [Pyrogram](https://pyrogram.org/), a Python framework 
enabling the creation of custom Telegram clients - or userbots. This is 
necessary, because  regular Telegram bots aren't fit for fetching posts from
channels you don't own. This also effectively means that the bot runs on your
personal account.

You can specify the channel where you want your feed to be posted, and your
subscribed channels can be taken from a specific folder or specified manually
in the `data.json`.
___
## Setup
To use AgreGram, you need to 
[install the Pyrogram library](https://docs.pyrogram.org/intro/install) and 
[obtain your Telegram API id](https://core.telegram.org/api/obtaining_api_id).
Now, you're ready to [generate your personal `my_account.session`](https://docs.pyrogram.org/start/auth)
file with which AgreGram will be able to access your Telegram account. Never 
share your Telegram API data and the `my_account.session` file with anyone.

Download the script from this GitHub page and include the `my_account.session`
file in the folder along with `main.py`. Configure the `data.json` file:
- `target_channel` refers to the name of your private channel, where you
want your feed posted to,
- `target_folder` is the name of the folder with your subscribed channels;
- alternatively, you can specify names of the subscribed channels in 
`manual_subscribed_dialogs`.

Run the script, preferably on a trusted server.