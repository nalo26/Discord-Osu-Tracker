import diff_calc
import requests
import pp_calc
import b_info

from beatmap import Beatmap
import utils
KEY = utils.read_txt('KEY')

def map(url, mod_l, acc, combo, c100, c50, miss):
	if acc == 100: acc = 0
	file_name = url

	file = requests.get(b_info.main(file_name, KEY)).text.splitlines()

	map = Beatmap(file)
	if combo == 0 or combo > map.max_combo: combo = map.max_combo

	# mod_s = [mod_s[i:i+2] for i in range(0, len(mod_s), 2)]
	for m in mod_l:
		set_mods(mod, m)
		mod.update()
			
	map.apply_mods(mod)
	diff = diff_calc.main(map)
	if acc == 0: pp = pp_calc.pp_calc(diff[0], diff[1], diff[3], miss, c100, c50, mod, combo, 1)
	else: pp = pp_calc.pp_calc_acc(diff[0], diff[1], diff[3], acc, mod, combo, miss, 1)
	return str(int(pp.pp))

class mods:
	def __init__(self):
		self.nf = 0
		self.ez = 0
		self.hd = 0
		self.hr = 0
		self.dt = 0
		self.ht = 0
		self.nc = 0
		self.fl = 0
		self.so = 0
		self.td = 0
		self.speed_changing = self.dt | self.ht | self.nc
		self.map_changing = self.hr | self.ez | self.speed_changing
	def update(self):
		self.speed_changing = self.dt | self.ht | self.nc
		self.map_changing = self.hr | self.ez | self.speed_changing


mod = mods()

def set_mods(mod, m):
		if m == "NF": mod.nf = 1
		if m == "EZ": mod.ez = 1
		if m == "HD": mod.hd = 1
		if m == "HR": mod.hr = 1
		if m == "DT": mod.dt = 1
		if m == "HT": mod.ht = 1
		if m == "NC": mod.nc = 1
		if m == "FL": mod.fl = 1
		if m == "SO": mod.so = 1
		if m == "TD": mod.td = 1
		if m == "NM":
			mod.nf = 0
			mod.ez = 0
			mod.hd = 0
			mod.hr = 0
			mod.dt = 0
			mod.ht = 0
			mod.nc = 0
			mod.fl = 0
			mod.so = 0
			mod.td = 0
