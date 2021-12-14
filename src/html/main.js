// Websocket connection
var function_is_running = false;
var PORT = 7307;

// $(document).ready(connect_to_socket);

function connect_to_socket() {
    if (function_is_running) return;

    console.log("Trying to connect...");
    function_is_running = true;
    let socket = new WebSocket(`ws://localhost:${PORT}`);
    socket.onopen = function (e) {
        console.log("CONNECTED");
    };
    socket.onmessage = function (event) {
        let data = JSON.parse(event.data);
        console.log(`New event: ${event.data}`);
        parse_message(data);
    };

    socket.onclose = function (event) {
        if (event.wasClean) console.log('CLEAN EXIT: ' + event);
        else console.log('UNCLEAN EXIT: ' + event);
        reconnect_to_socket();
    };

    socket.onerror = function (error) {
        console.log('ERROR: ' + error);
        reconnect_to_socket()
    };
}

function reconnect_to_socket() {
    console.log('Reconnecting..')
    function_is_running = false;
    setTimeout(function () {
        connect_to_socket();
    }, 500);
}

// Overlay functionality
var team_colors = [[74, 255, 2, 0.35], [3, 179, 255, 0.35], [255, 0, 0, 0.35]];
var custom_func = null;

function parse_message(data) {
    if (data.type == "color")
        team_colors = data.data;
    else if (data.type == "player_data")
        update_player_data(data.data)
}

function update_player_data(data) {
    $("#map").text(data.map);
    let team_data = { 1: "", 2: "" };
    for (const i in data.players) {
        p = data.players[i];
        // Decide where to place flag 
        let flag = `<td rowspan="2"><img src="../img/flags/${p.civ}.webp"></td>`;
        let t1f = '';
        let t2f = '';
        if (p.team == 1) t1f = flag; else t2f = flag;
        // Create player element
        let s = `<tr class="player">${t1f}<td colspan="5" class="name">${p.name}</td>${t2f}</tr>
        <tr class="stats"><td class="rank">${p.rank}</td><td class="rating">${p.rating}</td>
        <td class="winrate">${p.winrate}</td><td class="wins">${p.wins}</td><td class="losses">${p.losses}</td></tr>`;
        if ([1, 2].includes(p.team))
            team_data[p.team] += s;
    }
    $("#team1").html(team_data[1]);
    $("#team2").html(team_data[2]);
    if (custom_func != null) custom_func(data)
}


// DEBUG
var data = {
    "map": "Nagari",
    "mode": 20,
    "started": 1639442492,
    "ranked": false,
    "server": "westus2",
    "version": "9369",
    "match_id": "15433500",
    "players": [
        {
            "civ": "Chinese",
            "name": "Valhalla",
            "team": 2,
            "rating": "1241",
            "rank": "#2879",
            "wins": "69",
            "losses": "60",
            "winrate": "53.5%"
        },
        {
            "civ": "Chinese",
            "name": "Maguro",
            "team": 2,
            "rating": "1147",
            "rank": "#7926",
            "wins": "15",
            "losses": "11",
            "winrate": "57.7%"
        },
        {
            "civ": "French",
            "name": "naru001138",
            "team": 2,
            "rating": "1243",
            "rank": "#2822",
            "wins": "55",
            "losses": "40",
            "winrate": "57.9%"
        },
        {
            "civ": "Chinese",
            "name": "Salmon Sushi",
            "team": 2,
            "rating": "1194",
            "rank": "#4775",
            "wins": "90",
            "losses": "85",
            "winrate": "51.4%"
        },
        {
            "civ": "French",
            "name": "[FR]-Tristou-",
            "team": 1,
            "rating": "1374",
            "rank": "#642",
            "wins": "41",
            "losses": "30",
            "winrate": "57.7%"
        },
        {
            "civ": "Mongols",
            "name": "Mars Rigisamus",
            "team": 1,
            "rating": "1288",
            "rank": "#1711",
            "wins": "14",
            "losses": "6",
            "winrate": "70.0%"
        },
        {
            "civ": "Abbasid Dynasty",
            "name": "Rhaokin",
            "team": 1,
            "rating": "1129",
            "rank": "#9395",
            "wins": "19",
            "losses": "15",
            "winrate": "55.9%"
        },
        {
            "civ": "Holy Roman Empire",
            "name": "Sarelthil",
            "team": 1,
            "rating": "1213",
            "rank": "#3901",
            "wins": "23",
            "losses": "15",
            "winrate": "60.5%"
        }
    ]
}
update_player_data(data)