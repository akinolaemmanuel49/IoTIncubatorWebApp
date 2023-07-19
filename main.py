from datetime import datetime, timedelta
import secrets

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.orm import sessionmaker
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy.exc import SQLAlchemyError

from database.schemas import User, engine, SessionData, SensorData

app = Flask(__name__)
# Generate a secure secret key
secret_key = secrets.token_hex(16)

# Set the secret key in the Flask app
app.secret_key = secret_key

Session = sessionmaker(bind=engine)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    return session.query(User).get(int(user_id))


@app.route("/sensor/data")
def sensor_data():
    db_session = Session()
    status = False

    current_sensor_reading = db_session.query(
        SensorData).order_by(SensorData.timestamp.desc()).first()

    active_session = db_session.query(
        SessionData).filter(SessionData.is_active).first()
    if datetime.now() >= (active_session.session_start + timedelta(days=active_session.session_duration)):
        status = False

    return jsonify(temperature=current_sensor_reading.temperature,
                   humidity=current_sensor_reading.humidity,
                   motionSensorState=current_sensor_reading.motion_detected,
                   waterLevelSensorState=current_sensor_reading.refill_water,
                   incubatorStatus=status,
                   timestamp=current_sensor_reading.timestamp)


@app.route('/register', methods=['GET', 'POST'])
def register():
    title = "IoT Incubator|Register"
    year = datetime.utcnow().year
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user instance
        new_user = User(username=username, passwordhash=hashed_password)

        try:
            session = Session()
            session.add(new_user)
            session.commit()
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            session.rollback()
            error_message = 'An error occurred during registration. Please try again.'
            flash(error_message, 'error')
            return render_template('register.html', error_message=error_message, title=title, year=year)

    return render_template('register.html', title=title, year=year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = "IoT Incubator|Login"
    year = datetime.utcnow().year
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        session = Session()
        user = session.query(User).filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.passwordhash, password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Replace 'dashboard' with the desired route name
        else:
            error_message = 'Invalid username or password. Please try again.'
            flash(error_message, 'error')
            return render_template('login.html', error_message=error_message, title=title, year=year)

    return render_template('login.html', title=title, year=year)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    db_session = Session()

    active_session = db_session.query(
        SessionData).filter(SessionData.is_active).first()
    if active_session:
        max_temp = active_session.max_temperature
        min_temp = active_session.min_temperature
        max_humidity = active_session.max_humidity
        min_humidity = active_session.min_humidity
        egg_turn_interval = active_session.turn_interval
        egg_turning_start = active_session.turn_stage_start
        incubation_egg_turn_period = active_session.duration_turning_stage
        incubation_period = active_session.session_duration
    db_session.close()

    return render_template('dashboard.html',
                           title='IoT Incubator|Dashboard',
                           heading='Dashboard',
                           active_page='dashboard',
                           max_temp=max_temp,
                           min_temp=min_temp,
                           min_humidity=min_humidity,
                           max_humidity=max_humidity,
                           egg_turn_interval=egg_turn_interval,
                           egg_turning_start=egg_turning_start,
                           incubation_egg_turn_period=incubation_egg_turn_period,
                           incubation_period=incubation_period)


@app.route('/live-monitoring', methods=['GET'])
@login_required
def live_monitoring():
    return render_template('live_monitoring.html', title='IoT Incubator|Live Monitoring', heading='Live Monitoring', active_page='live_monitoring')


@app.route('/control-panel', methods=['GET', 'POST'])
@login_required
def control_panel():
    db_session = Session()

    if request.method == 'POST':
        # Get user inputs from the form
        min_temp = float(request.form['min_temp'])
        max_temp = float(request.form['max_temp'])
        min_humidity = float(request.form['min_humidity'])
        max_humidity = float(request.form['max_humidity'])
        egg_turn_interval = float(request.form['egg_turn_interval'])
        egg_turning_start = int(request.form['egg_turning_start'])
        incubation_egg_turn_period = int(
            request.form['incubation_egg_turn_period'])
        incubation_period = int(request.form['incubation_period'])

        active_session = db_session.query(
            SessionData).filter(SessionData.is_active).first()
        if active_session:
            active_session.min_temperature = min_temp
            active_session.max_temperature = max_temp
            active_session.min_humidity = min_humidity
            active_session.max_humidity = max_humidity
            active_session.turn_interval = egg_turn_interval
            active_session.turn_stage_start = egg_turning_start
            active_session.duration_turning_stage = incubation_egg_turn_period
            active_session.session_duration = incubation_period
            db_session.add(active_session)
            db_session.commit()
        else:
            new_session = SessionData(
                max_temperature=max_temp,
                min_temperature=min_temp,
                max_humidity=max_humidity,
                min_humidity=min_humidity,
                turn_interval=egg_turn_interval,
                turn_stage_start=egg_turning_start,
                duration_turning_stage=incubation_egg_turn_period,
                session_duration=incubation_period
            )
            db_session.add(new_session)
            db_session.commit()
        db_session.close()
        return redirect(url_for('dashboard'))
    else:
        active_session = db_session.query(
            SessionData).filter(SessionData.is_active).first()
        if active_session:
            max_temp = active_session.max_temperature
            min_temp = active_session.min_temperature
            max_humidity = active_session.max_humidity
            min_humidity = active_session.min_humidity
            egg_turn_interval = active_session.turn_interval
            egg_turning_start = active_session.turn_stage_start
            incubation_egg_turn_period = active_session.duration_turning_stage
            incubation_period = active_session.session_duration
        db_session.close()

    return render_template('control_panel.html',
                           title='IoT Incubator|Control Panel',
                           heading='Control Panel',
                           active_page='control_panel',
                           min_temp=min_temp,
                           max_temp=max_temp,
                           min_humidity=min_humidity,
                           max_humidity=max_humidity,
                           egg_turn_interval=egg_turn_interval,
                           egg_turning_start=egg_turning_start,
                           incubation_egg_turn_period=incubation_egg_turn_period,
                           incubation_period=incubation_period)


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('login'))  # Replace 'login' with the desired route name


if __name__ == '__main__':
    app.run(debug=True)
