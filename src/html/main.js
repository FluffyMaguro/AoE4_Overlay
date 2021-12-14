var function_is_running = false;
var PORT = 7307;

$(document).ready(connect_to_socket);

function connect_to_socket() {
    if (function_is_running) return;

    console.log("Trying to connect...");
    function_is_running = true;
    let socket = new WebSocket("ws://localhost:" + PORT);
    socket.onopen = function (e) {
        console.log("OPENED");
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

var team_colors = [[74, 255, 2, 0.35], [3, 179, 255, 0.35], [255, 0, 0, 0.35]];

function reconnect_to_socket(message) {
    console.log('Reconnecting..')
    function_is_running = false;
    setTimeout(function () {
        connect_to_socket();
    }, 500);
}

function parse_message(data) {
    if (data.type == "color") {
        team_colors = data.data;
        console.log("Updated colors")
    } else if (data.type == "player_data") {
        console.log("players");
        update_player_data(data.data)
    }
}


function update_player_data(data) {
    console.log("addting data", data)
}

// DEBUG
var data = {"type": "override", "data": {"map": "Altai ", "players": [["REEEEEEEEEEEEEEEEEEEEEEE", "1703", "#67", "65.5%", "76", "40", "Chinese", 1], ["Armeria", "1635", "#119", "53.4%", "347", "303", "Abbasid Dynasty", 2], ["", "", "", "", "", "", "", 0], ["", "", "", "", "", "", "", 0], ["", "", "", "", "", "", "", 0], ["", "", "", "", "", "", "", 0], ["", "", "", "", "", "", "", 0], ["", "", "", "", "", "", "", 0]]}}
update_player_data(data.data)