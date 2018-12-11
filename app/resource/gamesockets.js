$(document).ready(function() {
    console.log("in gamesockets.js");
    var namespace = '/';
    var username = "";
    var room = "";
    var game_started = false;
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var thumb_url = "";
    var playlists;
    var audio_player = document.createElement("audio");
    audio_player.volume=0.10;
    audio_player.autoPlay=false;
    audio_player.preLoad=false;
    var users;
    var is_creator = false;
    socket.on('connect', function() {
        console.log("connected");
        urldata = urlData();
        username = urldata["name"];
        username = decodeURIComponent(username);
        room = urldata["room"];
        if(urldata["create"] == "True"){
            socket.emit('create_lobby', {name: username})
            $('#guess_song').hide();
            is_creator = true;
        }
        else {
            socket.emit('join_lobby', {name: username, room: room})
            $('#room_code').text("Room Code: " + room);
            $('#guess_song').hide();
            $('#create_game').hide();
        }
    });
    socket.on('redirect', function(event){
        window.location.replace("/index/" + event["error_type"]);
    });

    socket.on('chat_message', function(msg) {
        $('#chat_output').append( msg["username"] + ":" + msg["message"] + "<br/>");
    });
    socket.on('room_code', function(msg) {
        $('#room_code').text("Room Code: " + msg["room"]);
        room = msg["room"];
    });
    socket.on('join_message', function(msg) {
        $('#chat_output').append("ATTENTION " + msg + "<br/>");
    });
    socket.on('game_started', function(msg) {
       game_started = true;
       $('#create_game').hide();
       setInterval(request_game_data, 500);
    });
    socket.on('update_game', function(msg) {
        if(audio_player.src != msg["song"]["preview_url"]) {
            audio_player.src = msg["song"]["preview_url"];
            audio_player.load();
            audio_player.play();
            $('#thumb').hide();
        }
        thumb_url = msg["song"]["thumbnail_url"];
        users=msg["users"];
        update_scoreboard();
    });
    socket.on('round_end', function(msg) {
       audio_player.pause();
       $('#thumb').attr("src", thumb_url);
       $('#thumb').show();
    });
    socket.on('game_end', function(msg) {
        if (is_creator){
            $('#create_game').show();
        }
        game_started = false;
    });
    socket.on('guess_result', function(msg){
        var who = ""
        console.log(msg);
        if(msg["username"] == username) {
            who = "Your"
            if (msg["result"] == "correct") {
                $('#thumb').attr("src", thumb_url);
                $('#thumb').show();
            }
        }
        else{
            who = msg["username"] + "\'s";
        }
        $('#chat_output').append(who + " guess was " + msg["result"] + "!<br/>");
    });
    socket.on('playlists', function(msg){
        playlists = msg;
        for (let playlist of playlists){
            $('#playlist').append("<option value=" + playlist["id"]+">"+playlist["name"]+"</option>");
        }
    });
    $('button#chat_submit').click(function(event) {
        console.log(username + ", " + room);
        socket.emit('chat_message', {username: username, message: $('#chat_input').val(), room: room});
        $('#chat_input').val('');
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
    $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      $("button#chat_submit").trigger("click");
      return false;
    }
  });
    function request_game_data(){
        socket.emit("data_request", {username: username, room: room});
    }
    function update_scoreboard(){
        $('div#scoreboard').empty();
        console.log(users);
        for (let user of users) {
            console.log(user);
            $('div#scoreboard').append( $("<div>" + user["name"] + ": " + user["score"] + "</div>"));
        }
    }
});

function urlData() {
    var url = window.location.href;
    var spliturl = url.substr(url.indexOf("game/") + 5).split(":");
    return { create : spliturl[0],
            name : spliturl[1],
            room : spliturl[2]};
}