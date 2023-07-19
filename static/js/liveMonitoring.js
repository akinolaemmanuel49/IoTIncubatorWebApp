/* globals Chart:false, feather:false */

(function () {
    'use strict'

    var temperature = document.getElementById('temperature');
    var humidity = document.getElementById('humidity');
    var waterLevel = document.getElementById('water-level');
    var motionDetection = document.getElementById('motion');

    // Graphs
    var ctx = document.getElementById('myChart')
    // eslint-disable-next-line no-unused-vars
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                data: []
            },
            {
                label: 'Humidity',
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                data: []
            }]
        },
        options: {
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false,
                        suggestedMax: 100
                    }
                }]
            },
            legend: {
                display: true
            }
        }
    });

    // Queue implementation
    function Queue(size) {
        this.queue = [];
        this.size = size;
    }

    Queue.prototype.enqueue = function (item) {
        this.queue.push(item);
        if (this.queue.length > this.size) {
            this.queue.shift();
        }
    }

    Queue.prototype.dequeue = function () {
        return this.queue.shift();
    }

    Queue.prototype.isEmpty = function () {
        return this.queue.length === 0;
    }

    // Create queues for temperature and humidity data
    var temperatureQueue = new Queue(5);
    var humidityQueue = new Queue(5);

    // Function to update the chart data
    function updateChartData() {
        // setTimeout(() => {
            // fetch('https://flask-production-8ae1.up.railway.app/sensor/data')
            fetch('http://localhost:5000/sensor/data')
                .then(response => response.json())
                .then(data => {
                    if (typeof data !== 'object') {
                        console.error('Invalid data format:', data);
                        return;
                    }

                    temperatureQueue.enqueue({ timestamp: data.timestamp, temperature: data.temperature });
                    humidityQueue.enqueue({ timestamp: data.timestamp, humidity: data.humidity });

                    // Update chart data with queue contents
                    myChart.data.labels = temperatureQueue.queue.map(item => item.timestamp);
                    myChart.data.datasets[0].data = temperatureQueue.queue.map(item => item.temperature);
                    myChart.data.datasets[1].data = humidityQueue.queue.map(item => item.humidity);

                    myChart.update();
                    temperature.textContent = data.temperature.toFixed(2);
                    humidity.textContent = data.humidity.toFixed(2);
                    waterLevel.textContent = data.waterLevelSensorState;
                    motionDetection.textContent = data.motionSensorState;

                })
                .catch(error => console.error(error));
        // }, 5000);
    }

    // Update the chart every 5 second
    setInterval(updateChartData, 5000);
})();
