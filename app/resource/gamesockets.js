$(document).ready(function() {
    namespace = '/';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    socket.on('connect', function() {
        socket.emit('event', {data: 'Yoo hoo!'});
        console.log("yes");
    });
    socket.on('reply', function(msg) {
       $("#output").text( msg["data"] );
        console.log(msg);
    });
    $('button#join').click(function(event) {
        socket.emit('join_lobby', {name: $('#name').val(), room: $('#room_code').val()});
        console.log("JOINED");
       return false;
    });
    $('button#create_lobby').click(function(event) {
        socket.emit('create_lobby', {name: $('#name').val()});
        console.log('clicked');
        return false;
    });
});
