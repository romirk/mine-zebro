const QUEUE = [];
const HISTORY = [];
const STATS = {
  name: "LZ",
  connection: "",
  ip: "0.0.0.0",
  env: {
    temperature: 0,
    pressure: 0,
    humidity: 0,
  },
  battery: 0,
  geo: { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8 },
  lidar: {},
};

const chartsByCanvasId = {};

const destroyChartIfNecessary = (canvasId) => {
  if (chartsByCanvasId[canvasId]) {
    chartsByCanvasId[canvasId].destroy();
  }
};

const registerNewChart = (canvasId, chart) => {
  chartsByCanvasId[canvasId] = chart;
};

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
  document.getElementsByClassName("batt_level")[0].innerText = STATS.battery;
  document.getElementById("rname").innerText = STATS.name;
  document.getElementById("rconn").innerText = STATS.connection;
  document.getElementById("rip").innerText = STATS.ip;
  document.getElementById("rtemp").innerText = STATS.env.temperature;
  document.getElementById("rpress").innerText = STATS.env.pressure + " Pa";
  document.getElementById("rhum").innerText = STATS.env.humidity;

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

  const labels = Object.keys(STATS.geo);
  const data = {
    labels: labels,
    datasets: [
      {
        label: "GeoPhone",
        data: Object.values(STATS.geo),
        borderWidth: 1,
        color: "#cc65fe",
      },
    ],
  };

  const config = {
    type: "bar",
    data: data,
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  };

  destroyChartIfNecessary("geochart");
  const geochart = new Chart("geochart", config);
  registerNewChart("geochart", geochart);
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

update_ui(); //initialize
