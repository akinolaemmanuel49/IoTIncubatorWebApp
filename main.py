from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
import smtplib

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.orm import sessionmaker
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy.exc import SQLAlchemyError

from database.schemas import User, engine, SessionData, SensorData, Message

app = Flask(__name__)
# Generate a secure secret key
secret_key = secrets.token_hex(16)

# Set the secret key in the Flask app
app.secret_key = secret_key

Session = sessionmaker(bind=engine)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def send_email_alert(subject: str, message: str, user: User):
    db_session = Session()

    sender_email = 'biteatertest@gmail.com'  # Replace with your email address
    receiver_email = user.email  # Replace with the recipient's email address
    password = 'zvoe ikhd zpvs zrfa'  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))
    db_message = Message(subject=subject, body=message, sender_id=user.id)
    db_session.add(db_message)
    db_session.commit()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print('Email sent successfully')
    except smtplib.SMTPException as e:
        print('Error sending email:', str(e))


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    return session.query(User).get(int(user_id))


@app.route("/sensor/data")
def sensor_data():
    db_session = Session()
    status = True

    current_sensor_reading = db_session.query(
        SensorData).order_by(SensorData.timestamp.desc()).first()

    active_session = db_session.query(
        SessionData).filter(SessionData.is_active).first()
    
    db_session.query(User).get(active_session.user_id)

    if datetime.now() >= (active_session.session_start + timedelta(days=active_session.session_duration)):
        status = False

    # Check temperature and humidity thresholds
    temperature = current_sensor_reading.temperature
    humidity = current_sensor_reading.humidity

    return jsonify(temperature=temperature,
                   humidity=humidity,
                   motionSensorState=current_sensor_reading.motion_detected,
                   waterLevelSensorState=current_sensor_reading.refill_water,
                   incubatorStatus=status,
                   timestamp=current_sensor_reading.timestamp)

@app.route('/register', methods=['GET', 'POST'])
def register():
    title = "IoT Incubator|Register"
    year = datetime.utcnow().year
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user instance
        new_user = User(email=email, passwordhash=hashed_password)

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
        email = request.form['email']
        password = request.form['password']

        session = Session()
        user = session.query(User).filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.passwordhash, password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Replace 'dashboard' with the desired route name
        else:
            error_message = 'Invalid email address or password. Please try again.'
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
    return render_template('dashboard.html', 
                           title='IoT Incubator|Dashboard',
                           heading='Dashboard',
                           active_page='dashboard',)


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
                session_duration=incubation_period,
                user_id=current_user.id
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
    
    return render_template('control_panel.html',
                           title='IoT Incubator|Control Panel',
                           heading='Control Panel',
                           active_page='control_panel')



@app.route('/alert')
@login_required
def alert():
    db_session = Session()

    current_sensor_reading = db_session.query(
        SensorData).order_by(SensorData.timestamp.desc()).first()

    active_session = db_session.query(
        SessionData).filter(SessionData.is_active).first()
    
    user = db_session.query(User).filter(User.id == current_user.id).first()

    # Check temperature and humidity thresholds
    temperature = current_sensor_reading.temperature
    humidity = current_sensor_reading.humidity

    if active_session:
        if temperature >= active_session.max_temperature + 5:
            send_email_alert('Temperature Alert', f'Temperature is 5 values above the maximum threshold. Current value: {temperature}', user=user)

        if temperature <= active_session.min_temperature - 5:
            send_email_alert('Temperature Alert', f'Temperature is 5 values below the minimum threshold. Current value: {temperature}', user=user)

        if humidity >= active_session.max_humidity + 5:
            send_email_alert('Humidity Alert', f'Humidity is 5 values above the maximum threshold. Current value: {humidity}', user=user)

        if humidity <= active_session.min_humidity - 5:
            send_email_alert('Humidity Alert', f'Humidity is 5 values below the minimum threshold. Current value: {humidity}', user=user)
    return render_template('alerts.html',
                           title='IoT Incubator|Alerts',
                           heading='Alerts',
                           active_page='alerts',
                           current_sensor_reading=current_sensor_reading,
                           current_user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('login'))  # Replace 'login' with the desired route name


if __name__ == '__main__':
    app.run(debug=True)
