""""
Using 
https://aoeiv.net/#api

# Match type            leaderboard_id
# Quick Match (1v1)	    17
# Quick Match (2v2)	    18
# Quick Match (3v3)	    19
# Quick Match (4v4)	    20

rating_type_id in match history seem to be offset:
    leaderboard_id = rating_type_id + 2

"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from overlay.logging_func import get_logger
from overlay.settings import settings

logger = get_logger(__name__)
session = requests.session()


def validate_id(id: Optional[int],
                idtype: str = "steam",
                update_name: bool = False) -> bool:
    """ Validates whether given ID corresponds to some player.
    Assumes that a player has played some matches"""
    if id is None:
        return False
    url = f"https://aoeiv.net/api/player/matches?game=aoe4&{idtype}_id={id}&count=1"

    # When looking for profile we might want to find player name also
    text = session.get(url).text
    if text != "[]" and update_name and idtype == "profile":
        data = json.loads(text)
        for player in data[0]['players']:
            if player["profile_id"] == id:
                settings.player_name = player["name"]
                return True

    return text != "[]"


def find_player_by_name(name: str) -> bool:
    """ Looks for a player by name. If found return `True`.
    Updates settings automatically"""
    for id in range(17, 21):
        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={id}&search={name}&start=1&count=1"
        data = json.loads(session.get(url).text)
        if data['leaderboard'] and name == data['leaderboard'][0]['name']:
            settings.profile_id = data['leaderboard'][0]['profile_id']
            settings.steam_id = data['leaderboard'][0]['steam_id']
            settings.player_name = data['leaderboard'][0]['name']
            return True
    return False


def attempt_to_find_profile_id():
    """ Attempts to find player profile ID based on steam_id.
    Only works if the player is ranked any team mode."""
    if not settings.steam_id:
        return
    for id in range(17, 21):
        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={id}&steam_id={settings.steam_id}&start=1&count=1"
        data = json.loads(session.get(url).text)
        if data['leaderboard']:
            settings.profile_id = data['leaderboard'][0]['profile_id']
            settings.player_name = data['leaderboard'][0]['name']
            logger.info("Found player profile_id based on steam_id")
            return


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
            attempt_to_find_profile_id()
            return True
        if validate_id(id, idtype="profile", update_name=True):
            settings.profile_id = id
            logger.info("Found player by profile_id: {id}")
            return True
    logger.info(f"Failed to find a player with: {text}")
    return False


def get_match_history(amount: int = 1) -> List[Any]:
    """ Gets player match history"""
    if settings.steam_id:
        url = f"https://aoeiv.net/api/player/matches?game=aoe4&steam_id={settings.steam_id}&count={amount}"
    elif settings.profile_id:
        url = f"https://aoeiv.net/api/player/matches?game=aoe4&profile_id={settings.profile_id}&count={amount}"
    else:
        return []
    try:
        return json.loads(session.get(url).text)
    except Exception:
        logger.exception("Failed to parse match history")
        return []


def get_rating_history(leaderboard_id: int, amount: int = 1) -> List[Any]:
    """ Gets player match history"""
    if settings.steam_id:
        url = f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&steam_id={settings.steam_id}&count={amount}"
    elif settings.profile_id:
        url = f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&profile_id={settings.profile_id}&count={amount}"
    else:
        return []

    resp = session.get(url).text
    try:
        return json.loads(session.get(url).text)
    except:
        logger.exception(f"Failed to parse rating history: {resp}")
        return []


def get_full_match_history(amount: int = 100) -> List[Any]:
    """ Gets match history and adds some data its missing"""

    # Get player match history
    data = get_match_history(amount=amount)
    # What type of games are there
    leaderboard_ids = {i["rating_type_id"] + 2 for i in data}
    # Get rating histories for those modes
    rating_hist = {
        i: get_rating_history(i, amount + 1)
        for i in leaderboard_ids
    }

    def find_rating_change(leaderboard_id: int,
                           timestamp: int) -> Tuple[Optional[int], int]:
        """ Finds a rating change for given match"""
        # Go through rating histories, the first that's newer than our game has new rating
        reversed = rating_hist[leaderboard_id][::-1]
        for i, entry in enumerate(reversed):
            if entry['timestamp'] > timestamp:
                if i == 0:
                    return None, entry['rating']
                # Calculate rating difference compared to the previous game
                diff = entry['rating'] - reversed[i - 1]['rating']
                return diff, entry['rating']
        return None, -1

    for match in data:
        rating_diff, rating = find_rating_change(match["rating_type_id"] + 2,
                                                 match['started'])
        match["my_rating"] = rating
        if rating_diff is None:
            match['result'] = "?"
            match['my_rating_diff'] = "?"
        else:
            match['result'] = "Win" if rating_diff > 0 else "Loss"
            match['my_rating_diff'] = rating_diff

    return data


class API_checker:
    def __init__(self):
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
        match_history = get_match_history()
        if not match_history:
            return
        match = match_history[0]
        leaderboard_id = match['rating_type_id'] + 2

        if self.force_stop:
            return

        # Rating history
        rating_history = get_rating_history(leaderboard_id)
        if not rating_history:
            return
        rating = rating_history[0]

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
