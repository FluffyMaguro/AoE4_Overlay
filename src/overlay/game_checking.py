""""
Using 
https://aoeiv.net/#api

"""

import json
import time
from typing import Any, Dict, Optional

import requests
from pprint import pprint
from overlay.logging_func import get_logger

logger = get_logger(__name__)
session = requests.session()


def validate_steam_id(steam_id: Optional[int]) -> bool:
    if steam_id is None:
        return False
    url = f"https://aoeiv.net/api/player/matches?game=aoe4&steam_id={steam_id}&count=1"
    return session.get(url).text != "[]"


class API_checker:
    def __init__(self):
        self.steam_id: Optional[int] = None
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
        if self.steam_id is None or self.force_stop:
            return

        # Match history
        url = f"https://aoeiv.net/api/player/matches?game=aoe4&steam_id={self.steam_id}&count=1"
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
        url = f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&steam_id={self.steam_id}&count=1"
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
