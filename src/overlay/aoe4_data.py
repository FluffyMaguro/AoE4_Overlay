"""
Ids used by 
https://aoeiv.net/#api


# Mode type            leaderboard_id
# Quick Match (1v1)	    17
# Quick Match (2v2)	    18
# Quick Match (3v3)	    19
# Quick Match (4v4)	    20

"""

mode_data = {
    17: "1v1",
    18: "2v2",
    19: "3v3",
    20: "4v4",
}
"""aoe4.net leaderboard index to mode name"""

QM_ids = {17, 18, 19, 20}
"""Leaderboard ids of quick match leagues"""

civ_data = {
    0: 'Abbasid Dynasty',
    1: 'Chinese',
    2: 'Delhi Sultanate',
    3: 'English',
    4: 'French',
    5: 'Holy Roman Empire',
    6: 'Mongols',
    7: 'Rus',
    8: 'Ottomans',
    9: 'Malians',
    10: 'Ayyubids', # Later added for randomization. Indexes not accurate.
    11: 'Byzantines',
    12: 'Japanese',
    13: 'Jeanne Darc',
    14: 'Order Of The Dragon',
    15: 'Zhu Xis Legacy',
}

map_data = {
    -1: 'Unknown Map',
    0: 'Dry Arabia',
    1: 'Lipany',
    2: 'High View',
    3: 'Mountain Pass',
    4: 'Ancient Spires',
    5: 'Danube River',
    6: 'Black Forest',
    7: 'Mongolian Heights',
    8: 'Altai',
    9: 'Confluence',
    10: 'French Pass',
    11: 'Hill and Dale',
    12: 'King of The Hill',
    13: 'Warring Islands',
    14: 'Archipelago',
    15: 'Nagari',
    16: 'Boulder Bay',
    17: 'Mega Random'
}
"""aoe4.net map index to map name"""
