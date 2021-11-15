console.log("Hello world test")

socket.on('connect', function(){
    socket.emit('command', {command: ""});
});


socket.on('output', function(message){
    console.log(message)
});