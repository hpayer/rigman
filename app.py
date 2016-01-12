#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask, render_template, request, json, redirect, url_for, json
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf import Form
import logging
from logging import Formatter, FileHandler
# from web_page_logger import WebPageHandler
from forms import *
import serial
from cameras import IMICamera, CISCamera
from wtforms import FormField

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

LEFT, RIGHT, UP, DOWN, ENTER, NEXT, ALL = "left", "right", "up", "down", "enter", "next", 'all'
AVAILABLE_COMMANDS = {
    'Left': LEFT,
    'Right': RIGHT,
    'Up': UP,
    'Down': DOWN,
    'Enter': ENTER,
    'Next': NEXT,
    'All': ALL
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



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for(request.form['submit']))
    return render_template('pages/home.html', commands=AVAILABLE_COMMANDS)


# @app.route('/<cmd>')
# def command(cmd=None):
#     print 'in', cmd
#     camera_command = cmd[0].upper()
#     response = "Moving {}".format(cmd.capitalize())
#     # print camera_command
#
#     # ser.write(camera_command)
#     return response, 200, {'Content-Type': 'text/plain'}


@app.route('/command', methods=['POST'])
def command(cmd=None):
    form = request.form
    data = dict([(kv.split('=')) for kv in form['form'].split('&')])

    command=form['command']
    data.update(dict(command=command))
    # if command in ['push', 'open', 'save', 'remove']:
    #
    #     answer = False
    #     # answer = dialog()
    #     if not answer:
    #         return json.dumps({'status':'OK'})

    # print 'command:', data
    results = camera.execute(data)
    if results:
        print results
        return json.dumps(results)

    return json.dumps({'status':'OK'})


@app.route('/remote', methods=['POST', 'GET'])
def remote():
    form = RemoteForm()

    if request.method == 'POST':
        if request.form['command'] in ['up', 'down', 'left', 'right', 'enter']:
            command = request.form['command']
            camera_id = request.form['camera_id']
            # port = request.form['port']
            results = camera.execute(command)

    return render_template('pages/remote.html', form=form, commands=AVAILABLE_COMMANDS)


@app.route('/control', methods=['POST', 'GET'])
def control():
    form = MultiViewForm()

    if request.method == 'POST':
        if request.form['command'] in ['all', 'next']:
            command = request.form['command']
            # camera_id = request.form['camera_id']
            # port = request.form['port']
            camera.execute(command)

    return render_template('pages/control.html', form=form)


def get_form(fields):
    class NewForm(Form):
        pass
    for name, field in fields.items():
        setattr(NewForm, name, field)
    return NewForm


def get_formfield(form_classes):
    class NewForm(Form):
        pass
    for form_class in form_classes:
        setattr(NewForm, form_class.__name__, FormField(form_class, 'White Balance'))
    return NewForm


@app.route('/registers',  methods=['POST', 'GET'])
def registers():
    form = camera.pages['registers']
    form.camera_config.form.camera_config.choices = camera.config_choices
    return render_template('pages/registers.html', form=camera.pages['registers'])

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

