from flask import Flask, render_template, jsonify

app = Flask(__name__)


# Render the home page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='IoT Incubator|Dashboard', heading='Dashboard', active_page='dashboard')

@app.route('/live-monitoring')
def live_monitoring():
    return render_template('live_monitoring.html', title='IoT Incubator|Live Monitoring', heading='Live Monitoring', active_page='live_monitoring')

@app.route('/control-panel')
def control_panel():
    return render_template('control_panel.html', title='IoT Incubator|Control Panel', heading='Control Panel', active_page='control_panel')


if __name__ == '__main__':
    app.run(debug=True)
