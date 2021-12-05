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

  const prefix =
    "<span style='color:yellow;background-color:inherit;'>" +
    data.command_id +
    "</span>: ";

  // } else {
  // enqueue(data.command_id + ": " + data.package.msg);
  // }
  switch (data.command_id) {
    //TODO figure out format
    case "battery":
      // ??? where to put this?
      STATS.battery = data.package.msg;
      log_history(prefix + data.package.msg);
      break;
    case "mcp":
      log_history(prefix + data.package);
      break;
      case "env":
        STATS.env = data.package.data;
        log_history(prefix + STATS.env.temperature + " | " + STATS.env.humidity + " | " + STATS.env.pressure);
        break;
    case "geo":
      // ??? where to put this?
      STATS.geo = data.package.data;
      log_history(prefix + Object.keys(data.package.data).length);
      break;
    case "lidar":
      // ??? format?
      STATS.lidar = data.package.data;
      log_history(prefix + data.package);
      break;
    default:
      log_history(prefix + data.package.msg);
  }

  // update the UI
  update_ui();
});
