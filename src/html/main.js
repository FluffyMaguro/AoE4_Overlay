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
        player_message(data);
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

function reconnect_to_socket(message) {
    console.log('Reconnecting..')
    function_is_running = false;
    setTimeout(function () {
        connect_to_socket();
    }, 500);
}

// Different msg types: raw, override
function player_message(data) {
}