import discord
import requests as rq
from math import log10

import calc as std_pp
import utils

KEY = utils.read_txt('KEY')
EMOJIS = utils.read_json('EMOJIS.json')
ICON_URL = 'https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png'
BASE_URL = "https://osu.ppy/sh/api"

def check_user_exists(user, mode) -> bool:
    return (len(get_player_info(user, mode)) > 1)

def check_map_exists(map_id, mode) -> bool:
    return (len(get_map(map_id, mode)) > 1)

def check_mapset_exists(mapset_id, mode) -> bool:
    return (len(get_mapset(mapset_id, mode)) > 1)

def get_player_info(user, mode) -> dict:
    return rq.get(f"{BASE_URL}/get_user?k={KEY}&m={str(utils.MODES_VAL[mode])}&u={user}").json()[0]

def get_user_best(user, mode) -> list:
    return rq.get(f"{BASE_URL}/get_user_best?k={KEY}&m={str(utils.MODES_VAL[mode])}&u={user}&limit=50").json()

def get_map(map_id, mode) -> dict:
    return rq.get(f"{BASE_URL}/get_beatmaps?k={KEY}&b={map_id}&m={str(utils.MODES_VAL[mode])}").json()[0]

def get_mapset(mapset_id, mode) -> list:
    return rq.get(f"{BASE_URL}/get_beatmaps?k={KEY}&s={mapset_id}{f'&m={utils.MODES_VAL[mode]}' if mode != '' else ''}")

def get_top_play(map_id, mode) -> dict:
    return rq.get(f"{BASE_URL}/get_scores?k={KEY}&b={map_id}&m={str(utils.MODES_VAL[mode])}&limit=1").json()[0]

def embed_play(play, top, mode, old_user, new_user) -> discord.Embed:
    beatmap = get_map(play['beatmap_id'], mode)

    rank_change = "{0:+d}".format(old_user['rank'] - int(new_user['pp_rank']))
    acc_change  = "{0:+0.2f}%".format(float(new_user['accuracy']) - old_user['acc'])
    pp_change   = "{0:+0.1f}".format(float(new_user['pp_raw']) - old_user['pp'])

    hits = compute_hits((play['countmiss'], play['count50'], play['countkatu'], play['count100'], play['countgeki'], play['count300']), mode)
    acc = compute_acc((play['countmiss'], play['count50'], play['countkatu'], play['count100'], play['countgeki'], play['count300']), mode)
    if int(acc) == acc: acc = int(acc)
    score = "{:,}".format(int(play['score'])).replace(',', "'")
    maxcombo = beatmap['max_combo'] if mode == 'std' else get_top_play(play['beatmap_id'], mode)['maxcombo']
    mods, mods_str = compute_mods(int(play['enabled_mods']))
    objects = int(beatmap['count_normal']) + int(beatmap['count_slider']) + int(beatmap['count_spinner'])
    if mode == 'std': max_pp = std_pp.map(f"osu.ppy.sh/b/{beatmap['beatmap_id']}", mods, 100, maxcombo, 0, 0, 0)
    if mode == 'taiko': max_pp = taiko_pp(mods, int(beatmap['difficultyrating']), int(beatmap['diff_overall']), maxcombo, 100, 0)
    if mode == 'ctb': max_pp = ctb_pp(mods, int(beatmap['difficultyrating']), int(beatmap['diff_approach']), maxcombo, maxcombo, 100, 0)
    if mode == 'mania': max_pp = mania_pp(mods, int(beatmap['difficultyrating']), int(beatmap['diff_overall']), 1000000, objects)

    embed = discord.Embed(title=f"{beatmap['title']} [{beatmap['version']}]", url=f"https://osu.ppy.sh/b/{beatmap['beatmap_id']}")
    if top != -1: title = f"[{mode.upper()}] {new_user['username']} - Top play #{top}"
    else: title = f"[{mode.upper()}] {new_user['username']} - Recent play"
    embed.set_author(name=f"{title} ({rank_change})", icon_url=f"http://s.ppy.sh/a/{new_user['user_id']}")
    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap['beatmapset_id']}l.jpg")

    embed.add_field(name="Score", value=score)
    embed.add_field(name="PP", value=f"{round(float(play['pp']), 2)}/{max_pp}\n({pp_change})")
    embed.add_field(name="Rank", value=EMOJIS[play['rank'].lower()])
    embed.add_field(name="Accuracy", value=f"{acc} % ({acc_change})")
    embed.add_field(name="Combo", value=f"x{play['maxcombo']}/x{('≈' if mode != 'std' else '') + maxcombo}")
    embed.add_field(name="Mods", value=mods_str)
    embed.add_field(name="Stars", value=f"{round(float(beatmap['difficultyrating']), 2)}☆")
    embed.add_field(name="Hits", value=hits)
    embed.add_field(name='Map info', value=compute_map_info(beatmap, mode, maxcombo), inline=False)

    embed.set_footer(text="Score obtenu le/à", icon_url=ICON_URL)
    embed.timestamp = utils.compute_time(play['date'])

    return embed

def embed_user_info(user, mode) -> discord.Embed:
    embed = discord.Embed()

    wwr = "{:,}".format(user['pp_rank']).replace(",", "'")
    cr  = "{:,}".format(user['pp_country_rank']).replace(",", "'")
    embed.set_author(name = f"[{mode.upper()}] {user['username']} #{wwr} (#{cr} {utils.flag(user['country'])})", \
                     url = f"https://osu.ppy.sh/u/{user['user_id']}", icon_url = f"https://a.ppy.sh/{user['user_id']}_api.jpg")
    embed.set_thumbnail(url = f"https://a.ppy.sh/{user['user_id']}_api.jpg")

    rs  = "{:,}".format(user['ranked_score']).replace(",", "'")
    embed.add_field(name = "Ranked Score", value = rs)
    embed.add_field(name = "Raw pp", value = user['pp_raw'])
    embed.add_field(name = "Level", value = str(round(float(user['level']), 2)))
    embed.add_field(name = "Accuracy", value = f"{round(float(user['accuracy']), 2)}%")
    embed.add_field(name = "Play Count", value = user['playcount'])
    embed.add_field(name = "Play Time", value = utils.parse_date(int(user['total_seconds_played'])))

    ranks = f"{EMOJIS['xh']} {user['count_rank_ssh']}\t{EMOJIS['x']} {user['count_rank_ss']}\t{EMOJIS['sh']} {user['count_rank_sh']}\t" + \
            f"{EMOJIS['s']} {user['count_rank_s']}\t{EMOJIS['a']} {user['count_rank_a']}"
    embed.add_field(name = "Grades", value = ranks, inline = False)

    embed.set_footer(text="Ici depuis", icon_url=ICON_URL)
    embed.timestamp = utils.compute_time(user['join_date'])

    return embed

def embed_map_info(beatmap, mode, mods) -> discord.Embed:
    embed = discord.Embed(title = f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}]", \
                          url = f"https://osu.ppy.sh/b/{beatmap['beatmap_id']}")
    embed.set_author(name = f"Créée par {beatmap['creator']} [{mode.upper()}]", url = f"https://osu.ppy.sh/u/{beatmap['creator_id']}", \
                     icon_url = f"http://s.ppy.sh/a/{beatmap['creator_id']}")
    embed.set_thumbnail(url = f"https://b.ppy.sh/thumb/{beatmap['beatmapset_id']}l.jpg")

    dif = float(beatmap['difficultyrating'])
    map_id = beatmap['beatmap_id']
    objects = int(beatmap['count_normal']) + int(beatmap['count_slider']) + int(beatmap['count_spinner'])
    maxcombo = beatmap['max_combo'] if mode == 'std' else get_top_play(beatmap['beatmap_id'], mode)['maxcombo']

    desc = compute_map_info(beatmap, mode, maxcombo) + "\n\n"

    if mode == 'std': # std_pp(URL, MODS, ACC, COMBO, 100, 50, MISS)
        pp100 = std_pp.map(f"osu.ppy.sh/b/{map_id}", mods, 100, maxcombo, 0, 0, 0)
        pp99  = std_pp.map(f"osu.ppy.sh/b/{map_id}", mods, 99,  maxcombo, 0, 0, 0)
        pp97  = std_pp.map(f"osu.ppy.sh/b/{map_id}", mods, 97,  maxcombo, 0, 0, 0)
        pp95  = std_pp.map(f"osu.ppy.sh/b/{map_id}", mods, 95,  maxcombo, 0, 0, 0)
    if mode == 'taiko': # taiko_pp(MODS, STARS, OD, MAX_COMBO, ACCURACY, MISS)
        pp100 = taiko_pp(mods, dif, float(beatmap['diff_overall']), maxcombo, 100, 0)
        pp99  = taiko_pp(mods, dif, float(beatmap['diff_overall']), maxcombo, 99,  0)
        pp97  = taiko_pp(mods, dif, float(beatmap['diff_overall']), maxcombo, 97,  0)
        pp95  = taiko_pp(mods, dif, float(beatmap['diff_overall']), maxcombo, 95,  0)
    if mode == 'ctb': # ctb_pp(MODS, STARS, AR, MAX_COMBO, COMBO, ACCURACY, MISS)
        pp100 = ctb_pp(mods, dif, float(beatmap['diff_approach']), maxcombo, maxcombo, 100, 0)
        pp99  = ctb_pp(mods, dif, float(beatmap['diff_approach']), maxcombo, maxcombo, 99,  0)
        pp97  = ctb_pp(mods, dif, float(beatmap['diff_approach']), maxcombo, maxcombo, 97,  0)
        pp95  = ctb_pp(mods, dif, float(beatmap['diff_approach']), maxcombo, maxcombo, 95,  0)
    if mode == 'mania': # mania_pp(MODS, STARS, OD, SCORE, OBJECTS)
        pp100 = mania_pp(mods, dif, float(beatmap['diff_overall']), 1000000, objects)
        pp99  = mania_pp(mods, dif, float(beatmap['diff_overall']), 990000,  objects)
        pp97  = mania_pp(mods, dif, float(beatmap['diff_overall']), 970000,  objects)
        pp95  = mania_pp(mods, dif, float(beatmap['diff_overall']), 950000,  objects)

    desc += f"Avec mods: `{' '.join(mods)}`"
    desc += f"95%: `{round(pp95)}pp` 97%: `{round(pp97)}pp` 99%: `{round(pp99)}pp` 100%: `{round(pp100)}pp`"

    embed.description = desc
    embed.set_footer(text = "Mise à jour le/à", icon_url = ICON_URL)
    embed.timestamp = utils.compute_time(beatmap['last_updated'])

    return embed

def embed_mapset_info(mapset, mode) -> discord.Embed:
    embed = discord.Embed(title = f"{mapset[0]['artist']} - {mapset[0]['title']} {f'[{mode.upper()}]' if mode != '' else ''}")
    embed.set_author(name = f"Créé par {mapset[0]['creator']}", url = f"https://osu.ppy.sh/u/{mapset[0]['creator_id']}", \
                     icon_url = f"http://s.ppy.sh/a/{beatmap[0]['creator_id']}")

    desc = ""
    for i, beatmap in enumerate(mapset):
        dif = float(beatmap['difficultyrating'])
        maxcombo = beatmap['max_combo'] if mode == 'std' else get_top_play(beatmap['beatmap_id'], mode)['maxcombo']
        objects = int(beatmap['count_normal']) + int(beatmap['count_slider']) + int(beatmap['count_spinner'])

        if mode == 'std': max_pp = std_pp.map(f"osu.ppy.sh/b/{beatmap['beatmap_id']}", [], 100, maxcombo, 0, 0, 0)
        if mode == 'taiko': max_pp = taiko_pp([], dif, int(beatmap['diff_overall']), maxcombo, 100, 0)
        if mode == 'ctb': max_pp = ctb_pp([], dif, int(beatmap['diff_approach']), maxcombo, maxcombo, 100, 0)
        if mode == 'mania': max_pp = mania_pp([], dif, int(beatmap['diff_overall']), 1000000, objects)

        to_add = f"[{utils.MODE_IND[beatmap['mode']]}] {round(dif, 2)}☆ - {beatmap['version']} ({round(max_pp)}pp)\n"

        if len(desc) + len(to_add) <= 2048: desc += to_add
        else:
            amout = len(mapset) - i
            desc += f"\\> *...{amout} autre{'s' if amout > 1 else ''}...*"
            break

    embed.description = desc
    embed.set_footer(text = "Mise à jour le/à", icon_url = ICON_URL)
    embed.timestamp = utils.compute_time(mapset['last_updated'])

    return embed

def compute_hits(hits, mode) -> str:
    c0, c50, ckatu, c100, cgeki, c300 = hits
    formated_hits = ""
    if mode == 'std': formated_hits = f"{EMOJIS['300']} x{c300} / {EMOJIS['100']} x{c100}\n" + \
                                      f"{EMOJIS['50']} x{c50} / {EMOJIS['0']} x{c0}"
    if mode == 'ctb': formated_hits = f"Fruits: x{c300}\nTicks: x{c100}\nDroplets: x{c50}\nMiss: x{c0}"
    if mode == 'mania': formated_hits = f"{EMOJIS['300']} x{c300} / {EMOJIS['max']} x{cgeki}\n" + \
                                        f"{EMOJIS['200']} x{ckatu} / {EMOJIS['100']} x{c100}\n" + \
                                        f"{EMOJIS['50']} x{c50} / {EMOJIS['0']} x{c0}"
    if mode == 'taiko': formated_hits = f"Great: x{c300}\nGood: x{c100}\nMiss: x{c0}"

    return formated_hits

def compute_acc(hits, mode) -> float:
    c0, c50, ckatu, c100, cgeki, c300 = hits
    c0, c50, ckatu, c100, cgeki, c300 = int(c0), int(c50), int(ckatu), int(c100), int(cgeki), int(c300)
    acc = 1
    if mode == 'std': acc = float( (c50*50 + c100*100 + c300*300) / (c0 + c50 + c100 + c300) * 300 )
    if mode == 'ctb': acc = float( (c50 + c100 + c300) / (c0 + ckatu + c50 + c100 + c300) )
    if mode == 'mania': acc = float( (c50*50+c100*100+ckatu*200+(c300+cgeki)*300) / ((c0+c50+c100+ckatu+c300+cgeki)*300) )
    if mode == 'taiko': acc = float( (0.5 * c100 + c300) / (c0 + c100 + c300) )
    return round(acc*100, 2)

def compute_mods(mods) -> (str, str):
    if mods <= 0: return '0', '∅'
    mod_list = ['NF', 'EZ', 'NV', 'HD', 'HR', 'SD', 'DT', 'RX', 'HT', 'NC', 'FL', 'AP', 'SO', 'AP', 'PF', '4K', '5K', '6K', '7K', '8K', 'KM', 'FI', 'RD', 'LM', 'FM', '9K', '10K', '1K', '3K', '2K']
    bin_list = [int(x) for x in bin(mods)[2:]]
    mods, mods_str = [], ''
    for i, y in enumerate(reversed(bin_list)):
        if y == 1 and mod_list[i] not in ['NC', 'PF']:
            try: mods_str += EMOJIS[mod_list[i].lower()]
            except KeyError: mods_str += mod_list[i]
            mods.append(mod_list[i])
    return mods, mods_str

def compute_map_info(beatmap, mode, maxcombo) -> str:
    Lmin, Lsec = divmod(int(beatmap['total_length']), 60)   
    Smin, Ssec = divmod(int(beatmap['hit_length']), 60)
    info = ""
    info += f"Créateur : `{beatmap['creator']}` ID : `{beatmap['beatmap_id']}`\n"
    info += f"Durée: `{Lmin}:{Lsec}` (`{Smin}:{Ssec}`) BPM: `{beatmap['bpm']}` Combo: `{('≈' if mode != 'std' else '') + maxcombo}`\n"
    if mode != 'mania': info += f"CS: `{beatmap['diff_size']}` AR: `{beatmap['diff_approach']}` OD: `{beatmap['diff_overall']}` HP: `{beatmap['diff_drain']}`"
    else: info += f"Keys: `{beatmap['diff_size']}` OD: `{beatmap['diff_overall']}` HP: `{beatmap['diff_drain']}`"
    info += f"Stars: `{round(float(beatmap['difficultyrating']), 2)}☆`\n"
    info += f"Status: `{beatmap['approved']}` Taux de réussite: `{pass_value(int(beatmap['passcount']), int(beatmap['playcount']))}%`"

    return info

def pass_value(passcount, playcount):
    if passcount == 0 or playcount == 0: return 0
    return round(float(passcount / playcount * 100), 1)

def taiko_pp(mods, sr, od, max_combo, acc, miss) -> float:
    if 'EZ' in mods: od /= 2
    if 'HR' in mods: od *= 1.4
    od = max(min(od, 10), 0)
    od = int(20 + (50 - 20) * od / 10) - 0.5
    if 'HT' in mods: od /= 0.75
    if 'DT' in mods: od /= 1.5
    od = round(od * 100) / 100

    combo = max_combo - miss

    sr_value = pow(max(1, sr / 0.0075) * 5 - 4,2) / 100000
    lenght_bonus = min(1, max_combo / 1500) * 0.1 + 1
    sr_value *= lenght_bonus
    sr_value *= pow(0.985, miss)
    sr_value *= min(pow(combo, 0.5) / pow(max_combo, 0.5), 1)
    sr_value *= acc / 100
    acc_value = pow(150 / od, 1.1) * pow(acc / 100, 15) * 22
    acc_value *= min(pow(max_combo / 1500, 0.3), 1.15)
    mod_mult = 1.10
    if 'HD' in mods:
        mod_mult *= 1.10
        sr_value *= 1.025
    if 'NF' in mods: mod_mult *= 0.90
    if 'FL' in mods: sr_value *= 1.05 * lenght_bonus
    total = pow(pow(sr_value, 1.1) + pow(acc_value, 1.1), 1 / 1.1) * mod_mult
    return round(total * 100) / 100

def ctb_pp(mods, sr, ar, max_combo, combo, acc, miss) -> float:
    if 'DT' in mods:
        ms = 200 + (11 - ar) * 100 if ar > 5 else 800 + (5 - ar) * 80
        if ms < 300: ar = 11
        elif ms < 1200: ar = round((11 - (ms - 300) / 150) * 100) / 100
        else: ar = round((5 - (ms - 1200) / 120) * 100) / 100
    if 'HT' in mods:
        ms = 400 + (11 - ar) * 200 if ar > 5 else 1600 + (5 - ar) * 160
        if ms < 600: ar = 10
        elif ms < 1200: ar = round((11 - (ms - 300) / 150) * 100) / 100
        else: ar = round((5 - (ms - 1200) / 120) * 100) / 100

    final = pow(((5 * sr / 0.0049) - 4), 2) / 100000
    lenght_bonus = (0.95 + 0.3 * min(1, max_combo / 2500) + (log10(max_combo / 2500) * 0.475 if max_combo > 2500 else 0))
    final *= lenght_bonus
    final *= pow(0.97, miss)
    final *= pow(combo / max_combo, 0.8)
    arbonus = 1
    if ar > 9:  arbonus += 0.1 * (ar - 9.0)
    if ar > 10: arbonus += 0.1 * (ar - 10.0)
    if ar < 8:  arbonus += 0.025 * (8.0 - ar)
    final *= arbonus
    hiddenbonus = 1.01 + 0.04 * (11 - min(11, ar)) if ar > 10 else 1.05 + 0.075 * (10 - ar)
    final *= pow(acc / 100, 5.5)

    if 'HD' in mods and 'FL' in mods: return round(100 * final * 1.35 * lenght_bonus * hiddenbonus) / 100
    if 'FL' in mods: return round(100 * final * 1.35 * lenght_bonus) / 100
    if 'HD' in mods: return round(100 * final * hiddenbonus) / 100
    return round(100 * final) / 100

def mania_pp(mods, sr, od, score, objects) -> float:
    nerfpp = (0.5 if 'EZ' in mods else 1) * (0.9 if 'NF' in mods else 1)
    nerfod = 0.5 if 'EZ' in mods else 1

    if score < 500000: return 0

    sb = pow(5 * max(1, sr / 0.2) - 4, 2.2) / 135 * (1 + 0.1 * min(1, objects / 1500))
    if score < 500000: sm = score / 500000 * 0.1
    elif score < 600000: sm = (score - 500000) / 100000 * 0.3
    elif score < 700000: sm = (score - 600000) / 100000 * 0.25 + 0.3
    elif score < 800000: sm = (score - 700000) / 100000 * 0.2 + 0.55
    elif score < 900000: sm = (score - 800000) / 100000 * 0.15 + 0.75
    else: sm = (score - 900000) / 100000 * 0.1 + 0.9
    av = od * nerfod * 0.02 * sb * pow((score - 960000) / 40000, 1.1) if score >= 960000 else 0

    return round((0.73 * pow(pow(av, 1.1) + pow(sb * sm, 1.1), 1 / 1.1) * 1.1 * nerfpp), 2)