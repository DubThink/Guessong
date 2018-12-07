$(document).ready(function() {
    console.log("in gamesockets.js");
    var namespace = '/';
    var username = "";
    var room = "";
    var game_started = false;
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    //var audio = $("#audio");
        //$("#audio_src").attr("src", 'https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/AudioPreview118/v4/ea/82/07/ea8207c8-d2ab-1d08-4658-13b8df263bd5/mzaf_2704060614543532885.plus.aac.p.m4a');
        var audio_player = document.createElement("audio");
        //audio_player.src="http://funksyou.com/fileDownload/Songs/0/30828.mp3";
        //audio_player.src="https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/AudioPreview118/v4/ea/82/07/ea8207c8-d2ab-1d08-4658-13b8df263bd5/mzaf_2704060614543532885.plus.aac.p.m4a";
        audio_player.volume=0.10;
        audio_player.autoPlay=false;
        audio_player.preLoad=true;

    socket.on('connect', function() {
        console.log("connected");
        urldata = urlData();
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
    socket.on('redirect', function(event){
        window.stop();
        console.log("hello from redirect");
        //$(document.getElementById('#centered').innerHTML = 'hello from redirect';
    });
    socket.on('chat_message', function(msg) {
        $('#chat_output').append( msg["username"] + ":" + msg["message"] + "<br/>");
    });
    socket.on('room_code', function(msg) {
        $('#room_code').append("Room Code: " + msg["room"]);
        room = msg["room"];
    });
    socket.on('join_message', function(msg) {
        $('#chat_output').append("ATTENTION " + msg);
    });
    socket.on('game_started', function(msg) {
       game_started = true;
       setInterval(requestGameData, 500);
    });
    socket.on('update_game', function(msg) {
        console.log(msg["link"]);
        if(audio_player.src != msg["link"]) {
            audio_player.src = msg["link"];
            audio_player.load();
            audio_player.play();
        }
    });
    socket.on('guess_result', function(msg){
        $('#chat_output').text("GUESS RESULT: " + msg);
    });
    $('button#chat_submit').click(function(event) {
        console.log(username + ", " + room);
        socket.emit('chat_message', {username: username, message: $('#chat_input').val(), room: room});
        return false;
    });
    $('button#start').click(function(event) {
        socket.emit('start_game', {
            username: username,
            room: room,
            room_name: $('#room_name').val(),
            playlist: $('#playlist').val(),
            room_type: $("input[name='room_type']:checked").val(),
            song_length: $('#song_length').val()
        });
    });
    $('button#guess_button').click(function(event) {
        socket.emit('song_guess', {username: username, room: room, guess: $('#guess_box').val() });
    });
    function requestGameData(){
        socket.emit("data_request", {username: username, room: room});
    }
});

function urlData() {
    var url = window.location.href;
    var spliturl = url.substr(url.indexOf("game/") + 5).split(":");
    return { create : spliturl[0],
            name : spliturl[1],
            room : spliturl[2]};
}



