import random
from datetime import datetime

from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

# Generate random data for temperature and humidity
def generate_data():
    temperature = round(random.uniform(20, 30), 2)
    humidity = round(random.uniform(40, 60), 2)
    return temperature, humidity

# Render the home page
@app.route('/')
def home():
    return render_template('index.html', title='Dashboard')

# Endpoint for getting the chart data
@app.route('/chart-data')
def chart_data():
    temperature, humidity = generate_data()
    timestamp = datetime.now().isoformat()
    
    # Check for null values
    if temperature is None or humidity is None:
        return jsonify(error='Null values received')
    
    return jsonify(temperature=temperature, humidity=humidity, timestamp=timestamp)

if __name__ == '__main__':
    app.run(debug=True)
