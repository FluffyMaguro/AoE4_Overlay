import sys
import os
import unittest
from unittest.mock import MagicMock, patch

import tempfile

# Mock PyQt5 and requests before importing overlay
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()
sys.modules['requests'] = MagicMock()

appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock

sys.modules['keyboard'] = MagicMock()

# Add src to path so we can import overlay
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.helper_func import zeroed, strtime, version_to_int, process_game
from overlay.settings import settings

class TestHelperFunc(unittest.TestCase):

    def test_zeroed(self):
        self.assertEqual(zeroed(None), 0)
        self.assertEqual(zeroed(10), 10)
        self.assertEqual(zeroed(0), 0)

    def test_strtime(self):
        # 3661 seconds = 1 hour, 1 minute, 1 second
        self.assertEqual(strtime(3661, show_seconds=True), "1 hours 1 minutes 1 seconds")
        self.assertEqual(strtime(3600), "1 hours")
        self.assertEqual(strtime(60), "1 minutes")
        self.assertEqual(strtime(30), "0 minutes") # Default behavior for small deltas

    def test_version_to_int(self):
        self.assertEqual(version_to_int("1.0.0"), 1000000)
        self.assertEqual(version_to_int("1.4.8"), 1004008)
        self.assertTrue(version_to_int("1.5.0") > version_to_int("1.4.9"))

    def test_process_game_basic(self):
        # Mock settings
        settings.profile_id = 12345
        
        # Sample game data from API structure
        game_data = {
            'map': 'Dry Arabia',
            'leaderboard_id': 17,
            'started_at': '2023-01-01T00:00:00.000Z',
            'server': 'ukwest',
            'game_id': 999,
            'kind': 'rm_1v1',
            'teams': [
                [ # Team 0
                    {
                        'profile_id': 12345,
                        'name': 'Hero',
                        'civilization': 'english',
                        'country': 'gb',
                        'modes': {
                            'rm_1v1': {
                                'rating': 1200,
                                'rank': 100,
                                'wins_count': 10,
                                'losses_count': 5,
                                'win_rate': 66.6,
                                'civilizations': []
                            }
                        }
                    }
                ],
                [ # Team 1
                    {
                        'profile_id': 67890,
                        'name': 'Villain',
                        'civilization': 'french',
                        'country': 'fr',
                        'modes': {
                            'rm_1v1': {
                                'rating': 1100,
                                'rank': 200,
                                'wins_count': 8,
                                'losses_count': 8,
                                'win_rate': 50.0,
                                'civilizations': []
                            }
                        }
                    }
                ]
            ]
        }

        result = process_game(game_data)
        
        self.assertEqual(result['map'], 'Dry Arabia')
        self.assertEqual(len(result['players']), 2)
        
        # Check main player is sorted first (index 0)
        self.assertEqual(result['players'][0]['name'], 'Hero')
        self.assertEqual(result['players'][0]['civ'], 'English')
        self.assertEqual(result['players'][0]['team'], 1) # 0-indexed team + 1
        
        # Check opponent
        self.assertEqual(result['players'][1]['name'], 'Villain')
        self.assertEqual(result['players'][1]['team'], 2)

if __name__ == '__main__':
    unittest.main()
