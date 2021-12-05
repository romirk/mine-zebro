//These are the controls for the rover.
var leftButton = document.getElementsByClassName("controlButton4")[0];
leftButton.onclick = function (event) {
  console.log("leftbutton");
  socket.emit("command", { command: "loc: go left:10" });
};

var downButton = document.getElementsByClassName("controlButton3")[0];
downButton.onclick = function (event) {
  console.log("downbutton");
  socket.emit("command", { command: "loc: go back:10" });
};

var rightButton = document.getElementsByClassName("controlButton2")[0];
rightButton.onclick = function (event) {
  console.log("rightbutton");
  socket.emit("command", { command: "loc: go right:10" });
};

var upButton = document.getElementsByClassName("controlButton1")[0];
upButton.onclick = function (event) {
  console.log("upbutton");
  socket.emit("command", { command: "loc: go forward:10" });
};

//Additional Locomotion commands

var relaxButton = document.getElementsByClassName("control button5")[0];
relaxButton.onclick = function (event) {
  console.log("relax");
  socket.emit("command", { command: "loc: go relax" });
};

var bowButton = document.getElementsByClassName("control button4")[0];
bowButton.onclick = function (event) {
  console.log("bow");
  socket.emit("command", { command: "loc: go bow" });
};

var sitButton = document.getElementsByClassName("control button3")[0];
sitButton.onclick = function (event) {
  console.log("sit");
  socket.emit("command", { command: "loc: go sit" });
};

var lieButton = document.getElementsByClassName("control button2")[0];
lieButton.onclick = function (event) {
  console.log("lie");
  socket.emit("command", { command: "loc: go down" });
};

var riseButton = document.getElementsByClassName("control button1")[0];
riseButton.onclick = function (event) {
  console.log("rise");
  socket.emit("command", { command: "loc: go up" });
};

var cameraOn = document.getElementsByClassName("control button6")[0];
cameraOn.onclick = function (event) {
  console.log("camera on");
  socket.emit("command", { command: "camera on" });
};

var cameraOff = document.getElementsByClassName("control button7")[0];
cameraOff.onclick = function (event) {
  console.log("camera off");
  socket.emit("command", { command: "camera off" });
};

var cameraScreenShot = document.getElementsByClassName("control button8")[0];
cameraScreenShot.onclick = function (event) {
  console.log("camera screenshot");
  socket.emit("command", { command: "camera screenshot" });
};

var lightsOn = document.getElementsByClassName("control button81")[0];
lightsOn.onclick = function (event) {
  console.log("lights on");
  socket.emit("command", { command: "lights on" });
};

var lightsOff = document.getElementsByClassName("control button82")[0];
lightsOff.onclick = function (event) {
  console.log("lights off");
  socket.emit("command", { command: "lights off" });
};

var lightsMax = document.getElementsByClassName("control button83")[0];
lightsMax.onclick = function (event) {
  console.log("lights max");
  socket.emit("command", { command: "lights max" });
};

//Queue Commands
var sendCommandToQueue = document.getElementsByClassName("control button14")[0];
sendCommandToQueue.onclick = function (event) {
  const command_prompt = document.getElementsByClassName("command_prompt")[0];
  const command = command_prompt.value.trim();
  command_prompt.value = "";
  QUEUE.push(command);
  console.log("Command: " + command);
  socket.emit("command", { command: command });
};
