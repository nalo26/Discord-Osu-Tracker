import json

def init():
	global stats

	with open('stats.json', 'r') as mf:
		stats = json.load(mf)