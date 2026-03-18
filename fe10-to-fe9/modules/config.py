# import os
import sys
from pathlib import Path

MOTIONS_ALL_9 = ('atk1', 'crit', 'damage', 'dead', 'escape', 'event', 'magic1','move2', 'ready',
                 'rod', 'tackle', 'trans', 'move', 'wait', 'wait', 'atk2', 'magic2')
MOTIONS_10_TO_9 = ('atk', 'arc', 'damage', 'dead', 'avoid', 'evt1', 'mag', 'walk', 'poise',
                   'rod', 'tack', 'trans', 'move', 'wait', 'twait', 'atk', 'mag')

MOTIONS_10_EVT = ('evt2', 'evt3', 'evt4', 'evt5', 'evt6', 'evt7', 'evt8',
                  'evt9', 'evt10', 'evt11', 'evt12')

MOTIONS_ALL_10 = ('wait', 'move', 'twait', 'walk', 'atk', 'atk2', 'mag', 'mag2', 'crit',
                  'atku', 'atk2u', 'magu', 'mag2u', 'critu', 'atkd', 'atk2d', 'magd',
                  'mag2d', 'critd', 'arc', 'arc2', 'arc3', 'arc4', 'arc5', 'rod', 'tack',
                  'avoid', 'poise', 'guard', 'damage', 'trans', 'dead', 'up', 'down', 'flip',
                  'flip2', 'evt1', 'evt2', 'evt3', 'evt4', 'evt5', 'evt6', 'evt7', 'evt8',
                  'evt9', 'evt10', 'evt11', 'evt12')
WP_ALL_STRINGS = ('N', 'SW', 'SP', 'JA', 'AX', 'HA', 'BW', 'RD', 'BG')

ANIM_DATA_DICT = {}
ANIM_DATA_DICT_HEX = {}
ANIM_PATHS = []
DEST_FILES = []
MODEL = ''
MODELS = []
OTHER_PATHS = []
SRC_FILES = []
STANDARD_SRC_FILES = []


# config.reset()        return None
def reset():
    """Reset mutable global values
    Note: index slice must be updated if new global values are added after STANDARD_SRC_FILES
    """
    global_keys = list(globals())
    first_idx = global_keys.index('ANIM_DATA_DICT')
    last_idx = global_keys.index('STANDARD_SRC_FILES') + 1
    global_keys =  global_keys[first_idx:last_idx]
    # global_values = list(globals().values())[first_idx:last_idx]

    for key in global_keys:
        if type(globals()[key]) == list:
            globals()[key] = []
        elif type(globals()[key]) == set:
            globals()[key] = {}
        elif type(globals()[key]) == str and globals()[key] != 'Unassigned Value':
            globals()[key] = ''
        elif type(globals()[key]) == int:
            globals()[key] = -1
        elif type(globals()[key]) == bool:
            globals()[key] = False
        else:
            globals()[key] = 'Unassigned Value'


# resource_path.reset(relative_path)        return os.path.join(base_path, relative_path)
def resource_path(relative_path):
    """ Redirect referenced paths
    Redirects the paths of external files referenced by this script.
    Wrap all filenames with the function resource_path()

    Modified to use pathlib instead of os.
        os version from https://stackoverflow.com/questions/31836104

    :param relative_path: Path
    :return: os.path.join(base_path, relative_path): Path
    """
    try:
        base_path = sys._MEIPASS2
    except Exception:
        # base_path = os.path.abspath(".")
        base_path = Path(".")
        base_path = base_path.resolve()

    # return os.path.join(base_path, relative_path)
    return base_path.joinpath(relative_path)
