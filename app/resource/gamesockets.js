$(document).ready(function() {
    console.log("in gamesockets.js");
    namespace = '/';
    console.log(getUrlVars()["username"]);
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    socket.on('connect', function() {
        socket.emit('event', {data: 'Yoo hoo!'});
    });
    socket.on('reply', function(msg) {
       $("#output").text( msg["data"] );
       console.log(msg);
    });
    socket.on('chat_message', function(msg) {
        $('#chat_output').append( msg["username"] + ":" + msg["message"] + "<br/>");
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
        socket.emit('chat_message', {username: username, message: $('#chat_input').val()});
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

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}
