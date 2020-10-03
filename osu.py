key='YOUR OSU KEY HERE'
import sys, os
import json
from jsondiff import diff
import jsondiff
import aiohttp
import asyncio
import discord
import botutils
import calc
import stats as vari
vari.init()

import mania_pp_calc as mania_pp
import ctb_pp_calc as ctb_pp
import taiko_pp_calc as taiko_pp

signature = 'Osu! Tracking Bot created by nalo_'
#mode: std = 0, ctb = 2, mania = 3, taiko = 1
mode_value = {"std": 0, "taiko": 1, "ctb": 2, "mania": 3}
reversed_mode_value = ['std', 'taiko', 'ctb', 'mania']

emojis = {'0': '<:hit_0:542327683858563084>', '50': '<:hit_50:542327689244049410>', '100': '<:hit_100:542327693526433793>', '200': '<:hit_200:542327700048576513>', '300': '<:hit_300:542327701327970344>', 'max': '<:hit_max:542327700400898048>', 'fc': '<:fc:542327030121889792>',
		  'a': '<:rank_a:542327056025911316>', 'b': '<:rank_b:542327056353198090>', 'c': '<:rank_c:542327049793175552>', 'd': '<:rank_d:542327053710524425>', 's': '<:rank_s:542327053714718720>', 'sh': '<:rank_sh:542327049298378752>', 'x': '<:rank_x:542327056600530975>', 'xh': '<:rank_xh:542327053916176384>',
		  '4k': '<:mod_4k:542327012296228865>', '5k': '<:mod_5k:542327012254023698>', '6k': '<:mod_6k:542327014980583454>', '7k': '<:mod_7k:542327026300747777>', '8k': '<:mod_8k:542327026342690819>', 
		  'ap': '<:mod_ap:542327026674171905>', 'dt' : '<:mod_dt:542327029928820736>', 'ez': '<:mod_ez:542327026871304222>', 'fi': '<:mod_fi:542327026896601089>', 'fl': '<:mod_fl:542327026850332702>', 'hd': '<:mod_hd:542327029626961963>', 
		  'hr': '<:mod_hr:542327029941665795>', 'ht': '<:mod_ht:542327027076956171>', 'nc': '<:mod_nc:542327027299254282>', 'nf': '<:mod_nf:542327029841002498>', 'pf': '<:mod_pf:542327027198590987>', 'rx': '<:mod_rx:542327027382878230>', 
		  'sd': '<:mod_sd:542327029991735296>', 'so': '<:mod_so:542327030209970186>'}

async def check_user(user, mode):
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(f'https://osu.ppy.sh/api/get_user?k={key}&m={str(mode_value[mode])}&u={user}') as r:
				vari.stats['api_usage'] += 1
				if len(await r.text()) > 4:
					return 1
	except Exception as e:
		print("In Check user:")
		print(e)
		return -1
	return 0
	
async def track_user(user, mode):
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(f'https://osu.ppy.sh/api/get_user_best?k={key}&m={str(mode_value[mode])}&u={user}&limit=50') as r:
				vari.stats['api_usage'] += 1
				raw_r = await r.text()
				if len(raw_r) > 4:
					jr = json.loads(raw_r)
					with open('data/'+mode+'/'+user, 'r') as myfile:
						jdata = json.load(myfile)
					if jr != jdata :
						e = diff(jdata, jr)
						if jsondiff.insert in e:
							play = e[jsondiff.insert]
							with open('data/'+mode+'/'+user, "w") as raw:
								raw.write(raw_r)
							return (1,len(e[jsondiff.insert]),play)
						with open('data/'+mode+'/'+user, "w") as raw:
							raw.write(raw_r)
	except Exception as e:
		print("In Track_user:")
		print(e)
		return -1
	return 0


async def get_recent(user, mode):
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(f'https://osu.ppy.sh/api/get_user_recent?k={key}&m={str(mode_value[mode])}&u={user}&limit=20') as r:
				vari.stats['api_usage'] += 1
				raw_r = await r.text()
				if len(raw_r) > 4:
					jr = json.loads(raw_r)
					n = 0
					for i in range(len(jr)):
							if jr[i-n]['rank'] == 'F':
								del jr[i-n]
								n += 1
					return jr
				else: return None
	except Exception as e:
		print("In get recent:")
		print(e)
		return -1
	return 0
	

async def get_map_mode(map_id):
	dic_ret = await get_map(map_id, '0')
	if dic_ret != -1: return 'std', '0'
	else:
		dic_ret = await get_map(map_id, '1')
		if dic_ret != -1: return 'taiko', '1'
		else:
			dic_ret = await get_map(map_id, '2')
			if dic_ret != -1: return 'ctb', '2'
			else:
				dic_ret = await get_map(map_id, '3')
				if dic_ret != -1: return 'mania', '3'
				else: return -1, -1

	
async def print_play(play, top, user):
	map = await get_map(str(play['beatmap_id']), '0')
	url = 'https://osu.ppy.sh/b/'+str(map['beatmap_id'])
	mods_str, mods_emoj = get_mods(int(play['enabled_mods']))
	with open('tracked_users_std', 'r') as myfile:
		tracklist = json.load(myfile)
		old_user_info = str(tracklist[user]).split('|')
		old_rank = str(old_user_info[1])
		old_pp = str(old_user_info[2])
		new_user_inf, useless = await get_user_info(user, 'std')
		new_rank = str(new_user_inf['pp_rank'])
		new_pp = str(new_user_inf['pp_raw'])
		diff_rank = int(int(old_rank) - int(new_rank))
		if diff_rank >= 0: diff_rank = str('+'+str(diff_rank))
		diff_pp = float(float(new_pp) - float(old_pp))
		if diff_pp >= 0: diff_pp = str('+'+str(diff_pp))
		diff_pp = str(diff_pp)[:5]

	tracklist[user] = str(old_user_info[0])+'|'+str(new_rank)+'|'+str(new_pp)
	with open('tracked_users_std', 'w') as myfile:
		json.dump(tracklist, myfile)

	if map == -1: return -1
	try:
		date = str(compute_time(str(play['date'])))
		if date == -1: date = str(play['date'])
		acc = str(compute_acc(str(play['countmiss']), str(play['count50']), '0', str(play['count100']), '0', str(play['count300']), 'std'))
		if str(acc) == '1.0': acc = '100 %'
		else: acc = acc[2:][:2]+','+acc[4:][:2]+' %'
		#time = str(calc_date(str(play['date'])))
		score = "'".join(str(play['score'])[::-1][i:i+3] for i in range(0, len(str(play['score'])), 3))[::-1]
		
		try:
			ret = await botutils.dl_image("https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg", str(map['beatmapset_id'])+'.jpg', 'm')
			if ret == -1: raise NameError('Fail dl')
			chex = botutils.av_color('data/m/'+str(map['beatmapset_id'])+'.jpg')
			if chex == -1: raise NameError('Fail color calc')
		except Exception: chex = 0xf44242
		embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
		
		if top != -1: embedz.set_author(name='Nouveau top #'+str(top+1)+' standard par '+str(user)+' :')
		else: embedz.set_author(name='Nouveau récent standard par '+str(user)+' :')
		embedz.set_thumbnail(url="https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg")
		
		embedz.add_field(name='Score', value=str(score)+'\n('+str(diff_rank)+', '+str(diff_pp)+'pp)', inline=True)
		# embedz.add_field(name='PP', value=str(play['pp'])+'/'+str(calc.map('https://osu.ppy.sh/b/'+str(map['beatmap_id']), mods_str, 100, int(play['maxcombo']), 0)), inline=True)
		if top != -1: embedz.add_field(name='PP', value=str(play['pp']), inline=True)
		embedz.add_field(name='Rank', value=emojis[str(play['rank']).lower()], inline=True)
		embedz.add_field(name='Accuracy', value=str(acc), inline=True)
		if int(play['perfect']) == 1: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/x'+str(map['max_combo'])+' ('+emojis['fc']+')', inline=True)
		else: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/x'+str(map['max_combo']), inline=True)
		try: embedz.add_field(name='Mods', value=str(mods_emoj), inline=True)
		except Exception: embedz.add_field(name='Mods', value=str(mods_str), inline=True)
		embedz.add_field(name='Stars', value=str(map['difficultyrating'])[:4]+"☆", inline=True)
		# embedz.add_field(name='Hits [300/100/50/miss]', value=". . . . .[ "+str(play['count300'])+" / "+str(play['count100'])+" / "+str(play['count50'])+" / "+str(play['countmiss'])+" ]", inline=True)
		embedz.add_field(name='Hits', value=emojis['300']+' x'+str(play['count300'])+' / '+emojis['100']+' x'+str(play['count100'])+'\n'+emojis['50']+' x'+str(play['count50'])+' / '+emojis['0']+' x'+str(play['countmiss']), inline=True)
		embedz.add_field(name='Date', value=date+"\n ", inline=True)

		Lmin, Lsec = divmod(int(map['total_length']), 60)
		Smin, Ssec = divmod(int(map['hit_length']), 60)
		passvalue = str(pass_value(str(map['passcount']), str(map['playcount'])))
		info = ""
		info += "Créateur : `{}` ID : `{}`\n".format(map['creator'], map['beatmap_id'])
		info += "Durée: `{}:{}` (`{}:{}`)  BPM: `{}`  Combo: `{}`\n".format(Lmin, Lsec, Smin, Ssec, map['bpm'], map['max_combo'])
		info += "CS: `{}`  AR: `{}`  OD: `{}`  HP: `{}`  Stars: `{}☆`\n".format(map['diff_size'], map['diff_approach'], map['diff_overall'], map['diff_drain'], map['difficultyrating'][:4])
		# info += "95%: `{}pp` 97%: `{}pp` 99%: `{}pp` 100%: `{}pp`\n".format(calc.map(str(np['url']), str(np['mods']), 95, int(np['combo']), int(np['miss'])), calc.map(str(np['url']), str(np['mods']), 97, int(np['combo']), int(np['miss'])), calc.map(str(np['url']), str(np['mods']), 99, int(np['combo']), int(np['miss'])), calc.map(str(np['url']), str(np['mods']), 100, int(np['combo']), int(np['miss'])))
		info += "Status: `{}`  Taux de réussite: `{}%`".format(map['approved'], passvalue[:4])
		embedz.add_field(name='Map info', value=info, inline=True)
		embedz.set_footer(text = signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')

		if top != -1: print('[std] Play by : '+str(user)+', '+play['pp']+'pp')
	except Exception as e:
		print('In Print play:')
		print(e)
		return -1
	return embedz

async def print_play_mania(play, top, user):
	map = await get_map(str(play['beatmap_id']), '3')
	bestplay = await get_top_play(str(play['beatmap_id']), '3')
	mode = ''
	if map == -1:
		mode = 'mania mode'
		map = await get_map(str(play['beatmap_id']), '3&a=1')
		if map == -1:
			mode = ''
			return -1		
	mods_str, mods_emoj = get_mods(int(play['enabled_mods']))
	with open('tracked_users_mania', 'r') as myfile:
		tracklist = json.load(myfile)
		old_user_info = str(tracklist[user]).split('|')
		old_rank = str(old_user_info[1])
		old_pp = str(old_user_info[2])
		new_user_inf, useless = await get_user_info(user, 'mania')
		new_rank = str(new_user_inf['pp_rank'])
		new_pp = str(new_user_inf['pp_raw'])
		diff_rank = int(int(old_rank) - int(new_rank))
		if diff_rank >= 0: diff_rank = str('+'+str(diff_rank))
		diff_pp = float(float(new_pp) - float(old_pp))
		if diff_pp >= 0: diff_pp = str('+'+str(diff_pp))
		diff_pp = str(diff_pp)[:5]

	# try:
	date = str(compute_time(str(play['date'])))
	if date == -1: date = str(play['date'])
	acc = str(compute_acc(str(play['countmiss']), str(play['count50']), str(play['countkatu']), str(play['count100']), str(play['countgeki']), str(play['count300']), 'mania'))
	if acc == '1.0': acc = '100 %'
	else: acc = acc[2:][:2]+','+acc[4:][:2]+' %'
	#time = str(calc_date(str(play['date'])))
	score = "'".join(str(play['score'])[::-1][i:i+3] for i in range(0, len(str(play['score'])), 3))[::-1]
	
	try:
		ret = await botutils.dl_image("https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg", str(map['beatmapset_id'])+'.jpg', 'm')
		if ret == -1: raise NameError('Fail dl')
		chex = botutils.av_color('data/m/'+str(map['beatmapset_id'])+'.jpg')
		if chex == -1: raise NameError('Fail color calc')
		embedz=discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
	except Exception: chex = 0xf44242

	if mode == 'mania mode': embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"] ["+mode+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
	else: embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
	if top != -1: embedz.set_author(name='Nouveau top #'+str(top+1)+' mania par '+str(user)+' :')
	else: embedz.set_author(name='Nouveau récent mania par '+str(user)+' :')
	embedz.set_thumbnail(url="https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg")
	
	embedz.add_field(name='Score', value=str(score)+'\n('+str(diff_rank)+', '+str(diff_pp)+'pp)', inline=True)
	if top != -1: embedz.add_field(name='PP', value=str(play['pp']), inline=True)
	embedz.add_field(name='Rank', value=emojis[str(play['rank']).lower()], inline=True)
	embedz.add_field(name='Accuracy', value=str(acc), inline=True)
	if int(play['perfect']) == 1: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/≈x'+str(bestplay['maxcombo'])+' ('+emojis['fc']+')', inline=True)
	else: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/≈x'+str(bestplay['maxcombo']), inline=True)
	try: embedz.add_field(name='Mods', value=str(mods_emoj), inline=True)
	except Exception: embedz.add_field(name='Mods', value=str(mods_str), inline=True)
	embedz.add_field(name='Stars', value=str(map['difficultyrating'])[:4]+"☆", inline=True)
	# embedz.add_field(name='[Max/300/200/100/50/miss]', value="["+str(play['countgeki'])+"/"+str(play['count300'])+"/"+str(play['countkatu'])+"/"+str(play['count100'])+"/"+str(play['count50'])+"/"+str(play['countmiss'])+"]", inline=True)
	# embedz.add_field(name='Hits', value=emojis['max']+' x'+str(play['countgeki'])+' / '+emojis['300']+' x'+str(play['count300'])+'\n'+emojis['200']+' x'+str(play['countkatu'])+' / '+emojis['100']+' x'+str(play['count100'])+'\n'+emojis['50']+' x'+str(play['count50'])+' / '+emojis['0']+' x'+str(play['countmiss']), inline=True)
	embedz.add_field(name='Hits (ratio: {})'.format(str(int(play['countgeki'])/int(play['count300']))[:4]), value=emojis['300']+' x'+str(play['count300'])+' / '+emojis['max']+' x'+str(play['countgeki'])+'\n'+emojis['200']+' x'+str(play['countkatu'])+' / '+emojis['100']+' x'+str(play['count100'])+'\n'+emojis['50']+' x'+str(play['count50'])+' / '+emojis['0']+' x'+str(play['countmiss']), inline=True)
	embedz.add_field(name='Date', value=date+"\n", inline=True)

	Lmin, Lsec = divmod(int(map['total_length']), 60)
	Smin, Ssec = divmod(int(map['hit_length']), 60)
	passvalue = str(pass_value(str(map['passcount']), str(map['playcount'])))
	info = ""
	info += "Créateur : `{}` ID : `{}`\n".format(map['creator'], map['beatmap_id'])
	info += "Durée: `{}:{}` (`{}:{}`)  BPM: `{}`  Combo: `≈{}`\n".format(Lmin, Lsec, Smin, Ssec, map['bpm'], bestplay['maxcombo'])
	info += "Keys: `{}`  OD: `{}`  HP: `{}`  Stars: `{}☆`\n".format(map['diff_size'], map['diff_overall'], map['diff_drain'], map['difficultyrating'][:4])
	info += "Status: `{}`  Taux de réussite: `{}%`".format(map['approved'], passvalue[:4])
	embedz.add_field(name='Map info', value=info, inline=True)
	embedz.set_footer(text = signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')

	tracklist[user] = str(old_user_info[0])+'|'+str(new_rank)+'|'+str(new_pp)
	with open('tracked_users_mania', 'w') as myfile:
		json.dump(tracklist, myfile)
	if top != -1: print('[mania] Play by : '+str(user)+', '+play['pp']+'pp')
	# except Exception as e:
	# 	print('In Print play:')
	# 	print(e)
	# 	return -1
	return embedz

async def print_play_ctb(play, top, user):
	map = await get_map(str(play['beatmap_id']), '2')
	bestplay = await get_top_play(str(play['beatmap_id']), '2')
	mode = ''
	if map == -1:
		mode = 'CTB mode'
		map = await get_map(str(play['beatmap_id']), '2&a=1')
		if map == -1:
			mode = ''
			return -1
	mods_str, mods_emoj = get_mods(int(play['enabled_mods']))
	with open('tracked_users_ctb', 'r') as myfile:
		tracklist = json.load(myfile)
		old_user_info = str(tracklist[user]).split('|')
		old_rank = str(old_user_info[1])
		old_pp = str(old_user_info[2])
		new_user_inf, useless = await get_user_info(user, 'ctb')
		new_rank = str(new_user_inf['pp_rank'])
		new_pp = str(new_user_inf['pp_raw'])
		diff_rank = int(int(old_rank) - int(new_rank))
		if diff_rank >= 0: diff_rank = str('+'+str(diff_rank))
		diff_pp = float(float(new_pp) - float(old_pp))
		if diff_pp >= 0: diff_pp = str('+'+str(diff_pp))
		diff_pp = str(diff_pp)[:5]

	try:
		date = str(compute_time(str(play['date'])))
		if date == -1: date = str(play['date'])
		acc = str(compute_acc(str(play['countmiss']), str(play['count50']), str(play['countkatu']), str(play['count100']), str(play['countgeki']), str(play['count300']), 'ctb'))
		if acc == '1.0': acc = '100 %'
		else: acc = acc[2:][:2]+','+acc[4:][:2]+' %'
		# time = str(calc_date(str(play['date'])))
		score = "'".join(str(play['score'])[::-1][i:i+3] for i in range(0, len(str(play['score'])), 3))[::-1]
		
		try:
			ret = await botutils.dl_image("https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg", str(map['beatmapset_id'])+'.jpg', 'm')
			if ret == -1: raise NameError('Fail dl')
			chex = botutils.av_color('data/m/'+str(map['beatmapset_id'])+'.jpg')
			if chex == -1: raise NameError('Fail color calc')
		except Exception: chex = 0x42f442

		if mode == 'CTB mode': embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"] ["+mode+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
		else: embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
		if top != -1: embedz.set_author(name='Nouveau top #'+str(top+1)+' catch par '+str(user)+' :')
		else: embedz.set_author(name='Nouveau récent catch par '+str(user)+' :')
		embedz.set_thumbnail(url="https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg")
		
		embedz.add_field(name='Score', value=str(score)+'\n('+str(diff_rank)+', '+str(diff_pp)+'pp)', inline=True)
		if top != -1: embedz.add_field(name='PP', value=str(play['pp']), inline=True)
		embedz.add_field(name='Rank', value=emojis[str(play['rank']).lower()], inline=True)
		embedz.add_field(name='Accuracy', value=str(acc), inline=True)
		if int(play['perfect']) == 1: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/x'+str(bestplay['maxcombo'])+' ('+emojis['fc']+')', inline=True)
		else: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/x'+str(bestplay['maxcombo']), inline=True)
		try: embedz.add_field(name='Mods', value=str(mods_emoj), inline=True)
		except Exception: embedz.add_field(name='Mods', value=str(mods_str), inline=True)
		embedz.add_field(name='Stars', value=str(map['difficultyrating'])[:4]+"☆", inline=True)
		# embedz.add_field(name='Hits [fruits/ticks/droplets/miss]', value=". . . . .[ "+str(play['count300'])+" / "+str(play['count100'])+" / "+str(play['count50'])+" / "+str(play['countmiss'])+" ]", inline=True)
		embedz.add_field(name='Hits', value='Fruits: x'+str(play['count300'])+'\nTicks: x'+str(play['count100'])+'\nDroplets: x'+str(play['count50'])+'\nMiss: x'+str(play['countmiss']), inline=True)
		embedz.add_field(name='Date', value=date+"\n", inline=True)

		Lmin, Lsec = divmod(int(map['total_length']), 60)
		Smin, Ssec = divmod(int(map['hit_length']), 60)
		passvalue = str(pass_value(str(map['passcount']), str(map['playcount'])))
		info = ""
		info += "Créateur : `{}` ID : `{}`\n".format(map['creator'], map['beatmap_id'])
		info += "Durée: `{}:{}` (`{}:{}`)  BPM: `{}`  Combo: `{}`\n".format(Lmin, Lsec, Smin, Ssec, map['bpm'], bestplay['maxcombo'])
		info += "CS: `{}`  AR: `{}`  OD: `{}`  HP: `{}`  Stars: `{}☆`\n".format(str(map['diff_size']), str(map['diff_approach']), str(map['diff_overall']), str(map['diff_drain']), str(map['difficultyrating'])[:4])
		info += "Status: `{}`  Taux de réussite: `{}%`".format(map['approved'], passvalue[:4])
		embedz.add_field(name='Map info', value=info, inline=True)
		embedz.set_footer(text = signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')

		tracklist[user] = str(old_user_info[0])+'|'+str(new_rank)+'|'+str(new_pp)
		with open('tracked_users_ctb', 'w') as myfile:
			json.dump(tracklist, myfile)
		if top != -1: print('[CTB] Play by : '+str(user)+', '+play['pp']+'pp')
	except Exception as e:
		print('In Print play ctb:')
		print(e)
		return -1
	return embedz

async def print_play_taiko(play, top, user):
	map = await get_map(str(play['beatmap_id']), '1')
	bestplay = await get_top_play(str(play['beatmap_id']), '1')
	mode = ''
	if map == -1:
		mode = 'taiko mode'
		map = await get_map(str(play['beatmap_id']), '1&a=1')
		if map == -1:
			mode = ''
			return -1
	mods_str, mods_emoj = get_mods(int(play['enabled_mods']))
	with open('tracked_users_taiko', 'r') as myfile:
		tracklist = json.load(myfile)
		old_user_info = str(tracklist[user]).split('|')
		old_rank = str(old_user_info[1])
		old_pp = str(old_user_info[2])
		new_user_inf, useless = await get_user_info(user, 'taiko')
		new_rank = str(new_user_inf['pp_rank'])
		new_pp = str(new_user_inf['pp_raw'])
		diff_rank = int(int(old_rank) - int(new_rank))
		if diff_rank >= 0: diff_rank = str('+'+str(diff_rank))
		diff_pp = float(float(new_pp) - float(old_pp))
		if diff_pp >= 0: diff_pp = str('+'+str(diff_pp))
		diff_pp = str(diff_pp)[:5]

	try:
		date = str(compute_time(str(play['date'])))
		if date == -1: date = str(play['date'])
		acc = str(compute_acc(str(play['countmiss']), '0', '0', str(play['count100']), '0', str(play['count300']), 'taiko'))
		if acc == '1.0': acc = '100 %'
		else: acc = acc[2:][:2]+','+acc[4:][:2]+' %'
		# time = str(calc_date(str(play['date'])))
		score = "'".join(str(play['score'])[::-1][i:i+3] for i in range(0, len(str(play['score'])), 3))[::-1]
		
		try:
			ret = await botutils.dl_image("https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg", str(map['beatmapset_id'])+'.jpg', 'm')
			if ret == -1: raise NameError('Fail dl')
			chex = botutils.av_color('data/m/'+str(map['beatmapset_id'])+'.jpg')
			if chex == -1: raise NameError('Fail color calc')
		except Exception: chex = 0x42f442

		if mode == 'taiko mode': embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"] ["+mode+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
		else: embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=chex)
		if top != -1: embedz.set_author(name='Nouveau top #'+str(top+1)+' taiko par '+str(user)+' :')
		else: embedz.set_author(name='Nouveau récent taiko par '+str(user)+' :')
		embedz.set_thumbnail(url="https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg")
		
		embedz.add_field(name='Score', value=str(score)+'\n('+str(diff_rank)+', '+str(diff_pp)+'pp)', inline=True)
		if top != -1: embedz.add_field(name='PP', value=str(play['pp']), inline=True)
		embedz.add_field(name='Rank', value=emojis[str(play['rank']).lower()], inline=True)
		embedz.add_field(name='Accuracy', value=str(acc), inline=True)
		if int(play['perfect']) == 1: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/≈x'+str(bestplay['maxcombo'])+' ('+emojis['fc']+')', inline=True)
		else: embedz.add_field(name='Combo', value='x'+str(play['maxcombo'])+'/≈x'+str(bestplay['maxcombo']), inline=True)
		try: embedz.add_field(name='Mods', value=str(mods_emoj), inline=True)
		except Exception: embedz.add_field(name='Mods', value=str(mods_str), inline=True)
		embedz.add_field(name='Stars', value=str(map['difficultyrating'])[:4]+"☆", inline=True)
		# embedz.add_field(name='Hits [great/good/miss]', value=". . . . .[ "+str(play['count300'])+" / "+str(play['count100'])+" / "+str(play['countmiss'])+" ]", inline=True)
		embedz.add_field(name='Hits', value='Great: x'+str(play['count300'])+'\nGood: x'+str(play['count100'])+'\nMiss: x'+str(play['countmiss']), inline=True)
		embedz.add_field(name='Date', value=date+"\n", inline=True)

		Lmin, Lsec = divmod(int(map['total_length']), 60)
		Smin, Ssec = divmod(int(map['hit_length']), 60)
		passvalue = str(pass_value(str(map['passcount']), str(map['playcount'])))
		info = ""
		info += "Créateur : `{}` ID : `{}`\n".format(map['creator'], map['beatmap_id'])
		info += "Durée: `{}:{}` (`{}:{}`)  BPM: `{}`  Combo: `≈{}`\n".format(Lmin, Lsec, Smin, Ssec, map['bpm'], bestplay['maxcombo'])
		info += "CS: `{}`  AR: `{}`  OD: `{}`  HP: `{}`  Stars: `{}☆`\n".format(map['diff_size'], map['diff_approach'], map['diff_overall'], map['diff_drain'], map['difficultyrating'][:4])
		info += "Status: `{}`  Taux de réussite: `{}%`".format(map['approved'], passvalue[:4])
		embedz.add_field(name='Map info', value=info, inline=True)
		embedz.set_footer(text = signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')

		tracklist[user] = str(old_user_info[0])+'|'+str(new_rank)+'|'+str(new_pp)
		with open('tracked_users_taiko', 'w') as myfile:
			json.dump(tracklist, myfile)
		if top != -1: print('[taiko] Play by : '+str(user)+', '+play['pp']+'pp')
	except Exception as e:
		print('In Print play taiko:')
		print(e)
		return -1
	return embedz
	
async def embed_map_info(map_id, mode, mods, acc, combo, miss):
	map = await get_map(str(map_id), str(mode_value[mode]))
	mods2 = []
	if mode != 'std':
		bestplay = await get_top_play(str(map_id), str(mode_value[mode]))
		map['max_combo'] = bestplay['maxcombo']
	if map == -1:
		return -1
	if combo == 0:
		combo = int(map['max_combo'])
	if mods != '0' and mods != None:
		mods2 = [mods[i:i+2] for i in range(0, len(mods), 2)]
	try:
		if mode == 'std': # calc.map(URL, MODS, ACC, COMBO, MISS)
			ppCust = calc.map('osu.ppy.sh/b/'+map_id, str(mods), float(acc), int(combo), int(miss))
			pp100 = calc.map('osu.ppy.sh/b/'+map_id, str(mods), 100, int(combo), int(miss))
			pp99 = calc.map('osu.ppy.sh/b/'+map_id, str(mods), 99, int(combo), int(miss))
			pp97 = calc.map('osu.ppy.sh/b/'+map_id, str(mods), 97, int(combo), int(miss))
			pp95 = calc.map('osu.ppy.sh/b/'+map_id, str(mods), 95, int(combo), int(miss))
		if mode == 'mania': # mania_pp.pp(STARS, ACCURACY, NB_NOTE, SCORE, OD, MODS)
			ppCust = mania_pp.pp(float(map['difficultyrating']), float(acc), int(map['count_normal'])+int(map['count_slider']), int(1000000*(acc/100)), float(map['diff_overall']), mods2)
			pp100 = mania_pp.pp(float(map['difficultyrating']), 100, int(map['count_normal'])+int(map['count_slider']), int(1000000*(100/100)), float(map['diff_overall']), mods2)
			pp99 = mania_pp.pp(float(map['difficultyrating']), 99, int(map['count_normal'])+int(map['count_slider']), int(1000000*(99/100)), float(map['diff_overall']), mods2)
			pp97 = mania_pp.pp(float(map['difficultyrating']), 97, int(map['count_normal'])+int(map['count_slider']), int(1000000*(97/100)), float(map['diff_overall']), mods2)
			pp95 = mania_pp.pp(float(map['difficultyrating']), 95, int(map['count_normal'])+int(map['count_slider']), int(1000000*(95/100)), float(map['diff_overall']), mods2)
		if mode == 'ctb': # ctb_pp.pp(STARS, ACCURACY, MAX_COMBO, PLAYER_COMBO, MISS, AR, MODS)
			ppCust = ctb_pp.pp(float(map['difficultyrating']), float(acc), int(map['max_combo']), int(combo), int(miss), float(map['diff_approach']), mods2)
			pp100 = ctb_pp.pp(float(map['difficultyrating']), 100, int(map['max_combo']), int(combo), int(miss), float(map['diff_approach']), mods2)
			pp99 = ctb_pp.pp(float(map['difficultyrating']), 99, int(map['max_combo']), int(combo), int(miss), float(map['diff_approach']), mods2)
			pp97 = ctb_pp.pp(float(map['difficultyrating']), 97, int(map['max_combo']), int(combo), int(miss), float(map['diff_approach']), mods2)
			pp95 = ctb_pp.pp(float(map['difficultyrating']), 95, int(map['max_combo']), int(combo), int(miss), float(map['diff_approach']), mods2)
		if mode == 'taiko': # taiko_pp.pp(STARS, ACCURACY, MAX_COMBO, MISS, OD, MODS)
			ppCust = taiko_pp.pp(float(map['difficultyrating']), float(acc), int(map['max_combo']), int(miss), float(map['diff_overall']), mods2)
			pp100 = taiko_pp.pp(float(map['difficultyrating']), 100, int(map['max_combo']), int(miss), float(map['diff_overall']), mods2)
			pp99 = taiko_pp.pp(float(map['difficultyrating']), 99, int(map['max_combo']), int(miss), float(map['diff_overall']), mods2)
			pp97 = taiko_pp.pp(float(map['difficultyrating']), 97, int(map['max_combo']), int(miss), float(map['diff_overall']), mods2)
			pp95 = taiko_pp.pp(float(map['difficultyrating']), 95, int(map['max_combo']), int(miss), float(map['diff_overall']), mods2)

		Lmin, Lsec = divmod(int(map['total_length']), 60)
		Smin, Ssec = divmod(int(map['hit_length']), 60)
		passvalue = str(pass_value(str(map['passcount']), str(map['playcount'])))
		embedz = discord.Embed(title=f"{str(map['artist'])} - {str(map['title'])} [{str(map['version'])}]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=0xf4f442)
		embedz.set_author(name=f"Créé par {str(map['creator'])} [{mode.upper()}]")
		embedz.set_thumbnail(url="https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg")		
		info = ""
		info += f"Durée: `{Lmin}:{Lsec}` (`{Smin}:{Ssec}`)  BPM: `{map['bpm']}`  Combo: `{map['max_combo']}`\n"
		if mode != 'mania':
			info += f"CS: `{map['diff_size']}`  AR: `{map['diff_approach']}`  OD: `{map['diff_overall']}`  HP: `{map['diff_drain']}`  Stars: `{map['difficultyrating'][:4]}☆`\n"
		else:
			info += f"Keys: `{map['diff_size']}`  OD: `{map['diff_overall']}`  HP: `{map['diff_drain']}`  Stars: `{map['difficultyrating'][:4]}☆`\n"
		info += f"Status: `{map['approved']}`  Taux de réussite: `{passvalue[:4]}%`\n\n"
		if mods != '0':
			info += f"Avec mods : `{mods}`\n"
		if acc != 0:
			info += f"{acc}%: `{ppCust}pp`\n"
		else:
			info += f"95%: `{pp95}pp` 97%: `{pp97}pp` 99%: `{pp99}pp` 100%: `{pp100}pp`\n"
		embedz.description = info
		embedz.set_footer(text = signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')
		return embedz
	except Exception as e:
		print('error in embed map info')
		print(e)
			

async def file_replay(play):
	mode = ''
	try:
		map = await get_map_hash(str(play.beatmap_hash))
		if str(play.game_mode) == 'GameMode.Standard': mode = 'std'
		elif str(play.game_mode) == 'GameMode.Osumania': mode = 'mania'
		elif str(play.game_mode) == 'GameMode.CatchTheBeat': mode = 'ctb'
		elif str(play.game_mode) == 'GameMode.Taiko': mode = 'taiko'
		user, useless = await get_user_info(str(play.player_name), mode, 0)

		if mode != 'std':
			bestplay = await get_top_play(str(map['beatmap_id']), str(mode_value[mode]))
			map['max_combo'] = bestplay['maxcombo']

		mods = (str(play.mod_combination).split(' ')[1])[:-3]
		mods_str, mods_emoj = get_mods(int(mods))
		date = str(compute_time(str(play.timestamp)))
		acc = str(compute_acc(str(play.misses), str(play.number_50s), str(play.katus), str(play.number_100s), str(play.gekis), str(play.number_300s), mode))
		rank = str(compute_rank(int(play.number_300s), int(play.gekis), int(play.number_100s), int(play.katus), int(play.number_50s), int(play.misses), float(acc), str(mods_str), mode))
		score = "'".join(str(play.score)[::-1][i:i+3] for i in range(0, len(str(play.score)), 3))[::-1]
		if mode == 'std': # calc.map(URL, MODS, ACC, COMBO, MISS)
			playerPP = calc.map('osu.ppy.sh/b/'+map['beatmap_id'], mods_str, float(acc)*100, int(play.max_combo), int(play.misses))
			mapPP = calc.map('osu.ppy.sh/b/'+map['beatmap_id'], mods_str, 100, int(map['max_combo']), 0)
		if mode == 'mania': # mania_pp.pp(STARS, ACCURACY, NB_NOTE, SCORE, OD, MODS)
			playerPP = mania_pp.pp(float(map['difficultyrating']), float(acc)*100, int(map['count_normal'])+int(map['count_slider']), int(play.score), float(map['diff_overall']), mods_str)
			mapPP = mania_pp.pp(float(map['difficultyrating']), 100, int(map['count_normal'])+int(map['count_slider']), 1000000, float(map['diff_overall']), mods_str)
		if mode == 'ctb': # ctb_pp.pp(STARS, ACCURACY, MAX_COMBO, PLAYER_COMBO, MISS, AR, MODS)
			playerPP = ctb_pp.pp(float(map['difficultyrating']), float(acc)*100, int(map['max_combo']), int(play.max_combo), int(play.misses), float(map['diff_approach']), mods_str)
			mapPP = ctb_pp.pp(float(map['difficultyrating']), 100, int(map['max_combo']), int(map['max_combo']), 0, float(map['diff_approach']), mods_str)
		if mode == 'taiko': # taiko_pp.pp(STARS, ACCURACY, MAX_COMBO, MISS, OD, MODS)
			playerPP = taiko_pp.pp(float(map['difficultyrating']), float(acc)*100, int(map['max_combo']), int(play.misses), float(map['diff_overall']), mods_str)
			mapPP = taiko_pp.pp(float(map['difficultyrating']), 100, int(map['max_combo']), 0, float(map['diff_overall']), mods_str)
		if acc == '1.0':
			acc = '100%'
		else:
			acc = acc[2:][:2]+','+acc[4:][:2]+'%'

		embedz = discord.Embed(title=str(map['title'])+" ["+str(map['version'])+"]", url='https://osu.ppy.sh/b/'+str(map['beatmap_id']), color=0x42f442)
		embedz.set_author(name=f"Play [{mode}] par {str(play.player_name)} :", icon_url='https://a.ppy.sh/'+str(user['user_id'])+'_api.jpg')
		embedz.set_thumbnail(url="https://b.ppy.sh/thumb/"+str(map['beatmapset_id'])+"l.jpg")
		
		descN = f"{emojis[str(rank).lower()]}   {str(score)}   ({acc})   {str(play.timestamp)[:-7]}"
		desc = f"{playerPP}pp/{mapPP}pp   {play.max_combo}x/{map['max_combo']}x    [ {play.number_300s} / {play.number_100s} / {play.number_50s} / {play.misses} ]"
		graph = compute_graph(play.life_bar_graph)

		embedz.add_field(name=descN, value=desc, inline=True)
		embedz.add_field(name='Life Graph', value='```'+graph+'```', inline=True)
		embedz.set_footer(text=signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')
		return embedz
	except Exception as e:
		print('error in embed parsed file')
		print(e)
		return -1


async def get_top_play(map_id, mode):
	async with aiohttp.ClientSession() as session:
		async with session.get(f'https://osu.ppy.sh/api/get_scores?k={key}&b={map_id}&m={mode}&limit=1') as r:
			vari.stats['api_usage'] += 1
			raw_r = await r.text()
			if len(raw_r) > 4:
				try:
					jr = json.loads(raw_r)
				except Exception as e:
					print("error in get top "+reversed_mode_value[mode])
					print(e)
					return -1
				return jr[0]
	return -1

	
async def get_map(map_id, mode):
	async with aiohttp.ClientSession() as session:
		async with session.get(f'https://osu.ppy.sh/api/get_beatmaps?k={key}&b={map_id}&m={mode}') as r:
			vari.stats['api_usage'] += 1
			raw_r = await r.text()
			if len(raw_r) > 4:
				try:
					jr = json.loads(raw_r)
				except Exception as e:
					print("in get_map"+reversed_mode_value[mode])
					print(e)
					return -1
				return jr[0]
	return -1	

async def get_map_hash(hash_map):
	async with aiohttp.ClientSession() as session:
		async with session.get(f'https://osu.ppy.sh/api/get_beatmaps?k={key}&h={str(hash_map)}') as r:
			vari.stats['api_usage'] += 1
			raw_r = await r.text()
			if len(raw_r) > 4:
				try:
					jr = json.loads(raw_r)
				except Exception as e:
					print('in get_map_hash')
					print(e)
					return -1
				return jr[0]
	return -1

def pass_value(passcount, playcount):
	try:
		if int(passcount) != 0 and int(playcount) != 0:
			passvalue = str(float(int(passcount) / int(playcount) * 100))
		else:
			passvalue = '0'
	except Exception as e:
		print('error calculate % pass')
		print(e)
	return passvalue
	
def get_mods(number):
	try:
		mod_list = ['NF', 'EZ', 'NV', 'HD', 'HR', 'SD', 'DT', 'RX', 'HT', 'NC', 'FL', 'AutoPlay', 'SO', 'AP', 'PF', '4K', '5K', '6K', '7K', '8K', 'KM', 'FI', 'RanD', 'LM', 'FM', '9K', '10K', '1K', '3K', '2K']
		if number <= 0:
			return '0', '∅'
		bin_list = [int(x) for x in bin(number)[2:]]
		i=0
		mod_str = ''
		mod_emoj = ''
		for y in reversed(bin_list):
			if y == 1 and mod_list[i] != 'NC':
				mod_str += mod_list[i]
				mod_emoj += emojis[str(mod_list[i]).lower()]
			i+=1
	except Exception as e:
		print('[!ERROR!] in get_mods:')
		print(e)
		return '0', '!N/A!'
	return mod_str, mod_emoj

def compute_time(todate):
	try:
		h = int(todate[11:][:2])
		h = h+1
		day = str(todate[:10])
		min = str(todate[14:])
		date = day+' '+str(h)+':'+min
	except Exception as e:
		print('error in date calc')
		print(e)
		return -1
	return date


def compute_graph(data):
	a = (str(data)[:-1]).split(',')
	if len(a) >= 35: mult = (len(a)-35)/len(a) 
	else: mult = (35-len(a))/35
	j = 0
	life = []
	for i in range(len(a)):
		if len(a) >= 35: 
			j += mult
			if j < 1:
				l = str(a[i]).split('|')[1]
				life.append(l)
			else: j -= 1
		else:
			l = str(a[i]).split('|')[1]
			life.append(l)
			j += mult
			if j > 1:
				life.append(l)
				j -= 1

	if len(life) == 35: k = 35
	elif len(life) > 35: k = 36
	else: k = len(life)
	graph = ''
	for i in range(1, 6):
		for j in range(0, k):
			n = float(life[j])
			if n >= 1-i*0.2: graph += '█'
			else: graph += ' '
		graph += '\n'

	return graph[:-1]	


def compute_rank(c300, cgeki, c100, ckatu, c50, c0, acc, mods, mode):
	if mode == 'std':
		cgeki = 0
		ckatu = 0
	tot = c300 + cgeki + c100 + ckatu + c50 + c0

	if mode == 'mania':
		c300 += cgeki
		c100 += ckatu
	if mode == 'ctb':
		c300 += c50
		c0 += ckatu
	if mode == 'taiko':
		c50 = 0

	if acc*100 == 1: rank = 'X'
	elif c300 > 0.9*tot and c50 < 0.01*tot and c0 == 0: rank = 'S'
	elif (c300 > 0.8*tot and c0 == 0) or (c300 > 0.9*tot): rank = 'A'
	elif (c300 > 0.7*tot and c0 == 0) or (c300 > 0.8*tot): rank = 'B'
	elif c300 > 0.6*tot: rank= 'C'
	else: rank = 'D'

	if 'HD' in mods or 'FL' in mods:
		if rank == 'SS': rank = 'XH'
		if rank == 'S': rank = 'SH'

	return rank


# mania : 50 = bad (50) / 100 = good (100) / miss = miss (0) / katu = great (200) / geki = excellent (max) / 300 = excellent (300)
def compute_acc(cmiss, c50, ckatu, c100, cgeki, c300, mode):
	try:
		if mode == 'std':
			acc = str(float((int(c50)*50 + int(c100)*100 + int(c300)*300) / ((int(cmiss)+int(c50)+int(c100)+int(c300))*300)))
		elif mode == 'ctb':
			acc = str(float((int(c50) + int(c100) + int(c300)) / (int(cmiss) + int(ckatu) + int(c50) + int(c100) + int(c300))))
		elif mode == 'mania':
			acc = str(float((int(c50)*50+int(c100)*100+int(ckatu)*200+(int(c300)+int(cgeki))*300)/((int(cmiss)+int(c50)+int(c100)+int(ckatu)+int(c300)+int(cgeki))*300)))
		elif mode == 'taiko':
			acc = str(float((0.5 * int(c100) + int(c300)) / (int(cmiss) + int(c100) + int(c300))))
	except Exception as e:
		print('[!ERROR!] in compute_acc_'+mode+':')
		print(e)
		return 'unkwn'
	return acc	
	
	
async def get_user_info(user, mode, limit=5):
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(f'https://osu.ppy.sh/api/get_user?k={key}&m={str(mode_value[mode])}&u={str(user).lower()}') as r:
				vari.stats['api_usage'] += 1
				raw_r = await r.text()
				if len(raw_r) > 4:
					jr = json.loads(raw_r)
				
			async with session.get(f'https://osu.ppy.sh/api/get_user_best?k={key}&m={str(mode_value[mode])}&u={str(user).lower()}&limit={str(limit)}') as r:
				vari.stats['api_usage'] += 1
				raw_p = await r.text()
				if len(raw_p) > 4:
					jp = json.loads(raw_p)
				
			return jr[0], jp
	except Exception as e:
		print("in get_user_info_"+mode+":")
		print(e)
		return -1
	return -1
	
async def embed_user_info(user, mode, plays):
	# ----- Compute color and create embed obj ----- #
	try:
		try:
			ret = await botutils.dl_image('https://a.ppy.sh/'+str(user['user_id'])+'_api.jpg', str(user['user_id'])+'.jpg', 'u')
			if ret == -1:
				raise NameError('Fail dl')
			chex = botutils.av_color('data/u/'+str(user['user_id'])+'.jpg')
			if chex == -1:
				raise NameError('Fail color calc')
			embed=discord.Embed(title="https://osu.ppy.sh/u/"+str(user['user_id']), url='https://osu.ppy.sh/u/'+str(user['user_id']), color=chex)
		except Exception as e:
			print('In embed user info')
			print(e)
			embed=discord.Embed(title="https://osu.ppy.sh/u/"+str(user['user_id']), url='https://osu.ppy.sh/u/'+str(user['user_id']))
		embed.set_author(name='Profil de '+str(user['username'])+' :')
		embed.set_thumbnail(url='https://a.ppy.sh/'+str(user['user_id'])+'_api.jpg')
		# ----- Try digit sep World wide rank ----- #
		try:
			wwr = "'".join(str(user['pp_rank'])[::-1][i:i+3] for i in range(0, len(str(user['pp_rank'])), 3))[::-1]
			embed.add_field(name="World Wide Rank", value="#"+wwr, inline=True)
		except Exception as e:
			print('[!Error!] in wwr digit separation')
			print(e)
			embed.add_field(name="World Wide Rank", value="#"+str(user['pp_rank']), inline=True)
		embed.add_field(name="Raw pp", value=str(user['pp_raw']), inline=True)
		# ----- Try digit sep Country rank ----- #
		try:
			cr = "'".join(str(user['pp_country_rank'])[::-1][i:i+3] for i in range(0, len(str(user['pp_country_rank'])), 3))[::-1]
			embed.add_field(name="Country Rank", value="#"+cr+' '+botutils.flag(str(user['country']).upper()), inline=True)
		except Exception as e:
			print('[!Error!] in cr digit separation')
			print(e)
			embed.add_field(name="Country Rank", value="#"+str(user['pp_country_rank'])+' '+botutils.flag(str(user['country'])), inline=True)
		embed.add_field(name="Level", value=str(user['level'])[:5], inline=True)
		# ----- Try digit sep Playcount ------ #
		try:
			playcount = " ".join(str(user['playcount'])[::-1][i:i+3] for i in range(0, len(str(user['playcount'])), 3))[::-1]
			embed.add_field(name="Play count", value=str(playcount), inline=True)
		except Exception as e:
			print('[!Error!] in playcount digit separation')
			print(e)
			embed.add_field(name="Play count", value=str(user['playcount']), inline=True)
		embed.add_field(name="Accuracy", value=str(user['accuracy'])[:5]+" %", inline=True)
		
		topplays = ''
		for i in range(len(plays)):
			map = await get_map(str(plays[i]['beatmap_id']), str(mode_value[mode]))
			if map == -1:
				map = await get_map(str(plays[i]['beatmap_id']), str(mode_value[mode])+'&a=1')

			acc = str(compute_acc(str(plays[i]['countmiss']), str(plays[i]['count50']), str(plays[i]['countkatu']), str(plays[i]['count100']), str(plays[i]['countgeki']), str(plays[i]['count300']), mode))
			if acc != '1.0':
				acc = acc[2:][:2]+','+acc[4:][:2]+'%'
			else:
				acc = '100%'
			mods_str, mods_emoj = get_mods(int(plays[i]['enabled_mods']))
			if float(plays[i]['pp']) - float(int(float(plays[i]['pp']))) >= 0.5:
				pp = int(float(plays[i]['pp']))+1
			else:
				pp = int(float(plays[i]['pp']))

			topplays += f">**{str(pp)}pp** {emojis[str(plays[i]['rank']).lower()]} {str(map['title'])} ({str(map['difficultyrating'])[:4]}☆) {str(mods_emoj)} {acc}\n"
		
		embed.add_field(name="Tops plays", value=topplays, inline= True)
		embed.set_footer(text = signature, icon_url='https://raw.githubusercontent.com/ppy/osu-resources/51f2b9b37f38cd349a3dd728a78f8fffcb3a54f5/osu.Game.Resources/Textures/Menu/logo.png')
		return embed
	except Exception as e:
		print('[!ERROR!] in embed_user_info:')
		print(e)
		return -1
