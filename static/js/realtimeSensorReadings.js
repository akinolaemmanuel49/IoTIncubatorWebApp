(function () {
    'use strict'

    var temperature = document.getElementById('temperature');
    var humidity = document.getElementById('humidity');
    var waterLevel = document.getElementById('water-level');
    var motionDetection = document.getElementById('motion');
    var incubatorStatus = document.getElementById('status');

    function updateEnvironmentData() {
        // setTimeout(() => {
            // fetch('https://flask-production-8ae1.up.railway.app/sensor/data')
            fetch('http://localhost:5000/sensor/data')
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
                    if (data.incubatorStatus === true) {
                        incubatorStatus.className = 'status-icon active';
                    }
                    else if (data.incubatorStatus === false) {
                        incubatorStatus.className = 'status-icon completed';
                    }
                })
                .catch(error => console.error(error));
        // }, 5000);
    }
    // Update the environment data card every 5 second
    setInterval(updateEnvironmentData, 5000);
})();