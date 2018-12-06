function clickJoin(){
    var name = document.forms["joining_game"]["name"].value;
    var room_code = document.forms["joining_game"]["room_code"].value;;
    if(name == ""){
        document.getElementById("#createValidation").innerHTML = "please enter a name to proceed!";
    }
    if(room_code == ""){
        document.getElementById("#createValidation").innerHTML = "please enter a room code to proceed!";
    }
    if(name == "" && room_code == ""){
        document.getElementById("#createValidation").innerHTML = "please enter both a room code and a name to proceed!";
    }
}

function clickCreate(){
    var name = document.forms["creating_game"]["name"].value;
    if(name == ""){
        document.getElementById("#joinValidation").innerHTML = "please enter a name to proceed!";
    }
}

//TODO: update to make sure is valid