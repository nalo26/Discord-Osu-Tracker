import discord
from discord.ext import commands
import asyncio
import jsondiff

import utils
import osu

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready() -> None:
    print("Connected as : ")
    print(f"{client.user.name}#{client.user.discriminator}")
    print(client.user.id)
    print("-----------------")
    await client.change_presence(activity=discord.Game(name='osu!'))


@client.command(aliases=['add'])
async def track(ctx, *argv) -> None:
    if not utils.is_admin(ctx.message.author.id):
        await ctx.send(f':lock: Vous devez être administrateur pour faire ceci !')
        return
    
    user, mode, force = "", "", False
    for i, arg in enumerate(argv):
        if len(argv)-1 >= i+1 and '-' not in argv[i+1]:
            if arg in ['-u', '--user']: user = argv[i+1].lower()
            if arg in ['-m', '--mode']: mode = argv[i+1].lower()
            if arg in ['-f', '--force']: force = bool(argv[i+1].lower() == 'true')

    if user == "":
        await ctx.send(":x: Veuillez préciser un joueur ! (`-u <joueur>`)")
        return
    if mode == "":
        await ctx.send(":x: Veuillez préciser un mode de jeu ! (`-m <mode>`)")
        return
    if mode not in utils.MODES_IND:
        await ctx.send(f":x: Le mode de jeu `{mode}` n'existe pas !")
        return
    if not osu.check_user_exists(user, mode):
        await ctx.send(f":x: Le joueur `{user}` n'existe pas !")
        return
    player = osu.get_player_info(user, mode)
    if utils.already_tracked(player['user_id'], mode):
        await ctx.send(f":clipboard: Le joueur `{user}` est déjà dans la tracklist `{mode}` !")
        return

    channel = ctx.channel
    if force:
        channel = await ctx.guild.create_text_channel(name=user.replace(' ', '_'), category=getCategorie(ctx, mode))
        await ctx.send(f">>> <#{str(channel.id)}> <<<")
    utils.add_user(player, mode, channel.id)
    await channel.send(f":white_check_mark: Le joueur [`{mode.upper()}`] `{user}` a bien été ajouté à la tracklist !")

@client.command(aliases=['del'])
async def trackdel(ctx, *argv) -> None:
    if not utils.is_admin(ctx.message.author.id):
        await ctx.send(f':lock: Vous devez être administrateur pour faire ceci !')
        return

    user, mode, force = "", "", False
    for i, arg in enumerate(argv):
        if len(argv)-1 >= i+1 and '-' not in argv[i+1]:
            if arg in ['-u', '--user']: user = argv[i+1].lower()
            if arg in ['-m', '--mode']: mode = argv[i+1].lower()
            if arg in ['-f', '--force']: force = bool(argv[i+1].lower() == 'true')
    
    if user == "": user = ctx.name
    if mode == "": mode = ctx.category.name[9:].lower()
    if mode not in utils.MODES_IND and mode != "quaver":
        await ctx.send(f":x: Le mode `{mode}` n'existe pas ! ({utils.MODES_IND})")
        return
    if not osu.check_user_exists(user, mode):
        await ctx.send(f":x: Le joueur `{user}` n'existe pas !")
        return
    player = osu.get_player_info(user, mode)
    if force: client.get_channel(utils.get_user(player['user_id'], mode)['channel']).delete(f"Deleted user '{user}'.")
    utils.delete_user(player['user_id'], mode)
    await ctx.send(f":white_check_mark: Le joueur [`{mode.upper()}`] `{user}` a bien été supprimé !")

@client.command(aliases=['list'])
async def tracklist(ctx, *, mode:str = "") -> None:
    if mode == "": mode = ctx.category.name[9:]
    mode = mode.lower()
    if mode not in utils.MODES_IND:
        await ctx.send(f":x: Le mode `{mode}` n'existe pas ! ({utils.MODES_IND})")
        return
    data = utils.read_json('PLAYERS.json')
    tracked = ""
    for player in data[mode]:
        tracked += f"{data[mode][player]['name']} (#{data[mode][player]['rank']})\n"
    await ctx.send(f"Voici la liste des joueurs de la tracklist [`{mode.upper()}`] : ```{tracked}```")

@client.command(aliases=['u', 'user', 'profil'])
async def profile(ctx, *argv) -> None:
    if not isinstance(ctx, discord.TextChannel): ctx = ctx.channel
    user, mode, silent = "", "", False
    for i, arg in enumerate(argv):
        if len(argv)-1 >= i+1 and '-' not in argv[i+1]:
            if arg in ['-u', '--user']: user = argv[i+1].lower()
            if arg in ['-m', '--mode']: mode = argv[i+1].lower()
            if arg in ['-s', '--silent']: silent = get_bool(argv[i+1])

    if user == "":
        if ctx.category.name.lower() != "général": user = ctx.name
        elif not silent: await ctx.send(":x: Veuillez préciser un joueur !")
    if mode == "":
        if ctx.category.name.lower() != "général": mode = ctx.category.name[9:].lower()
        elif not silent: await ctx.send(":x: Veuillez préciser un mode de jeu !")
    if mode not in utils.MODES_IND and mode != "quaver":
        if not silent: await ctx.send(f":x: Le mode `{mode}` n'existe pas ! (`{'` / `'.join(utils.MODES_IND)}`)")
        return
    if not osu.check_user_exists(user, mode):
        if not silent: await ctx.send(f":x: Le joueur `{user}` n'existe pas !")
        return
    player = osu.get_player_info(user, mode)
    await ctx.send(embed = osu.embed_user_info(player, mode))

@client.command(aliases=['map', 'btmp'])
async def beatmap(ctx, *argv) -> None:
    if not isinstance(ctx, discord.TextChannel): ctx = ctx.channel
    btmp, mode, silent = "", "", False
    for i, arg in enumerate(argv):
        if len(argv)-1 >= i+1 and '-' not in argv[i+1]:
            if arg in ['-b', '--map', '--beatmap']: btmp = argv[i+1].lower()
            if arg in ['-m', '--mode']: mode = argv[i+1].lower()
            if arg in ['-s', '--silent']: silent = get_bool(argv[i+1])

    if mode == "":
        if ctx.category.name.lower() != "général": mode = ctx.category.name[9:].lower()
        elif not silent: await ctx.send(":x: Veuillez préciser un mode de jeu !")
    if mode not in utils.MODES_IND and mode != "quaver":
        mode = "quaver" if "quavergame" in btmp else ""
        if mode == "":
            if not silent: await ctx.send(f":x: Le mode `{mode}` n'existe pas ! (`{'` / `'.join(utils.MODES_IND)}`)")
            return
    if not osu.check_map_exists(btmp, mode):
        if not silent: await ctx.send(f":x: La map `{btmp}` n'existe pas !")
        return
    btmp = osu.get_map(btmp, mode)
    await ctx.send(embed = osu.embed_map_info(btmp, mode))
    
@client.command(aliases=['mapset', 'set'])
async def beatmapset(ctx, *argv) -> None:
    if not isinstance(ctx, discord.TextChannel): ctx = ctx.channel
    mapset, mode, silent = "", "", False
    for i, arg in enumerate(argv):
        if len(argv)-1 >= i+1 and '-' not in argv[i+1]:
            if arg in ['-b', '--set', '--mapset']: mapset = argv[i+1].lower()
            if arg in ['-m', '--mode']: mode = argv[i+1].lower()
            if arg in ['-s', '--silent']: silent = get_bool(argv[i+1])

    if mode == "":
        if ctx.category.name.lower() != "général": mode = ctx.category.name[9:].lower()
        elif not silent: await ctx.send(":x: Veuillez préciser un mode de jeu !")
    if mode not in utils.MODES_IND and mode != "quaver":
        mode = "quaver" if "quavergame" in mapset else ""
    if not osu.check_mapset_exists(mapset, mode):
        if not silent: await ctx.send(f":x: Le mapset `{mapset}` n'existe pas !")
        return
    mapset = osu.get_mapset(mapset, mode)
    await ctx.send(embed = osu.embed_mapset_info(mapset, mode))

@client.command(aliases=['stat'])
async def stats(ctx) -> None:
    a = ""
    # a += f"▸ Nombre de joueurs standard : `{str(vari.stats['tracked_user_std'])}`\n"
    # a += f"▸ Nombre de joueurs mania : `{str(vari.stats['tracked_user_mania'])}`\n"
    # a += f"▸ Nombre de joueurs catch : `{str(vari.stats['tracked_user_ctb'])}`\n"
    # a += f"▸ Nombre de joueurs taiko : `{str(vari.stats['tracked_user_taiko'])}`\n"
    # a += f"▸ Nombre de joueurs total : `{str(vari.stats['tracked_user'])}`\n"
    # a += f"▸ Nombre de scores affichés : `{str(vari.stats['displayed_play'])}`\n"
    # a += f"▸ Nombre de commandes effectuées : `{str(vari.stats['invoked_commands'])}`\n"
    # a += f"▸ Nombre de redémarrages : `{str(vari.stats['boot'])}`\n"
    # a += f"▸ Nombre de requêtes osu : `{str(vari.stats['api_usage'])}`"
    await ctx.send(a)

@client.command()
async def game(ctx, *, game) -> None:
    if not utils.is_admin(ctx.message.author.id):
        await ctx.send(f':lock: Vous devez être administrateur pour faire ceci !')
        return
    await client.change_presence(activity=discord.Game(name=game))

@client.command(aliases=['addadmin', 'setadmin'])
async def admin(ctx, *, user_id) -> None:
    if not utils.is_admin(ctx.message.author.id): 
        await ctx.send(f':lock: Vous devez être administrateur pour faire ceci !')
        return
    utils.add_admin(user_id)


@client.event
async def on_message(message) -> None:
    text = message.content

    if message.author.id == client.user.id: return
    if text.startswith('!!'): return

    await client.process_commands(message)

    if "osu.ppy.sh" in text and not text.startswith("!"):
        splited = text.split('/')

        if "osu.ppy.sh/u" in text: # user
            if "http" in text:
                user = splited[4]
                mode = splited[5] if len(splited) > 5 else 'std'
            else:
                user = splited[2]
                mode = splited[3] if len(splited) > 3 else 'std'
            if mode == 'osu': mode = 'std'
            if mode == 'fruits': mode = 'ctb'
            await profile(message.channel, "-u", str(user), "-m", str(mode), "-s", "true")
            return
        
        if "osu.ppy.sh/b" in text: # beatmap
            btmp = splited[-1]
            mode = ""
            if 'beatmapsets' in text:
                mode = splited[-2].split("#")[1]
                if mode == 'osu': mode = 'std'
                if mode == 'fruits': mode = 'ctb'
            await beatmap(message.channel, "-b", str(btmp), "-m", str(mode), "-s", "true")
            return
        
        if "osu.ppy.sh/beatmapsets" in text: # beatmapset
            mapset = splited[4] if "http" in text else splited[2]
            if "#" in mapset: mapset = mapset.split('#')[0]
            await beatmapset(message.channel, "-b", str(mapset), "-s", "true")
            return


def getCategorie(ctx, mode) -> discord.CategoryChannel:
    for cat in ctx.guild.categories:
        if cat.name.lower() == mode.lower(): return cat
    return None

def get_bool(string) -> bool:
    return (string.lower() in ["true", "yes", "t", "1"])

async def track_plays() -> None:
    await client.wait_until_ready()
    i = 0
    while True:
        data = utils.read_json('PLAYERS.json')
        for mode in data:
            for player in data[mode]:
                channel = client.get_channel(data[mode][player]['channel'])
                old_plays = data[mode][player]['plays']
                new_plays = osu.get_user_best(player, mode)
                if old_plays == new_plays: break # no new top play
                dif = jsondiff.diff(old_plays, new_plays)
                if jsondiff.insert not in dif: break
                play = dif[jsondiff.insert][0]
                user = osu.get_player_info(player, mode)
                await channel.send(embed = osu.embed_play(play[1], play[0]+1, mode, data[mode][player], user))
                data[mode][player]['plays'] = new_plays
                data[mode][player]['rank']  = int(user['pp_rank'])
                data[mode][player]['pp']    = float(user['pp_raw'])
                data[mode][player]['acc']   = float(user['accuracy'])
        utils.write_json('PLAYERS.json', data)

        i += 1
        if i % 60 == 0: utils.update_players() # update all players every 30 minutes
        await asyncio.sleep(30) # update all plays every 30 seconds


client.loop.create_task(track_plays())
client.run(utils.read_txt('TOKEN'))