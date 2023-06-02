(function () {
    'use strict'

    var temperature = document.getElementById('temperature');
    var humidity = document.getElementById('humidity');
    var waterLevel = document.getElementById('water-level');
    var motionDetection = document.getElementById('motion');
    var incubatorStatus = document.getElementById('status');

    function updateEnvironmentData() {
        fetch('https://flask-production-8ae1.up.railway.app/sensor/data')
            .then(response => response.json())
            .then(data => {
                if (typeof data !== 'object') {
                    console.error('Invalid data format:', data);
                    return;
                }

                temperature.textContent = data.temperature.toFixed(2);
                humidity.textContent = data.humidity.toFixed(2);
                if (data.waterLevelSensorState) {
                    waterLevel.className = 'status-text green';
                    waterLevel.textContent = 'TRUE';
                }
                else {
                    waterLevel.className = 'status-text red';
                    waterLevel.textContent = 'FALSE';
                }
                motionDetection.textContent = data.motionSensorState;
                if (data.motionSensorState) {
                    motionDetection.className = 'status-text green';
                    motionDetection.textContent = 'TRUE';
                }
                else {
                    motionDetection.className = 'status-text red';
                    motionDetection.textContent = 'FALSE';
                }
                if (data.incubatorStatus === 'active') {
                    incubatorStatus.className = 'status-icon active';
                }
                else if (data.incubatorStatus === 'paused') {
                    incubatorStatus.className = 'status-icon paused';
                }
                else if (data.incubatorStatus === 'completed') {
                    incubatorStatus.className = 'status-icon completed';
                }
            })
            .catch(error => console.error(error));
    }
    // Update the environment data card every 1 second
    setInterval(updateEnvironmentData, 1000);
})();