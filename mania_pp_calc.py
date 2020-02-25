import math
def max(val1, val2):
	if val1 >= val2:
		return val1
	else:
		return val2
def min(val1, val2):
	if val1 < val2:
		return val1
	else:
		return val2

def pp(STARS, ACCURACY, NB_NOTE, SCORE, OD, MODS):
	if 'EZ' in MODS:
		OD /= 2

	OD = max(min(OD, 10), 0)

	Max = 20
	Min = 50
	result = Min + (Max - Min) * OD / 10
	result = math.floor(result) - 0.5

	win = round(result * 100) / 100

	acc_value = pow((150/win)*pow(ACCURACY/100, 16), 1.8)*2.5*min(1.15, pow(NB_NOTE/1500, 0.3))
	StrainBase = (pow(5*max(1,STARS/0.0825)-4,3)/110000)*(1+0.1*min(1, NB_NOTE/1500))
	if SCORE<500000:
		StrainMult = SCORE/500000*0.1
	elif SCORE<600000:
		StrainMult = (SCORE-500000)/100000*0.2+0.1
	elif SCORE<700000:
		StrainMult = (SCORE-600000)/100000*0.35+0.3
	elif SCORE<800000:
		StrainMult = (SCORE-700000)/100000*0.2+0.65
	elif SCORE<900000:
		StrainMult = (SCORE-800000)/100000*0.1+0.85
	else:
		StrainMult = (SCORE-900000)/100000*0.05+0.95
	pp = round(pow(pow(acc_value, 1.1)+pow(StrainBase*StrainMult, 1.1), 1/1.1)*1.1)
	# print(pp)
	return pp


# http://maniapp.uy.to/