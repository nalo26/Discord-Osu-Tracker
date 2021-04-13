import json
import datetime
import time
import pytz
from urllib.request import urlopen
from PIL import ImageFile

MODES_VAL = {"std": 0, "taiko": 1, "ctb": 2, "mania": 3}
MODES_IND = ['std', 'taiko', 'ctb', 'mania']

def read_txt(path) -> str:
    with open(path, 'r') as mf:
        content = mf.read()
    mf.close()
    return content

def write_txt(path, content) -> None:
    with open(path, 'w') as mf:
        mf.write(content)
    mf.close()

def read_json(path) -> dict:
    with open(path, 'r') as mf:
        content = json.load(mf)
    mf.close()
    return content

def write_json(path, content) -> None:
    with open(path, 'w') as mf:
        json.dump(content, mf, indent=4)
    mf.close()


from osu import get_player_info
from osu import get_user_best

def is_admin(user_id) -> bool:
    return (str(user_id) in read_txt('ADMINS'))

def add_admin(user_id) -> None:
    content = read_txt('ADMINS')
    write_txt('ADMINS', f"{content}\n{user_id}")

def already_tracked(user_id, mode) -> bool:
    data = read_json('PLAYERS.json')
    for gm in data:
        if gm == mode and user_id in data[gm]: return True
    return False

def add_user(user, mode, channel) -> None:
    data = read_json('PLAYERS.json')
    player = user['user_id']
    try: raw_player = data[mode][player]
    except KeyError: raw_player = {}
    raw_player['name'] = user['username']
    raw_player['rank'] = int(user['pp_rank'])
    raw_player['pp'] = float(user['pp_raw'])
    raw_player['acc'] = float(user['accuracy'])
    raw_player['channel'] = channel
    raw_player['plays'] = get_user_best(player, mode)
    data[mode][player] = raw_player
    write_json('PLAYERS.json', data)

def update_players() -> None:
    data = read_json('PLAYERS.json')
    for mode in data:
        for player in data[mode]:
            user = get_player_info(player, mode)
            data[mode][player]['name'] = user['username']
            data[mode][player]['rank'] = int(user['pp_rank'])
            data[mode][player]['pp'] = float(user['pp_raw'])
            data[mode][player]['acc'] = float(user['accuracy'])
    write_json('PLAYERS.json', data)

def delete_user(user_id, mode) -> None:
    data = read_json('PLAYERS.json')
    del data[mode][user_id]
    write_json('PLAYERS.json', data)

def get_user(user_id, mode) -> dict:
    data = read_json('PLAYERS.json')
    return data[mode][user_id]

def flag(code) -> str:
    OFFSET = ord('🇦') - ord('A')
    if not code: return u''
    points = list(map(lambda x: ord(x) + OFFSET, code.upper()))
    try: return chr(points[0]) + chr(points[1])
    except ValueError: return ('\\U%08x\\U%08x' % tuple(points)).decode('unicode-escape')

def parse_date(seconds) -> str:
    date = datetime.timedelta(seconds=seconds)
    hours = time.strftime('%Hh %Mm', time.gmtime(int(date.seconds)))
    return f"{date.days}d {hours}"

def compute_time(dt) -> str:
    tz_UTC = pytz.timezone('UTC')
    tz_FR = pytz.timezone('Europe/Paris')

    try: dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S") #osu
    except ValueError: dt = datetime.datetime.strptime(dt[:-5], "%Y-%m-%dT%H:%M:%S") #quaver
    dt = tz_UTC.localize(dt)
    dt = dt.astimezone(tz_FR)
    # dt = dt.strftime("%d/%m/%Y %H:%M:%S")

    return dt

def avg_color(uri) -> list:
    file = urlopen(uri)
    p = ImageFile.Parser()
    while True:
        data = file.read(1024)
        if not data: break
        p.feed(data)

    file.close()
    colors = [0, 0, 0]

    im = p.close()
    width, height = im.size
    size = 0
    for x in range(width):
        for y in range(height):
            v = im.getpixel((x, y))
            if len(v) < 4 or (len(v) >= 4 and v[3] == 255):
                size += 1
                colors = [colors[i]+v[i] for i in range(3)]

    return [int(c / size) for c in colors]