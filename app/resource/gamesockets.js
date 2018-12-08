$(document).ready(function() {
    console.log("in gamesockets.js");
    var namespace = '/';
    var username = "";
    var room = "";
    var game_started = false;
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    var thumb_url = "";
    //var audio = $("#audio");
        //$("#audio_src").attr("src", 'https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/AudioPreview118/v4/ea/82/07/ea8207c8-d2ab-1d08-4658-13b8df263bd5/mzaf_2704060614543532885.plus.aac.p.m4a');
        var audio_player = document.createElement("audio");
        //audio_player.src="http://funksyou.com/fileDownload/Songs/0/30828.mp3";
        //audio_player.src="https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/AudioPreview118/v4/ea/82/07/ea8207c8-d2ab-1d08-4658-13b8df263bd5/mzaf_2704060614543532885.plus.aac.p.m4a";
        audio_player.volume=0.10;
        audio_player.autoPlay=false;
        audio_player.preLoad=false;
    var users;
    socket.on('connect', function() {
        console.log("connected");
        urldata = urlData();
        username = urldata["name"];
        room = urldata["room"];
        if(urldata["create"] == "True"){
            socket.emit('create_lobby', {name: username})
            $('#guess_song').hide();
        }
        else {
            socket.emit('join_lobby', {name: username, room: room})
            $('#room_code').text("Room Code: " + room);
            $('#guess_song').hide();
            $('#create_game').hide();
        }
    });

    socket.on('redirect', function(event){
        console.log("hello from redirect pre-replace");
        window.stop(); //supposed to stop the window from redirecting
        location.replace("index"); //supposed to redirect ?? back to the index page - i only put this here to see if it would work or not
        document.getElementById("#createValidation").innerHTML = "trying to join a room that doesn't exist!!";
        //changes the html right below the form entry to output error message
        console.log("hello from redirect post-replace");
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
       $('#guess_song').show();
       setInterval(request_game_data, 500);
    });
    socket.on('update_game', function(msg) {
        console.log(msg);
        console.log(msg["song"]["preview_url"]);
        if(audio_player.src != msg["song"]["preview_url"]) {
            audio_player.src = msg["song"]["preview_url"];
            audio_player.load();
            audio_player.play();
        }
        thumb_url = msg["song"]["thumbnail_url"];
        users=msg["users"];
        update_scoreboard();
    });
    socket.on('guess_result', function(msg){
        $('#chat_output').append("GUESS RESULT: " + msg);
        if(msg == "correct"){
            $('#thumb').attr("src", thumb_url);
        }
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



