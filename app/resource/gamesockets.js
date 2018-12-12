$(document).ready(function() {
    console.log("in gamesockets.js");
    var namespace = '/';
    var username = "";
    var room = "";
    var game_started = false;
    var round_over = false;
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var thumb_url = "";
    var playlists;
    var audio_player = document.createElement("audio");
    audio_player.volume=0.10;
    audio_player.autoPlay=false;
    audio_player.preLoad=false;
    var users;
    var is_creator = false;
    var played_songs = Array();

    // I added this, put it where you want it -B
    // resize the thumb/record-disc to be square
    function resizeThumb() {
        console.log("test");
        document.getElementById('thumb').style.height = document.getElementById('thumb').width + '';
    }
    window.onresize = resizeThumb;
    document.getElementById('thumb').style.height=document.getElementById('thumb').width+'';

    // update slider value text
    document.getElementById('song_length').oninput=function(){
        document.getElementById("time_value").innerText=document.getElementById('song_length').value;
    };

    $("#song_info").hide();
    socket.on('connect', function() {
        console.log("connected");
        urldata = urlData();
        username = urldata["name"];
        username = decodeURIComponent(username);
        room = urldata["room"];
        if(urldata["create"] == "True"){
            socket.emit('create_lobby', {name: username})
            is_creator = true;
            $("#game_col").hide();
        }
        else {
            socket.emit('join_lobby', {name: username, room: room})
            $('.room_code').val("Room Code: " + room);
            $('#create_col').hide();
            $('.table').hide();
        }
    });
    socket.on('redirect', function(event){
        window.location.replace("/index/" + event["error_type"]);
    });

    socket.on('chat_message', function(msg) {
        $('#chat_output').append( msg["username"] + ":" + msg["message"] + "\n");
    });
    socket.on('room_code', function(msg) {
        console.log(msg["room"]);
        $('.room_code').val(msg["room"]);
        room = msg["room"];
    });
    socket.on('join_message', function(msg) {
        $('#chat_output').append("ATTENTION " + msg + "\n");
    });
    socket.on('game_started', function(msg) {
       game_started = true;
       $('#create_col').hide();
       $('#game_col').show();
       $('.table').show();
       setInterval(request_game_data, 500);
    });
    socket.on('update_game', function(msg) {
        console.log(msg["name"]);
        if(audio_player.src != msg["song"]["preview_url"]) {
            audio_player.src = msg["song"]["preview_url"];
            audio_player.load();
            audio_player.play();
            round_over = false;
            $('#thumb').attr("src", "/resource/placeholder.png");
            $('#thumb').removeClass("stopspin");
            $("#song_info").hide();
        }
        thumb_url = msg["song"]["thumbnail_url"];
        users=msg["users"];
        update_scoreboard();
    });
    socket.on('round_end', function(msg) {
        if(!round_over) {
            audio_player.pause();
            played_songs[played_songs.length] = {name: msg["name"],
                thumb: thumb_url,
                link: msg["external_url"]};
            console.log(played_songs);
            $('#thumb').attr("src", thumb_url);
            $('#thumb').show();
            update_song_list();
            $('#thumb').addClass("stopspin");

            $("#song_info").show();
            $("h3#song_name").text(msg["name"]);
            $("h3#song_artist").text(msg["artist"]);
            $("h3#album").text(msg["album"]);
        }
       round_over = true;
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
        $('#chat_output').append(who + " guess was " + msg["result"] + "!\n");
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
        $('#score_body').empty();
        for (let user of users) {
            $('#score_body').append( $("<tr><th scope=\"row\">" + user["name"] + "</th><td>" + user["score"] + "</td></tr>"));
        }
    }
    function update_song_list(){
        $('#history_body').empty();
        var length = played_songs.length < 3 ? played_songs.length : 3;
        for(var count = 0; count < length; count++) {
            song = played_songs[played_songs.length - count - 1];
            $('#history_body').append( $("<tr><th scope=\"row\"><img class=\"history_thumb\" src=\"" +
                song["thumb"] + "\"/></th><td>" +
                song["name"] + "<br/><a target=\"_blank\" href=\"" +
                song["link"] + "\">Get on iTunes</a></td></tr>"));
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
