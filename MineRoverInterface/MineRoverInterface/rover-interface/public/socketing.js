console.log("Hello world test")

const socket = io();


socket.on('connect', function(){
    socket.emit('command', {command: ""});
});


socket.on('output', function(message){
    // console.log(message);
    let data = JSON.parse(message);
    console.log(data);
});