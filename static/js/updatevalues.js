var socket = io()

socket.on('update', function(data) {
    let element = document.getElementById(data["sensor_id"]);
    let sensor_value = data["sensor_value"];
    element.textContent = sensor_value + " °C";
});