from utils import config_loader
config = config_loader.load()

from utils import lang
from utils import buy_api
from utils import database


def clean_id(id):
    return ('{}'+str(id)).format(''.join('0' for _ in range(4 - len(str(id)))))

def split_list(original_list):
    result = []
    list_length = len(original_list)
    num_sublists = list_length // 10

    for i in range(num_sublists):
        start_index = i * 10
        end_index = start_index + 10
        sublist = original_list[start_index:end_index]
        result.append(sublist)

    remaining_items = list_length % 10
    if remaining_items > 0:
        sublist = original_list[num_sublists * 10:]
        result.append(sublist)

    return result

def convertHMS(value):
    sec = int(value)  # convert value to number if it's a string
    hours = sec // 3600  # get hours
    minutes = (sec - (hours * 3600)) // 60  # get minutes
    seconds = sec - (hours * 3600) - (minutes * 60)  # get seconds
    if hours > 0:
        hours = str(hours) + 'hr '
    else:
        hours = ''
    if minutes > 0:
        minutes = str(minutes) + 'm '
    else:
        minutes = ''
    if seconds > 0:
        seconds = str(seconds) + 's'
    else:
        if hours == '' and minutes == '':
            seconds = str(seconds) + 's'
        else:
            seconds = ''
    return hours + minutes + seconds

def get_credits(user_id):
    db = database.Connection()
    res = db.query("credits", ["balance"], {'user': user_id}, False)
    db.close()
    if res:
        return int(res[-1][1])
    else:
        return 0