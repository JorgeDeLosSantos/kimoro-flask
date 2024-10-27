plotGauge();
plotLine();

var socket = io()

socket.on('updateChart', function(data) {
  var new_data_gauge = {
    value: data["sensor_value"],
    delta: {reference: data["last_reads"][1]}
  }
  var new_data_line = {
    x: Array.from(Array(data["last_reads"].length).keys()),
    y: data["last_reads"],
  }
  if (sensor_id == parseInt(data["sensor_id"]) ){
    Plotly.update('chart-gauge-0'+sensor_id, new_data_gauge);
    Plotly.react('chart-line-0'+sensor_id, [new_data_line]);
  }
});

function plotGauge() {
  var data = [
    {
      domain: { x: [0, 1], y: [0, 1] },
      value: sensor_value,
      title: { text: "Temperature (°C)" },
      type: "indicator",
      mode: "gauge+number+delta",
      delta: { reference: last_reads[1] },
      gauge: {
        axis: { range: [0, 120] },
        bar: {color: "#2377cc"},
        steps: [
          { range: [0, 30], color: "#65c244" },
          { range: [30, 50], color: "#eb8657" },
          { range: [50, 120], color: "#f03a49" }
        ],
      }
    }
  ];
  
  var layout = {font: {size: 12}};
  var config = {resposive: true};
  Plotly.newPlot('chart-gauge-0'+sensor_id, data, layout, config);
}
  
function plotLine() {
  var data = {
    x: Array.from(Array(last_reads.length).keys()),
    y: last_reads,
    type: 'scatter'
  };

  var layout = {
    title: "Latest sensor readings",
    yaxis: {title:"Temperature °C"},
  }
  
  Plotly.newPlot('chart-line-0'+sensor_id, [data], layout, {responsive: true});
}