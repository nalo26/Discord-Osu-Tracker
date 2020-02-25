# Discord-Osu-Tracker
A simple osu! best play tracker for a discord bot using python.
The bot is in french by default, but you can edit the code to change that.

To setup the bot follow this steps :
- Open `keys.cfg` and past your osu api key
- Open `bot_admin` and past all the discord id of users you want to be able to manage the bot
- Open `main.py` and :
    - Past your osu api key on the first line
    - Change the log channel id on the line 33
    - Past your bot token on last line
- Open `osu.py` and past your osu api key on the first line

To run the bot, you need the following packages :
- Python 3.6 or greater
- discord.py (`pip install discord.py`)
- asyncio (`pip install async`)
- aiohttp (`pip install aiohttp`)
- datetime (`pip install datetime`)
- pytz (`pip install pytz`)
- jsondiff (`pip install jsondiff`)
- requests (`pip install requests`)
- pillow (`pip install pillow`)

The bot has the following commands :
- `!track <player> [gamemode=std] [force=False]`
  - This will track `player` on the current channel if `force` is False.
  - `gamemode` is the osu mode of tracking (`std` (default), `ctb`, `mania`, `taiko`).
  - `force` is to create the channel, then track the player on the created channel.

- `!del <player> [gamemode=std]`
  - This will delete the tracked user `player`.
  - `gamemode` is the osu mode of tracking (`std` (default), `ctb`, `mania`, `taiko`).
  
- `!list [gamemode]`
  - This will list the tracked players of the gamemode `gamemode`.
  - If `gamemode` isn't specify, it will try to see if the discord category of the current channel is a gamemode.
  
- `!user [player] [gamemode] [top=5]`
  - This will print the osu profile of the user `player`.
  - If `player` isn't specify, this will try to take the channel's name as player.
  - If `gamemode` isn't specify, it will try to see if the discord category of the current channel is a gamemode.
  - `top` is the number of best play to print with the profile. Default is 5.
  
- `!pp <url> [mods=NM] [accuracy=100] [combo=FC] [misses=0]`
  - The will show pp of a specific map (gamemode is auto detected)
  - `url` is the map's link.
  - `mods` is the list of mods used for the map. By default, there is no mods. Example : `HDHR`.
  - `combo` is the max combo on the map. By default, the map is considered as FC.
  - `misses` is the number of miss on the map. By default it's 0.
  
- `!force [player/number] [gamemode]`
  - This will force print the best play of `player` in gamemode `gamemode`.
  - If `player` isn't specify, this will try to take the channel's name as player.
  - If `number` instead of `player`, this will print the `number`th play of the channel's name player.
  - If `gamemode` isn't specify, it will try to see if the discord category of the current channel is a gamemode.
  
- `!rs [player] [gamemode]`
  - This will print the last play of `player` in gamemode `gamemode`.
  - If `player` isn't specify, this will try to take the channel's name as player.
  - If `gamemode` isn't specify, it will try to see if the discord category of the current channel is a gamemode.
  
- `!seek <url> [player] [gamemode]`
  - This will print the play of the map with link `url` for player `player` in gamemode `gamemode`, if exists.
  - It's a **local search**, not on the osu website.
  - `url` is the link of the osu beatmap.
  - If `player` isn't specify, this will try to take the channel's name as player.
  - If `gamemode` isn't specify, it will try to see if the discord category of the current channel is a gamemode.
 
- `!stats` will print the stats of the bot.
- `!help` will print the help message.

- Posting a beatmap link will print the map informations.
- Posting a player profile link will print the player information.
