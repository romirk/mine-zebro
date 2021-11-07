console.log("Hello world test")

socket.on('connect', function(){
    socket.emit('message', {data: 'I am connected'});
});
