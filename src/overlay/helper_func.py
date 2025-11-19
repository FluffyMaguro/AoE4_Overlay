import json
import os
import pathlib
import sys
import time
import traceback
from typing import Any, Dict, Optional, Union

import requests
from PyQt6 import QtCore

from overlay.aoe4_data import QM_ids
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
    loop.exec()


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
    try:
        for file_name in ("custom.css", "custom.js"):
            path = file_path(f"html/{file_name}")
            if not os.path.isfile(path):
                with open(path, "w") as f:
                    f.write("")
    except Exception:
        logger.exception("Failed to create custom.css/js")


def match_mode(match: Dict[str, Any], convert_customs: bool = True) -> int:
    """ Returns match mode (e.g., 17 for both QM 1v1)
    
    Returns the same value for Custom 1v1 if `convert_customs` == True
    """
    leaderboard_id = match['rating_type_id'] + 2
    if convert_customs and leaderboard_id not in QM_ids:
        leaderboard_id = 16 + match['num_slots'] / 2
    return int(leaderboard_id)


def process_game(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """ Processes game data returned by API
    Sorts players to main is at the top. Calculates winrates. 
    Gets text for civs and maps. Apart from `team`, all player data returned as string."""
    result = {}
    result['map'] = game_data['map']
    result['mode'] = game_data['leaderboard_id']
    result['started'] = game_data['started_at']
    result['ranked'] = 'qm_' in game_data['kind'] or 'rm_' in game_data['kind']
    result['server'] = game_data['server']
    result['match_id'] = game_data['game_id']
    mode = game_data['kind']

    # aoe4world has a single rm_team rating that we'd like to use instead here
    # for team games
    if mode in ['rm_4v4', 'rm_3v3', 'rm_2v2']:
        mode = "rm_team"

    # Sort players so the main player team is first
    players = []
    main_team = None
    for idx, team in enumerate(game_data['teams']):
        for player in team:
            player['team'] = idx
            players.append(player)
            if player['profile_id'] == settings.profile_id:
                main_team = idx

    def sortingf(player: Dict[str, Any]) -> int:
        if player['team'] is None:
            return 99
        if player['team'] == main_team:
            return -1
        return player['team']

    players = sorted(players, key=sortingf)

    # Add player data
    result['players'] = []
    for player in players:
        # Avoid overwriting mode when falling back to QM/RM on a specific player
        lookup_mode = mode
        current_civ = player['civilization']
        name = player['name'] if player['name'] is not None else "?"

        civ_games = ""
        civ_winrate = ""
        civ_win_median = ""
        try:
            if not lookup_mode in player['modes']:
                if 'rm_' in lookup_mode:
                    lookup_mode = lookup_mode.replace('rm_', 'qm_')
                elif 'qm_' in lookup_mode:
                    lookup_mode = lookup_mode.replace('qm_', 'rm_')
            if 'civilizations' in player['modes'][lookup_mode]:
                for civ in player['modes'][lookup_mode]['civilizations']:
                    if civ['civilization'] == current_civ:
                        civ_games = str(civ['games_count'])
                        civ_winrate = f"{civ['win_rate']/100:.1%}"
                        med = civ['game_length']['wins_median']
                        civ_win_median = time.strftime("%M:%S",
                                                       time.gmtime(med))
        except Exception:
            print(traceback.format_exc())

        mode_data = player.get('modes', {}).get(lookup_mode, {})
        mode_str = lookup_mode.split('_')[0].upper()
        data = {
            'civ': current_civ.replace("_", " ").title(),
            'name': name,
            'team': zeroed(player['team'] + 1),
            'country': player['country'],
            'rating': str(mode_data.get('rating', 0)),
            'rank': f"{mode_str}#{mode_data.get('rank',0)}",
            'wins': str(mode_data.get('wins_count', 0)),
            'losses': str(mode_data.get('losses_count', 0)),
            'winrate': f"{mode_data.get('win_rate', 0)}%",
            'civ_games': civ_games,
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
