import discord
import requests as rq

import utils

EMOJIS = utils.read_json('EMOJIS.json')
ICON_URL = 'https://camo.githubusercontent.com/119186f8d09fc5593175ae82130cea0516520656/68747470733a2f2f692e696d6775722e636f6d2f554b3350574a572e706e67'
BASE_URL = 'https://api.quavergame.com/v1'
MODES = ['4K', '7K']

def check_user_exists(user) -> bool:
    return (len(get_player_info(user)) > 1)

def check_map_exists(map_id) -> bool:
    return (len(get_map(map_id)) > 1)

def check_mapset_exists(mapset_id) -> bool:
    return (len(get_mapset(mapset_id)) > 1)

def get_player_info(user) -> dict:
    try: 
        info = rq.get(f"{BASE_URL}/users/full/{user}").json()['user']
        ret = {}
        ret['user_id'] = info['info']['id']
        ret['username'] = info['info']['username']
        ret['country'] = info['info']['country']
        ret['avatar'] = info['info']['avatar_url']
        ret['join_date'] = info['info']['time_registered']
        ret['pp_rank'] = info['keys4']['globalRank']
        ret['pp_country_rank'] = info['keys4']['countryRank']
        ret['ranked_score'] = info['keys4']['stats']['ranked_score']
        ret['pp_raw'] = info['keys4']['stats']['overall_performance_rating']
        ret['accuracy'] = info['keys4']['stats']['overall_accuracy']
        ret['playcount'] = info['keys4']['stats']['play_count']
        ret['failcount'] = info['keys4']['stats']['fail_count']
        ret['multi_w'] = info['keys4']['stats']['multiplayer_wins']
        ret['multi_l'] = info['keys4']['stats']['multiplayer_losses']
        ret['multi_t'] = info['keys4']['stats']['multiplayer_ties']
        ret['badges'] = [badge['name'] for badge in info['profile_badges']]
        return ret
    except KeyError: return {}

def get_user_best(user_id, limit=50) -> list:
    try: return rq.get(f"{BASE_URL}/users/scores/best?id={user_id}&mode=1&limit={str(limit)}").json()['scores']
    except KeyError: return []

def get_map(map_id) -> dict:
    try: return rq.get(f"{BASE_URL}/maps/{map_id}").json()['map']
    except KeyError: return {}

def get_mapset(mapset_id) -> dict:
    try: return rq.get(f"{BASE_URL}/mapsets/{mapset_id}").json()['mapset']
    except KeyError: return {}

def get_avatar(user) -> str:
    return get_player_info(user)['avatar']

def embed_play(play, top, old_user, new_user) -> discord.Embed:
    beatmap = get_map(play['map']['id'])

    rank_change = "{0:+d}".format(old_user['rank'] - int(new_user['pp_rank']))
    acc_change  = "{0:+0.2f}%".format(float(new_user['accuracy']) - old_user['acc'])
    pp_change   = "{0:+0.1f}".format(float(new_user['pp_raw']) - old_user['pp'])

    hits = compute_hits((play['count_miss'], play['count_okay'], play['count_good'], play['count_great'], play['count_perf'], play['count_marv']))
    score = "{:,}".format(int(play['total_score'])).replace(',', "'")
    maxcombo = compute_max_combo(beatmap)
    max_pp = pp(beatmap['difficulty_rating'], 100)

    embed = discord.Embed(title=f"{beatmap['title']} [{beatmap['difficulty_name']}]", url=f"https://quavergame.com/mapset/map/{beatmap['id']}")
    if top != -1: title = f"[Quaver] {new_user['username']} - Top play #{top}"
    else: title = f"[Quaver] {new_user['username']} - Recent play"
    embed.set_author(name=f"{title} ({rank_change})", icon_url=get_avatar(new_user['username']))
    embed.set_thumbnail(url=f"https://quaver.blob.core.windows.net/banners/{beatmap['mapset_id']}_banner.jpg")
    c = utils.avg_color(f"https://quaver.blob.core.windows.net/banners/{beatmap['mapset_id']}_banner.jpg")
    embed.colour = discord.Colour(0).from_rgb(c[0], c[1], c[2])

    embed.add_field(name="Score", value=score)
    embed.add_field(name="PP", value=f"{round(float(play['performance_rating']), 2)}/{max_pp}\n({pp_change})")
    embed.add_field(name="Rank", value=EMOJIS["q_"+play['grade'].lower()])
    embed.add_field(name="Accuracy", value=f"{round(play['accuracy'], 2)} % ({acc_change})")
    embed.add_field(name="Combo", value=f"x{play['max_combo']}/x{maxcombo}")
    embed.add_field(name="Mods", value=play['mods_string'])
    embed.add_field(name="Difficulty", value=f"{round(float(beatmap['difficulty_rating']), 2)}☆")
    embed.add_field(name="Hits", value=hits)
    embed.add_field(name='Map info', value=compute_map_info(beatmap), inline=False)

    embed.set_footer(text="Score obtenu le/à", icon_url=ICON_URL)
    embed.timestamp = utils.compute_time(play['time'])

    return embed

def embed_user_info(user) -> discord.Embed:
    embed = discord.Embed()

    wwr = "{:,}".format(user['pp_rank']).replace(",", "'")
    cr  = "{:,}".format(user['pp_country_rank']).replace(",", "'")
    embed.set_author(name = f"[Quaver] {user['username']} #{wwr} (#{cr} {utils.flag(user['country'])})", \
                     url = f"https://quavergame.com/user/{str(user['user_id'])}", icon_url = user['avatar'])
    embed.set_thumbnail(url = user['avatar'])
    c = utils.avg_color(user['avatar'])
    embed.colour = discord.Colour(0).from_rgb(c[0], c[1], c[2])

    rs  = "{:,}".format(user['ranked_score']).replace(",", "'")
    pr  = "{:,}".format(round(user['pp_raw'], 2)).replace(",", "'")
    embed.add_field(name = "Ranked Score", value = rs)
    embed.add_field(name = "Performance Rating", value = pr)
    embed.add_field(name = "Accuracy", value = f"{round(float(user['accuracy']), 2)}%")
    embed.add_field(name = "Play Count", value = user['playcount'])
    embed.add_field(name = "Win Rate", value = f"{win_value(user)}%")
    embed.add_field(name = "Mutliplayer", value = f"{user['multi_w']}W - {user['multi_l']}L - {user['multi_t']}T")

    if len(user['badges']) > 0: embed.add_field(name = "Badges", value = '\\> ' + '\n\\> '.join(user['badges']), inline=False)

    embed.add_field(name = "Top Plays", value = compute_tops(get_user_best(user['user_id'], 5)))

    embed.set_footer(text="Ici depuis", icon_url=ICON_URL)
    embed.timestamp = utils.compute_time(user['join_date'])

    return embed

def embed_map_info(beatmap) -> discord.Embed:
    embed = discord.Embed(title = f"{beatmap['artist']} - {beatmap['title']} [{beatmap['difficulty_name']}]", \
                          url = f"https://quavergame.com/mapset/map/{beatmap['id']}")
    embed.set_author(name = f"Créée par {beatmap['creator_username']}", url = f"https://quavergame.com/user/{str(beatmap['creator_id'])}", \
                     icon_url = get_avatar(beatmap['creator_id']))
    embed.set_thumbnail(url = f"https://quaver.blob.core.windows.net/banners/{beatmap['mapset_id']}_banner.jpg")
    c = utils.avg_color(f"https://quaver.blob.core.windows.net/banners/{beatmap['mapset_id']}_banner.jpg")
    embed.colour = discord.Colour(0).from_rgb(c[0], c[1], c[2])

    dif = beatmap['difficulty_rating']
    desc = compute_map_info(beatmap) + "\n\n"
    desc += f"95%: `{pp(dif, 95)}pr` 97%: `{pp(dif, 97)}pr` 99%: `{pp(dif, 99)}pr` 100%: `{pp(dif, 100)}pr`"

    embed.description = desc
    embed.set_footer(text = "Mise à jour le/à", icon_url = ICON_URL)
    embed.timestamp = utils.compute_time(beatmap['date_last_updated'])

    return embed

def embed_mapset_info(mapset) -> discord.Embed:
    embed = discord.Embed(title = f"{mapset['artist']} - {mapset['title']}")
    embed.set_author(name = f"Créé par {mapset['creator_username']}", url = f"https://quavergame.com/user/{str(mapset['creator_id'])}", \
                     icon_url = mapset['creator_avatar_url'])
    embed.set_thumbnail(url = f"https://quaver.blob.core.windows.net/banners/{mapset['id']}_banner.jpg")
    c = utils.avg_color(f"https://quaver.blob.core.windows.net/banners/{mapset['id']}_banner.jpg")
    embed.colour = discord.Colour(0).from_rgb(c[0], c[1], c[2])

    desc = ""
    for i, beatmap in enumerate(mapset['maps']):
        dif = beatmap['difficulty_rating']
        to_add = f"\\> [{MODES[beatmap['game_mode']-1]}] **{round(dif, 2)}**☆ - {beatmap['difficulty_name']} ({pp(dif, 100)}pr)\n"
        if len(desc) + len(to_add) <= 2048: desc += to_add
        else:
            amout = len(mapset['maps']) - i
            desc += f"\\> *...{amout} autre{'s' if amout > 1 else ''}...*"
            break

    embed.description = desc
    embed.set_footer(text = "Mise à jour le/à", icon_url = ICON_URL)
    embed.timestamp = utils.compute_time(mapset['date_last_updated'])

    return embed

def compute_map_info(beatmap) -> str:
    maxcombo = compute_max_combo(beatmap)
    info = ""
    info += f"Créateur : `{beatmap['creator_username']}` ID : `{beatmap['id']}`\n"
    info += f"Durée: `{compute_length(beatmap['length'])}` BPM: `{beatmap['bpm']}` Combo: `{maxcombo}`\n"
    info += f"LNs: `{ln_value(beatmap)}%` Difficulty: `{round(float(beatmap['difficulty_rating']), 2)}☆`\n"
    info += f"Status: `{beatmap['ranked_status']}` Taux de réussite: `{pass_value(beatmap)}%`"

    return info

def compute_hits(hits) -> str:
    miss, okay, good, great, perf, marv = hits
    return f"{EMOJIS['q_marv']} x{marv} / {EMOJIS['q_perf']} x{perf}\n" + \
           f"{EMOJIS['q_great']} x{great} / {EMOJIS['q_good']} x{good}\n" + \
           f"{EMOJIS['q_okay']} x{okay} / {EMOJIS['q_miss']} x{miss}"

def compute_max_combo(beatmap):
    return beatmap['count_hitobject_normal'] + (beatmap['count_hitobject_long'] * 2)

def compute_tops(plays) -> str:
    ret = ""
    for play in plays:
        beatmap = get_map(play['map']['id'])
        ret += f"\\> **{round(play['performance_rating'], 2)}pr** {EMOJIS['q_'+play['grade'].lower()]} {beatmap['title']} " + \
               f"({round(beatmap['difficulty_rating'], 2)}☆) {round(play['accuracy'], 2)}%"
        ret += f" ({play['mods_string']})\n" if play['mods_string'] != "None" else "\n"
    return ret

def compute_length(ms) -> str:
    m, s = divmod(ms/1000, 60)
    return f"{int(m)}:{round(s)}"

def ln_value(beatmap) -> float:
    if beatmap['count_hitobject_normal'] == 0: return 0
    return round(100*(beatmap['count_hitobject_long'] / beatmap['count_hitobject_normal']), 1)

def pass_value(beatmap) -> float:
    play = beatmap['play_count']
    fail = beatmap['fail_count']
    win  = play - fail
    if play == 0: return 0
    return round(float(win / play * 100), 1)

def win_value(user) -> float:
    if user['playcount'] == 0: return 0
    return round((user['playcount'] - user['failcount']) / user['playcount'] * 100, 2)

def pp(diff, acc) -> float:
    return round(diff * pow(acc / 98, 6), 2)