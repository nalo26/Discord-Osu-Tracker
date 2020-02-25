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

def pp(STARS, ACCURACY, MAX_COMBO, MISS, OD, MODS):
    usercombo = MAX_COMBO - MISS
    if 'EZ' in MODS:
        OD /= 2
    
    if 'HR' in MODS:
        OD *= 1.4
    
    OD = max(min(OD, 10), 0)
    
    Max = 20
    Min = 50
    result = Min + (Max - Min) * OD / 10
    result = math.floor(result) - 0.5
    
    if 'HT' in MODS:
        result /= 0.75
    
    if 'DT' in MODS:
        result /= 1.5
    
    OD300 = round(result * 100) / 100
    
    hundreds = -1
    hundreds = round((1 - MISS/MAX_COMBO - ACCURACY/100)*2*MAX_COMBO)
    
    STARSValue = pow(max(1,STARS/0.0075) * 5 - 4,2)/100000
    LengthBonus = min(1,MAX_COMBO/1500) * 0.1 + 1
    STARSValue *= LengthBonus
    STARSValue *= pow(0.985,MISS)
    STARSValue *= min(pow(usercombo,0.5) / pow(MAX_COMBO,0.5),1)
    STARSValue *= ACCURACY/100
    ACCURACYValue = pow(150/OD300,1.1) * pow(ACCURACY/100,15) * 22
    ACCURACYValue *= min(pow(MAX_COMBO/1500,0.3),1.15)

    ModMultiplier = 1.10
    if 'HD' in MODS:
        ModMultiplier *= 1.10
        STARSValue *= 1.025
    
    if 'NF' in MODS:
        ModMultiplier *= 0.90
    
    if 'FL' in MODS:
        STARSValue *= 1.05 * LengthBonus
    
    TotalValue = pow(pow(STARSValue,1.1) + pow(ACCURACYValue,1.1),1.0/1.1) * ModMultiplier

    pp = round(TotalValue * 100) / 100
    return round(pp)
    # print(pp)

# https://mon.im/taikopp/