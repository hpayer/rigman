#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask, render_template, request, json
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf import Form
import logging
from logging import Formatter, FileHandler
# from web_page_logger import WebPageHandler
from forms import *
import serial
from cameras import IMICamera, CISCamera

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

LEFT, RIGHT, UP, DOWN, ENTER = "left", "right", "up", "down", "enter"
AVAILABLE_COMMANDS = {
    'Left': LEFT,
    'Right': RIGHT,
    'Up': UP,
    'Down': DOWN,
    'Enter': ENTER
}
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''


camera = IMICamera()

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


def send_command(command='', port='', camera_id='all'):
    ser = serial.Serial(port=port)
    result = ser.write(command)
    # print result
    ser.close()


@app.route('/')
def home():
    return render_template('pages/home.html', commands=AVAILABLE_COMMANDS)

@app.route('/command', methods=['POST'])
def command(cmd=None):
    data = dict([(kv.split('=')) for kv in request.form['form'].split('&')])
    data.update(dict(command=request.form['command']))
    print data
    return json.dumps({'status':'OK'})


@app.route('/remote', methods=['POST', 'GET'])
def remote():
    form = RemoteConfig()

    if request.method == 'POST':
        if request.form['command'] in ['up', 'down', 'left', 'right', 'enter']:
            command = request.form['command']
            camera_id = request.form['camera_id']
            # port = request.form['port']
            camera.execute(command)

    return render_template('pages/remote.html', form=form, commands=AVAILABLE_COMMANDS)


def get_form(fields):
    class NewForm(Form):
        pass
    for name, field in fields.items():
        setattr(NewForm, name, field)
    return NewForm


@app.route('/registers',  methods=['POST', 'GET'])
def registers():
    fields = camera.pages['registers']
    form = get_form(fields)(csrf_enabled=False)
    return render_template('pages/registers.html', form=form)

@app.route('/config')
def config():
    parameters = []

    return render_template('pages/config.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/log')
def log():
    return render_template('pages/log.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')



#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

