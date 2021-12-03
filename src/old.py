"""
Using 
https://aoeiv.net/#nightbot
https://aoeiv.net/#api

Not the best way since nightbot returns a formatted string mainly intended to be used for 1v1.
And #api doesn't return the current match as far as I know.

"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from pprint import pprint


def is_english(s):
    try:
        s.encode(encoding="utf-8").decode("ascii")
    except UnicodeDecodeError:
        return False
    else:
        return True


class MatchType(Enum):
    t1v1 = 17
    t2v2 = 18
    t3v3 = 19
    t4v4 = 20


@dataclass
class Player:
    name: str = ""
    current_civ: str = ""
    profile_id: int = -1
    steam_id: int = -1

    # Dictionary containing stats for various game modes
    stats: Dict[MatchType, Dict[str, int]] = field(default_factory=dict)

    def __eq__(self, other):
        return (self.profile_id == other.profile_id and self.profile_id != -1) or (self.steam_id == other.steam_id and self.steam_id != -1)

    def check_for_last_character(self) -> bool:
        """Checks if there as a decoding error adding a letter to the end.
        Removes it and returns True if there might have been one."""
        if not is_english(self.name[-2]) and is_english(self.name[-1]):
            self.name = self.name[:-1]
            return True
        return False

    def get_data(self, match_type: MatchType, session: requests.Session):
        """ Pulls player data from API and updates the player"""
        if self.profile_id != -1:
            url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={match_type.value}&profile_id={self.profile_id}&start=1&count=1"
        elif self.steam_id != -1:
            url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={match_type.value}&steam_id={self.steam_id}&start=1&count=1"
        else:
            url = f"https://aoeiv.net/api/leaderboard?game=aoe4&leaderboard_id={match_type.value}&search={self.name}&start=1&count=1"

        data = json.loads(requests.get(url).text)

        # What if there is no data
        if not data["leaderboard"]:
            if self.profile_id != -1 and self.steam_id != -1:
                return  # Cant do anything about that
            # Try fixing the name if it was decoded incorrectly
            removed = self.check_for_last_character()
            if removed:
                print("Removed char")
                self.get_data(match_type, session)
            return  # Nothing anyway

        data = data["leaderboard"][0]

        self.name = data['name']
        self.profile_id = data["profile_id"]
        self.steam_id = data["steam_id"]

        self.stats[match_type] = dict()
        self.stats[match_type]['elo'] = data["rating"]
        self.stats[match_type]['wins'] = data["wins"]
        self.stats[match_type]['losses'] = data["losses"]
        self.stats[match_type]['rank'] = data["rank"]
        self.stats[match_type]['streak'] = data["streak"]




class GameChecking:
    def __init__(self, steam_id: int):
        self.session = requests.session()
        self.current_data = {"map": "", "players": set()}

        self.me = Player()
        self.me.steam_id = steam_id
        self.me.get_data(MatchType.t4v4, self.session)

        # self.overlay = AoEOverlay()
        # self.overlay.show()

    def check_for_team_games(self):
        """ Continously check if there are a new game being played"""
        while True:
            self.get_team_data()
            time.sleep(10)
            print('...')

    def get_team_data(self):
        """ """
        url = f"https://aoeiv.net/api/nightbot/match?game=aoe4&profile_id={self.me.profile_id}&civflag=true"
        splt = self.session.get(url).text.split(" playing on ")
        map_name = splt[1]
        players = []
        splt = splt[0].replace(" -VS- ", " + ").split(" + ")
        for item in splt:
            faction = [i for i in item.split(" ") if "grub" in i][0]
            name = item.replace(faction, "")
            faction = faction.replace("grub", "")
            if "(" in name and ")" in name:
                elo = name[name.index("(") + 1:name.index(")")]
                name = name.replace(f"({elo})", "")
            name = name.strip()

            if name == self.me.name:
                self.me.current_civ = faction
                players.append(self.me)
            else:
                player = Player(name, faction)
                players.append(player)

        # Check if this data are new
        player_names = {p.name for p in players}
        if self.current_data['map'] == map_name and self.current_data['players'] == player_names:
            return

        print("NEW DATA!")
        print(self.current_data['map'], "!=", map_name)
        print(self.current_data['players'], "!=", player_names)
        self.current_data['map'] = map_name
        self.current_data['players'] = player_names

        # for player in players:
        #     player.get_data(match_type, self.session)

        # print(f"Map: {map_name}")
        # pprint(players)

    def get_data(self):
        # Match history
        url = f"https://aoeiv.net/api/player/matches?game=aoe4&steam_id={self.me.steam_id}&count=1"
        resp = self.session.get(url).text
        print("MATCHES")
        try:
            match = json.loads(resp)[0]
        except:
            print("Failed to parse rating")
            print(resp)
            return

        leaderboard_id = int(16 + match['num_players']/2) # 16 for 1v1 | 20 for 4v4
        pprint(match)

        # Rating history
        url = f"https://aoeiv.net/api/player/ratinghistory?game=aoe4&leaderboard_id={leaderboard_id}&steam_id={self.me.steam_id}&count=1"
        resp = self.session.get(url).text
        print("RATING 4v4")
        try:
            rating = json.loads(resp)[0]
        except:
            print("Failed to parse rating")
            print(resp)
            return

        if match['started'] > rating['timestamp']:
            print("new match....")
        else:
            print("old match....")


game_check = GameChecking(steam_id=76561198073723227)
game_check.get_data()

# game_check.check_for_team_games()

# p = Player('@Linear')
# p.get_data(MatchType.t3v3, requests.session())
# print(p)
