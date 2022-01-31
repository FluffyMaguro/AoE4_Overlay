import json
import os
import pathlib
import sys
import time
from typing import Any, Dict, Optional, Union

import requests
from PyQt5 import QtCore

from overlay.aoe4_data import QM_ids, civ_data, map_data
from overlay.logging_func import get_logger
from overlay.settings import settings

logger = get_logger(__name__)
ROOT = pathlib.Path(sys.argv[0]).parent.absolute()


def zeroed(value: Optional[int]) -> int:
    """ Returns `value` after replacing `None` with 0"""
    return value if value is not None else 0


def pyqt_wait(miliseconds: int):
    """ Pause executing for `time` in miliseconds"""
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(miliseconds, loop.quit)
    loop.exec_()


def is_compiled() -> bool:
    """ Checks whether the app is compiled by Nuitka"""
    return '__compiled__' in globals()


def file_path(file: str) -> str:
    """ Returns the path to the main directory regardless of the current working directory """
    return os.path.normpath(os.path.join(ROOT, file))


def version_to_int(version: str):
    """Convets `1.0.1` to an integer """
    return sum([
        int(i) * (1000**idx) for idx, i in enumerate(version.split('.')[::-1])
    ])


def version_check(version: str) -> str:
    """ Checks version. Returns either link for the new version or an empty string. """
    try:
        url = "https://raw.githubusercontent.com/FluffyMaguro/AoE4_Overlay/main/version.json"
        data = json.loads(requests.get(url).text)
        if version_to_int(version) < version_to_int(data['version']):
            return data['link']
    except Exception:
        logger.warning("Failed to check for a new version")
    return ""


def create_custom_files():
    """ Creates custom.css and custom.js files if they don't exist"""
    for file_name in ("custom.css", "custom.js"):
        path = file_path(f"html/{file_name}")
        if not os.path.isfile(path):
            with open(path, "w") as f:
                f.write("")


def match_mode(match: Dict[str, Any], convert_customs: bool = True) -> int:
    """ Returns match mode (e.g., 17 for both QM 1v1)
    
    Returns the same value for Custom 1v1 if `convert_customs` == True
    """
    leaderboard_id = match['rating_type_id'] + 2
    if convert_customs and leaderboard_id not in QM_ids:
        leaderboard_id = 16 + match['num_slots'] / 2
    return int(leaderboard_id)


def quickmatch_game(match: Dict[str, Any]) -> bool:
    """ Checks whether the game is a quickmatch"""
    return match_mode(match, convert_customs=False) in QM_ids


def process_game(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """ Processes game data returned by API
    
    Sorts players to main is at the top. Calculates winrates. 
    Gets text for civs and maps. Apart from `team`, all player data returned as string."""
    result = {}
    result['map'] = map_data.get(game_data["map_type"], "Unknown map")
    result['mode'] = match_mode(game_data)
    result['started'] = game_data['started']
    result['ranked'] = game_data['ranked']
    result['server'] = game_data['server']
    result['version'] = game_data['version']
    result['match_id'] = game_data['match_id']

    # Sort players so the main player team is first
    team = None
    for player in game_data['players']:
        if player['profile_id'] == settings.profile_id:
            team = player['team']
            break
    if team is not None:

        def sortingf(player: Dict[str, Any]) -> int:
            if player['team'] == team:
                return -1
            return player['team']

        game_data['players'] = sorted(game_data['players'], key=sortingf)

    # Add player data
    result['players'] = []
    for player in game_data['players']:
        wins = zeroed(player.get('wins'))
        losses = zeroed(player.get('losses'))
        games = wins + losses
        winrate = wins / games if games else 0
        civ_win_median = ''
        if 'civ_win_length_median' in player:
            civ_win_median = time.strftime(
                "%M:%S", time.gmtime(player['civ_win_length_median']))
        civ_winrate = ''
        if 'civ_winrate' in player:
            civ_winrate = f"{player['civ_winrate']/100:.1%}"

        data = {
            'civ': civ_data.get(player['civ'], "Unknown civ"),
            'name': player['name'],
            'team': zeroed(player['team']),
            'rating': str(player.get('rating', '')),
            'rank': f"#{player.get('rank', '')}",
            'wins': str(wins) if wins else '',
            'losses': str(losses) if losses else '',
            'winrate': f"{winrate:.1%}",
            'civ_games': str(player.get('civ_games', '')),
            'civ_winrate': civ_winrate,
            'civ_win_length_median': civ_win_median
        }
        result['players'].append(data)

    return result


def strtime(t: Union[int, float], show_seconds: bool = False) -> str:
    """ Returns formatted string 
    X days, Y hours, Z minutes
    """
    years, delta = divmod(t, 31557600)
    days, delta = divmod(delta, 86400)
    hours, delta = divmod(delta, 3600)
    minutes, seconds = divmod(delta, 60)

    s = []
    if years:
        s.append(f"{years:.0f} years")
    if days:
        s.append(f"{days:.0f} days")
    if hours:
        s.append(f"{hours:.0f} hours")
    if minutes or (not show_seconds and not s):
        s.append(f"{minutes:.0f} minutes")
    if show_seconds:
        s.append(f"{seconds:.0f} seconds")
    return " ".join(s)
