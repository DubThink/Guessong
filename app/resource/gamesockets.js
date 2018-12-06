$(document).ready(function() {
    console.log("in gamesockets.js");
    var namespace = '/';
    var username = ""
    var room = ""
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    socket.on('connect', function() {
        console.log("connected")
        urldata = urlData()
        username = urldata["name"];
        room = urldata["room"];
        if(urldata["create"] == "True"){
            socket.emit('create_lobby', {name: username})
        }
        else {
            socket.emit('join_lobby', {name: username, room: room})
            $('#room_code').text("Room Code: " + room);
        }
    });
    socket.on('chat_message', function(msg) {
        $('#chat_output').append( msg["username"] + ":" + msg["message"] + "<br/>");
    });
    socket.on('room_code', function(msg) {
        $('#room_code').text("Room Code: " + msg["room"]);
    });
    socket.on('join_message', function(msg) {
        $('#chat_output').text("ATTENTION " + msg);
    });
    $('button#join').click(function(event) {
        socket.emit('join_lobby', {name: $('#name').val(), room: $('#room_name').val()});
        return false;
    });
    $('button#create_lobby').click(function(event) {
        socket.emit('create_lobby', {name: $('#name').val()});
        return false;
    });
    $('button#chat_submit').click(function(event) {
        socket.emit('chat_message', {username: username, message: $('#chat_input').val(), room: room});
        return false;
    });
    $('button#start').click(function(event) {
        socket.emit('start_game', {
            username: username, 
            room_name: $('#room_name').val(),
            playlist: $('#playlist').val(),
            room_type: $("input[name='room_type']:checked").val(),
            song_length: $('#song_length').val()
        });
    });
    $('button#guess_button').click(function(event) {
        socket.emit('song_guess', {username: username, guess: $('#guess_box').val() });
    });
});

function urlData() {
    var url = window.location.href;
    var spliturl = url.substr(url.indexOf("game/") + 5).split(":");
    return { create : spliturl[0],
            name : spliturl[1],
            room : spliturl[2]};
}

