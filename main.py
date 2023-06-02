from flask import Flask, render_template, request

app = Flask(__name__)


# Render the home page
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html', title='IoT Incubator|Dashboard', heading='Dashboard', active_page='dashboard')


@app.route('/live-monitoring', methods=['GET'])
def live_monitoring():
    return render_template('live_monitoring.html', title='IoT Incubator|Live Monitoring', heading='Live Monitoring', active_page='live_monitoring')


@app.route('/control-panel', methods=['GET', 'POST'])
def control_panel():
    # Default values for incubation parameters
    default_min_temp = 37.5
    default_max_temp = 38.5
    default_min_humidity = 50
    default_max_humidity = 70
    default_egg_turn_interval = 60
    default_turning_days = 18

    if request.method == 'POST':
        # Get user inputs from the form
        min_temp = float(request.form['min_temp'])
        max_temp = float(request.form['max_temp'])
        min_humidity = int(request.form['min_humidity'])
        max_humidity = int(request.form['max_humidity'])
        egg_turn_interval = int(request.form['egg_turn_interval'])
        turning_days = int(request.form['turning_days'])
    else:
        # Use default values
        min_temp = default_min_temp
        max_temp = default_max_temp
        min_humidity = default_min_humidity
        max_humidity = default_max_humidity
        egg_turn_interval = default_egg_turn_interval
        turning_days = default_turning_days

    return render_template('control_panel.html', title='IoT Incubator|Control Panel', heading='Control Panel', active_page='control_panel', min_temp=min_temp, max_temp=max_temp,
                           min_humidity=min_humidity, max_humidity=max_humidity,
                           egg_turn_interval=egg_turn_interval,
                           turning_days=turning_days)


if __name__ == '__main__':
    app.run(debug=True)
