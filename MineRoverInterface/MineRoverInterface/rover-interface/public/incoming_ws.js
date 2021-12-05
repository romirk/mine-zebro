// import {update_ui, QUEUE, HISTORY} from './ui.js';

const socket = io();

socket.on("connect", function () {
  console.log("Connected to server");
});

socket.on("output", function (message) {
  let data = JSON.parse(message);
  console.log(data);
  // TODO figure out how to add backend to queue
  // if (data.has_process_completed) {
  log_history(
    "<span style='color:yellow;background-color:inherit;'>" +
      data.command_id +
      "</span>: " +
      data.package.msg
  );
  // } else {
  // enqueue(data.command_id + ": " + data.package.msg);
  // }
  switch (data.command_id) {
    case "battery":
      // ??? where to put this?
      break;
  }

  // update the UI
  update_ui();
});
