import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

from overlay.aoe4_data import QM_ids
from overlay.helper_func import match_mode
from overlay.logging_func import get_logger
from overlay.settings import settings

logger = get_logger(__name__)
session = requests.session()


def find_player(text: str) -> bool:
    """ Tries to find a player based on a text containing either name, steam_id or profile_id
    Returns `True` if the player was found. Settings are automatically updated."""

    # Save the current player settings
    old = (settings.player_name, settings.profile_id, settings.steam_id)

    # First try if it's a profile id
    try:
        url = f"https://aoe4world.com/api/v0/players/{text}"
        resp = json.loads(session.get(url).text)
        if 'name' in resp:
            settings.profile_id = resp['profile_id']
            settings.player_name = resp['name']
            settings.steam_id = resp.get('steam_id')
            logger.info(
                f"Found player by profile_id: {settings.player_name} ({settings.profile_id})"
            )
            return True
    except Exception:
        logger.exception("")

    # Then try query
    try:
        url = f"https://aoe4world.com/api/v0/players/search?query={text}"
        resp = json.loads(session.get(url).text)
        if resp['players']:
            settings.profile_id = resp['players'][0]['profile_id']
            settings.player_name = resp['players'][0]['name']
            settings.steam_id = resp['players'][0].get('steam_id')
            logger.info(
                f"Found player by query: {settings.player_name} ({settings.profile_id})"
            )
            return True
    except Exception:
        logger.exception("")

    logger.info(f"Failed to find a player with: {text}")
    settings.player_name, settings.profile_id, settings.steam_id = old
    return False


def get_match_history(amount: int = 1,
                      raise_exception: bool = False) -> List[Any]:
    """ Gets player match history"""
    if settings.steam_id:
        url = f"https://aoeiv.net/api/player/matches?game=aoe4&steam_id={settings.steam_id}&count={amount}"
    elif settings.profile_id:
        url = f"https://aoeiv.net/api/player/matches?game=aoe4&profile_id={settings.profile_id}&count={amount}"
    else:
        return []

    resp = session.get(url).text
    try:
        return json.loads(resp)
    except Exception:
        logger.warning(f"Failed to parse match history\n{resp}")
        if raise_exception:
            raise Exception
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
        return json.loads(resp)
    except:
        logger.warning(f"Failed to parse rating history: {resp}")
        return []


def get_leaderboard_data(leaderboard_id: int) -> Dict[str, Any]:
    """ Gets leaderboard data for the main player"""
    if settings.steam_id:
        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={leaderboard_id}&steam_id={settings.steam_id}&count=1"
    elif settings.profile_id:
        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={leaderboard_id}&profile_id={settings.profile_id}&count=1"
    elif settings.player_name:
        url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={leaderboard_id}&search={settings.player_name}&count=1"
    else:
        return {}

    resp = session.get(url).text
    try:
        return json.loads(resp)
    except:
        logger.warning(f"Failed to parse leaderboard data: {resp}")
        return {}


def get_full_match_history(amount: int) -> Optional[List[Any]]:
    """ Gets match history and adds some data its missing"""
    # Get player match history
    try:
        data = get_match_history(amount=amount, raise_exception=True)
    except Exception:
        return None

    # Make sure data is sorted by date
    data = sorted(data, key=lambda x: x['started'], reverse=True)

    logger.info(
        f"Asked for {amount} games | obtained {len(data)} from get_match_history"
    )
    # What type of games are there
    leaderboard_ids = {match_mode(i, convert_customs=False) for i in data}
    leaderboard_ids = {i for i in leaderboard_ids if i in QM_ids}

    # Get rating histories for those modes
    rating_hist = {
        i: get_rating_history(i, amount + 1)
        for i in leaderboard_ids
    }

    def find_rating_change(leaderboard_id: int,
                           timestamp: int) -> Tuple[Optional[int], int]:
        """ Finds a rating change for given match"""
        # If not quick match
        if leaderboard_id not in QM_ids:
            return None, -1

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
        rating_diff, rating = find_rating_change(
            match_mode(match, convert_customs=False), match['started'])
        match["my_rating"] = rating
        if rating_diff is None:
            match['result'] = "?"
            match['my_rating_diff'] = "?"
        elif rating_diff == 0:
            match['result'] = "?"
            match['my_rating_diff'] = 0
        else:
            match['result'] = "Win" if rating_diff > 0 else "Loss"
            match['my_rating_diff'] = rating_diff

    return data


class Api_checker:

    def __init__(self):
        self.force_stop = False
        self.last_match_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.last_rating_timestamp = datetime(1900, 1, 1, 0, 0, 0)

    def reset(self):
        """ Resets last timestamps"""
        self.last_match_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.last_rating_timestamp = datetime(1900, 1, 1, 0, 0, 0)

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

            if self.sleep(settings.interval):
                return

    def get_data(self) -> Optional[Dict[str, Any]]:
        if self.force_stop:
            return

        # Get last match from aoe4world.com
        try:
            url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/games/last"
            resp = session.get(url)
            data = json.loads(resp.text)
        except Exception:
            logger.exception("")
            return

        if self.force_stop:
            return
        if "error" in data:
            return

        # Calc old leaderboard id
        data['leaderboard_id'] = 0
        try:
            data['leaderboard_id'] = int(data['kind'][-1]) + 16
        except Exception:
            logger.exception("")

        # Calc started time
        started = datetime.strptime(data['started_at'],
                                    "%Y-%m-%dT%H:%M:%S.000Z")
        data['started_sec'] = started.timestamp()

        # Show the last game
        if started > self.last_match_timestamp:  # and data['ongoing']:
            self.last_match_timestamp = started
            return data

        if not "qm_" in data['kind']:
            return

        # When a game finished
        if started > self.last_rating_timestamp and not data['ongoing']:

            # Check for new ratings
            if not data['leaderboard_id']:
                return

            rating_history = get_rating_history(data['leaderboard_id'],
                                                amount=1)

            if not rating_history:
                return

            self.last_rating_timestamp = started
            rating = rating_history[0]
            return {"new_rating": True, 'timestamp': rating['timestamp']}
