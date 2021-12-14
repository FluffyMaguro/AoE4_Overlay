// Websocket connection
var function_is_running = false;
var PORT = 7307;

$(document).ready(connect_to_socket);

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
    let first_team = null;
    let second_team = null;
    for (const i in data.players) {
        p = data.players[i];
        if (first_team == null) first_team = p.team;
        // Decide where to place flag 
        let flag = `<td class="flag" rowspan="2"><img src="../img/flags/${p.civ}.webp"></td>`;
        let t1f = '';
        let t2f = '';
        if (p.team == first_team) t1f = flag; else t2f = flag;
        // Create player element
        let s = `<tr class="player">${t1f}<td colspan="5" class="name">${p.name}</td>${t2f}</tr>
        <tr class="stats"><td class="rank">${p.rank}</td><td class="rating">${p.rating}</td>
        <td class="winrate">${p.winrate}</td><td class="wins">${p.wins}W</td><td class="losses">${p.losses}L</td></tr>`;
        if ([1, 2].includes(p.team))
            team_data[p.team] += s;
    }
    if (first_team == 1) second_team = 2; else second_team = 1;
    $("#team1").html(team_data[first_team]);
    $("#team2").html(team_data[second_team]);
    if (custom_func != null) custom_func(data)
}

