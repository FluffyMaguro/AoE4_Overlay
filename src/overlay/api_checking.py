import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from overlay.logging_func import get_logger
from overlay.settings import settings

import threading

logger = get_logger(__name__)
session = requests.session()


def close_session():
    """ Closes the requests session """
    session.close()


def find_player(text: str) -> bool:
    """ Tries to find a player based on a text containing either name, steam_id or profile_id
    Returns `True` if the player was found. Settings are automatically updated."""

    # Save the current player settings
    old = (settings.player_name, settings.profile_id, settings.steam_id)

    # First try if it's a profile id
    try:
        url = f"https://aoe4world.com/api/v0/players/{text}"
        resp = json.loads(session.get(url, timeout=10).text)
        if 'name' in resp:
            settings.profile_id = resp['profile_id']
            settings.player_name = resp['name']
            settings.steam_id = resp.get('steam_id')
            logger.info(
                f"Found player by profile_id: {settings.player_name} ({settings.profile_id})"
            )
            return True
    except json.decoder.JSONDecodeError:
        ...
    except Exception:
        logger.exception("")

    # Then try query
    try:
        url = f"https://aoe4world.com/api/v0/players/search?query={text}"
        resp = json.loads(session.get(url, timeout=10).text)
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


# Not used anymore
def get_rating_history(leaderboard_id: int, amount: int = 1) -> List[Any]:
    """ Gets player match history"""
    if settings.steam_id:
        url = f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&steam_id={settings.steam_id}&count={amount}"
    elif settings.profile_id:
        url = f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&profile_id={settings.profile_id}&count={amount}"
    else:
        return []

    resp = session.get(url, timeout=10).text
    try:
        return json.loads(resp)
    except:
        logger.warning(f"Failed to parse rating history: {resp}")
        return []


# Not used anymore
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

    resp = session.get(url, timeout=10).text
    try:
        return json.loads(resp)
    except:
        logger.warning(f"Failed to parse leaderboard data: {resp}")
        return {}


def get_full_match_history(amount: int) -> Optional[List[Any]]:
    """ Gets match history and adds some data its missing"""

    url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/games?limit={amount}"
    try:
        resp = session.get(url, timeout=10).text
        data = json.loads(resp)
        return data['games']
    except Exception:
        logger.exception("")
        return None


class Api_checker:

    def __init__(self):
        self.stop_event = threading.Event()
        self.force_check_event = threading.Event()
        self.last_match_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.last_rating_timestamp = datetime(1900, 1, 1, 0, 0, 0)

    def reset(self):
        """ Resets last timestamps"""
        self.last_match_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.last_rating_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.force_check_event.set()

    def sleep(self, seconds: int) -> bool:
        """ Sleeps while checking for stop_event
        Returns `True` if we need to stop the parent function"""
        if self.stop_event.is_set():
            return True
        
        # Wait for either stop_event or force_check_event, or timeout
        # We need to wait for 'seconds', but can be interrupted by force_check
        if self.force_check_event.is_set():
            self.force_check_event.clear()
            return False

        # We wait on force_check_event because if it gets set, we want to wake up immediately
        # But if stop_event gets set, we also want to know.
        # Since we can only wait on one event at a time easily without complex logic,
        # and force_check implies "stop sleeping and check now", we wait on that.
        # We should also check stop_event periodically or use a composite wait if possible,
        # but here we can just wait on force_check_event with a timeout.
        
        start_time = time.time()
        while time.time() - start_time < seconds:
            remaining = seconds - (time.time() - start_time)
            if remaining <= 0:
                break
            
            if self.stop_event.is_set():
                return True
            
            # Wait for force_check or a small slice to check stop_event again
            # Using a small slice (e.g. 0.5s) mimics the old behavior but cleaner
            # OR we can wait on force_check_event for 'remaining' but then we 
            # won't catch stop_event until it triggers or timeout. 
            # Ideally we'd wait on both.
            # Simpler approach: wait on force_check_event with timeout of min(remaining, 0.5)
            
            wait_time = min(remaining, 0.5)
            if self.force_check_event.wait(timeout=wait_time):
                self.force_check_event.clear()
                return False
                
        return self.stop_event.is_set()

    def check_for_new_game(self,
                           delayed_seconds: int = 0
                           ) -> Optional[Dict[str, Any]]:
        """ Continously check if there are a new game being played
        Returns match data if there is a new game"""

        if self.sleep(delayed_seconds):
            return

        while not self.stop_event.is_set():
            result = self.get_data()
            if result is not None:
                return result

            if self.sleep(settings.interval):
                return

    def get_data(self) -> Optional[Dict[str, Any]]:
        if self.stop_event.is_set():
            return

        # Get last match from aoe4world.com
        try:
            url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/games/last"
            resp = session.get(url, timeout=10)
            data = json.loads(resp.text)
        except Exception:
            logger.exception("")
            return

        if self.stop_event.is_set():
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

    @property
    def force_stop(self):
        return self.stop_event.is_set()

    @force_stop.setter
    def force_stop(self, value):
        if value:
            self.stop_event.set()
        else:
            self.stop_event.clear()
