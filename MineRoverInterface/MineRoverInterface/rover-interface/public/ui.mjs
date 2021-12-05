const QUEUE = [];
const HISTORY = [];

const QueueElement = document.getElementsByClassName("queue_list")[0];
const HistoryElement = document.getElementsByClassName("history")[0];
let lastCommand = 0;

function enqueue(command) {
  QUEUE.push(command);
  update_ui();
}

function log_history(history) {
  HISTORY.push(history);
  update_ui();
}

function clear_queue() {
  QUEUE.length = 0;
  update_ui();
}

function clear_history() {
  HISTORY.length = 0;
  update_ui();
}

function update_ui() {
  let qstr = "";

  QUEUE.forEach((command, index) => {
    let split = command.split(" ");
    if (split.length < 1) return;
    qstr +=
      "<span style='color:skyblue;background-color:inherit;'>" +
      split[0] +
      "</span> " +
      (split.length > 1 ? split.slice(1).join(" ") : "") +
      "<br>";
  });
  QueueElement.innerHTML = qstr;
  HistoryElement.innerHTML = HISTORY.join("<br>");
}

// non-ws event listeners
var clearQueueBtn = document.getElementsByClassName("control button12")[0];
clearQueueBtn.onclick = function (event) {
  clear_queue();
};

var clearhistoryBtn = document.getElementsByClassName("control button10")[0];
clearhistoryBtn.onclick = function (event) {
  clear_history();
};
