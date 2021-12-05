const QUEUE = [];
const HISTORY = [];

const QueueElement = document.getElementsByClassName("queue_list")[0];
const HistoryElement = document.getElementsByClassName("history")[0];

function update_ui() {
    QueueElement.innerHTML = QUEUE.join("<br>");
    HistoryElement.innerHTML = HISTORY.join("<br>");
  }

//   export {update_ui, QUEUE, HISTORY};