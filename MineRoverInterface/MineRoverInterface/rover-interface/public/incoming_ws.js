// import {update_ui, QUEUE, HISTORY} from './ui.js';

const socket = io();

socket.on("connect", function () {
  socket.emit("command", { command: "" });
});

socket.on("output", function (message) {
  let data = JSON.parse(message);
  console.log(data);
  if (data.has_process_completed) {
    HISTORY.push(data.command_id + ": " + data.package.msg);
  } else {
    QUEUE.push(data.command_id + ": " + data.package.msg);
  }
  switch (data.command_id) {
    case "battery":
      // ??? where to put this?
      break;
  }

  // update the UI
  update_ui();
});
