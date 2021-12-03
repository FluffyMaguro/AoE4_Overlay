""""
Using 
https://aoeiv.net/#api

"""

import json
import time
from typing import Any, Dict, Optional

import requests

from overlay.logging_func import get_logger
from overlay.settings import settings

logger = get_logger(__name__)
session = requests.session()


def validate_id(id: Optional[int], idtype: str = "steam") -> bool:
    """ Validates whether given ID corresponds to some player.
    Assumes that a player has played some matches"""
    if id is None:
        return False
    url = f"https://aoeiv.net/api/player/matches?game=aoe4&{idtype}_id={id}&count=1"
    return session.get(url).text != "[]"


def find_player_by_name(name: str) -> bool:
    """ Looks for a player by name. If found return `True`.
    Updates settings automatically"""
    for id in range(17, 21):
        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={id}&search={name}&start=1&count=1"
        data = json.loads(session.get(url).text)
        if data['leaderboard'] and name == data['leaderboard'][0]['name']:
            settings.profile_id = data['leaderboard'][0]['profile_id']
            settings.steam_id = data['leaderboard'][0]['steam_id']
            return True
    return False


def find_player(text: str) -> bool:
    """ Tries to find a player based on a text containing either name, steam_id or profile_id
    Returns `True` if the player was found. Settings are automatically updated."""
    id = None
    try:
        id = int(text)
    except Exception:
        # Probably a name
        if find_player_by_name(text):
            logger.info("Found player by name")
            return True

    if id is not None:
        if validate_id(id, idtype="steam"):
            settings.steam_id = id
            logger.info("Found player by steam_id: {id}")
            return True
        if validate_id(id, idtype="profile"):
            settings.profile_id = id
            logger.info("Found player by profile_id: {id}")
            return True
    logger.info(f"Failed to find a player with: {text}")
    return False


class API_checker:
    def __init__(self):
        self.steam_id: Optional[int] = None
        self.profile_id: Optional[int] = None
        self.force_stop = False

    def sleep(self, seconds: int) -> bool:
        """ Sleeps while checking for force_stop
        Returns `True` if we need to stop the parent function"""
        for _ in range(seconds * 2):
            if self.force_stop:
                return True
            time.sleep(0.5)
        return False

    def check_for_new_game(self,
                           delayed_seconds: int = 0
                           ) -> Optional[Dict[str, Any]]:
        """ Continously check if there are a new game being played
        Returns match data if there is a new game"""

        if self.sleep(delayed_seconds):
            return

        while True:
            result = self.get_data()
            if result is not None:
                return result

            if self.sleep(10):
                return

    def get_data(self) -> Optional[Dict[str, Any]]:
        """ Returns match data if there is a new game"""
        if self.force_stop:
            return

        # Match history
        if self.steam_id:
            url = f"https://aoeiv.net/api/player/matches?game=aoe4&steam_id={self.steam_id}&count=1"
        elif self.profile_id:
            url = f"https://aoeiv.net/api/player/matches?game=aoe4&profile_id={self.profile_id}&count=1"
        else:
            return

        resp = session.get(url).text
        try:
            match = json.loads(resp)[0]
        except Exception:
            logger.exception(f"Failed to parse match history: {resp}")
            return

        # Calculate which rating to check based on the number of players:
        # Match type            leaderboard_id
        # Quick Match (1v1)	    17
        # Quick Match (2v2)	    18
        # Quick Match (3v3)	    19
        # Quick Match (4v4)	    20
        leaderboard_id = int(16 + match['num_players'] / 2)

        if self.force_stop:
            return

        # Rating history
        if self.steam_id:
            f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&steam_id={self.steam_id}&count=1"
        elif self.profile_id:
            f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&profile_id={self.profile_id}&count=1"
        else:
            return

        resp = session.get(url).text
        try:
            rating = json.loads(resp)[0]
        except:
            logger.exception(f"Failed to parse rating: {resp}")
            return

        # Gets additional player data from leaderboards stats (in-place)
        for player in match['players']:
            self.get_player_data(leaderboard_id, player)

        return match  # Delete later
        if match['started'] > rating['timestamp']:
            return match

    def get_player_data(self, leaderboard_id: int, player_dict: Dict[str,
                                                                     Any]):
        """ Updates player data inplace"""

        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={leaderboard_id}&profile_id={player_dict['profile_id']}&start=1&count=1"
        data = json.loads(session.get(url).text)
        if not data['leaderboard']:
            return  # not yet ranked player
        data = data["leaderboard"][0]
        player_dict['rating'] = data["rating"]
        player_dict['wins'] = data["wins"]
        player_dict['losses'] = data["losses"]
        player_dict['rank'] = data["rank"]
        player_dict['streak'] = data["streak"]
