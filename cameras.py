import os
import json
import serial
import shutil
import time
from wtforms import BooleanField, IntegerField, FloatField, StringField, SelectField, FormField, SubmitField
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField
from wtforms import validators
from wtforms import Form
from forms import ToggleField, IntegerRangeWithNumberField, CommandButtonField, CommandButtonFieldWithInputDialog
from forms import CommandButtonFieldWithDeleteWarningDialog
from rig_io import Rig_io


class CameraCommandButtonForm(Form):
    push_config = CommandButtonField(
        'Push',
        # icon='glyphicon glyphicon-send',
        command='push',
        # title='Push current config',
        message='Do you want to push the selected config?'
    )

    # open_config = CommandButtonField(
    #     'Open',
    #     # icon='glyphicon glyphicon-floppy-open',
    #     command='open',
    #     # title='Open current config',
    #     message='Do you want to open the selected config?'
    # )

    save_config = CommandButtonFieldWithInputDialog(
        'Save',
        # icon='glyphicon glyphicon-floppy-save',
        command='save',
        # title='Save current config',
        message='Please confirm or rename the configuration.'
    )

    delete_config = CommandButtonFieldWithDeleteWarningDialog(
        'Delete',
        # icon='glyphicon glyphicon-floppy-remove',
        command='delete',
        # title='Remove current config',
        message='Do you want to delete the selected config?'
    )


class CameraConfigForm(Form):
    camera_config = SelectField(
        "Config",
        choices=[('default', 'Default')],
    )
    config_command = FormField(CameraCommandButtonForm, label='Commands')


class CameraSelectionForm(Form):
    camera_id = IntegerRangeWithNumberField(
        "Camera (-1=All)",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=-1, max=255, message='min:%(min)s max%(max)s')
        ],
        minimum=-1,
        maximum=255,
        default=-1
    )


class IMIWhiteBalanceForm(Form):
    white_balance_mode = SelectField(
        "Mode",
        choices=[(0, 'ATW'), (1, 'AWC'), (2, 'INDOOR'), (3, 'OUTDOOR'), (4, 'MANUAL'), (5, 'AWB')],
        default=4,
    )
    manual_blue_gain = IntegerRangeWithNumberField(
        "Blue Gain",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=1, max=100, message='min:%(min)s max%(max)s')
        ],
        default=50
    )
    manual_red_gain = IntegerRangeWithNumberField(
       "Red Gain",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=1, max=100, message='min:%(min)s max%(max)s')
        ],
        default=50
    )
    awc_set = ToggleField('AWC Set')


class IMIHueForm(Form):
    hue_gain_r = IntegerRangeWithNumberField(
        "Red",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=128,
        minimum=1,
        maximum=255,
    )

    hue_gain_g = IntegerRangeWithNumberField(
        "Green",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=128,
        minimum=1,
        maximum=255,
    )

    hue_gain_b = IntegerRangeWithNumberField(
        "Blue",
        validators=[
            validators.Required(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=128,
        minimum=1,
        maximum=255,
    )


class IMIExposureForm(Form):
    dc_lens_mode = SelectField(
        "Mode",
        choices=[(0, 'Indoor'), (1, "Outdoor")]
    )
    dc_indoor_shut_mode = SelectField(
        "Shutter",
        choices=[
            (0x0, 'Auto'),
            (0x1, '1/60(50)'),
            (0x2, '1/100(120)(FLK)'),
            (0x3, '1/240(200)'),
            (0x4, '1/480(400)'),
            (0x5, '1/1000'),
            (0x6, '1/2000'),
            (0x7, '1/5000'),
            (0x8, '1/10000'),
            (0x9, '1/50000'),
            (0xA, 'x2'),
            (0xB, 'x4'),
            (0xC, 'x6'),
            (0xD, 'x8'),
            (0xE, 'x10'),
            (0xF, 'x15'),
            (0x10, 'x20'),
            (0x11, 'x25'),
            (0x12, 'x30'),
        ]
    )


class IMIRegistersForm(Form):
    camera_selection = FormField(CameraSelectionForm, label="Selection")
    camera_config = FormField(CameraConfigForm, label="Config")
    white_balance = FormField(IMIWhiteBalanceForm, label="White Balance")
    exposure = FormField(IMIExposureForm, label="Exposure")
    hue = FormField(IMIHueForm, label='Hue')


class IMIRemote(Form):
    # camera_id = SelectField(
    #     "Camera ID",
    #     choices=[(c, c) for c in ['all', 1, 2, 3, 4, 5, 6]],
    # )
    camera_id = IntegerRangeWithNumberField(
        "Camera (-1=All)",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=-1, max=255, message='min:%(min)s max%(max)s')
        ],
        minimum=-1,
        maximum=255,
        default=-1
    )
    port = SelectField(
        "Port",
        choices=[('usb0', 'usb0')]
    )


class IMIRemoteForm(Form):
    config = FormField(IMIRemote, label='Selection')


class Camera(object):
    CONFIGS_LOCATION = os.path.abspath('./camera_configs')
    DELETED_CONFIGS_LOCATION = os.path.join(CONFIGS_LOCATION, 'deleted')

    @property
    def port(self):
        raise NotImplemented('not impllemented')

    def execute(self, data):
        getattr(self, data.pop('command'))(data)

    @property
    def configs(self):
        configs = [path for path in os.listdir(self.CONFIGS_LOCATION) if os.path.splitext(path)[-1] == '.json']
        return [os.path.splitext(config)[0] for config in configs]

    @property
    def config_choices(self):
        return [(config, config.title()) for config in self.configs]


class IMICamera(Camera):
    type_name = "IMI"
    port = '/dev/ttyUSB0'
    delay = 1
    pages = dict(
        registers=IMIRegistersForm(),
        remote=IMIRemoteForm()
    )
    _control_commands = dict(
            up='01',
            down='02',
            left='03',
            right='04',
            enter='00',
        )

    addresses = {
        'exposure-dc_indoor_shut_mode': 'E108',
        'exposure-dc_lens_mode': 'E0F1',
        'hue-hue_gain_b': '03E7',
        'hue-hue_gain_g': '03E5',
        'hue-hue_gain_r': '03E3',
        'white_balance-manual_blue_gain': 'E201',
        'white_balance-manual_red_gain': 'E202',
        'white_balance-white_balance_mode': 'E200',
    }


    def __init__(self):
        self.bus = Rig_io()
        self.bus_methods =[
            method for method in dir(self.bus) if callable(getattr(self.bus, method)) and method != "__init__"
        ]
        self.data = None
        self.current_config_name = 'default'
        self.current_config = {}

    @property
    def control_commands(self):
        camera_id = self.data.get('camera_id', '-1')
        template = '#OKC={value}\r'
        if camera_id != '-1':
            template = '#OKC2={camera_id}{value}\r'

        return dict([(key, template.format(**locals())) for key, value in self._control_commands.iteritems()])

    def execute(self, data):
        command = data.pop('command')
        self.data = data
        # print 'executing:', command

        if command in self._control_commands:

            self.send_command(self.control_commands[command], port=self.port)
            print command, 'executed'
            return

        local_command = getattr(self, command, None)
        if local_command:
            return local_command()

        # see if bus has command
        elif command in self.bus_methods:
            getattr(self.bus, command)()
        else:
            print command, 'not found'
            return

        # print command, 'executed'
        return

    def all_cameras(self):
        self.bus.mv_all()
        time.sleep(0.1)
        self.bus.mv_idle()
        time.sleep(0.1)
        print 'All cameras done'

    def next_camera(self):
        self.bus.mv_step()
        time.sleep(0.1)
        self.bus.mv_idle()
        time.sleep(0.1)
        print 'Next camera done'

    def flash_and_beep(self):
        print 'closing contact'
        self.bus.cl_on()
        time.sleep(0.1)
        print 'openning contact'
        self.bus.cl_off()
        print 'done'

    def record_start(self):
        print 'start recording'
        self.bus.rec_on()
        time.sleep(1)
        self.bus.rec_off()

    def record_stop(self):
        print 'stop recording'
        self.bus.rec_on()
        time.sleep(4)
        self.bus.rec_off()

    def all_off(self):
        print 'all off'
        self.bus.alloff()

    def send_command(self, command='', port='',):
        try:
            ser = serial.Serial(port=self.port)
            result = ser.write(command)
            # print result
            ser.close()
        except OSError:
            # print 'Serial device %s not found'%port
            pass

    def push(self):
        camera_id = int(self.data.pop('camera_selection-camera_id'))
        camera_config_name = self.data.pop('camera_config-camera_config')
        self.data.pop('config_name')

        template = "#ISPW={address}{data}\r"
        if camera_id != -1:
            template = "#ISPW2={camera_id}{address}{data}\r"
            camera_id = '%02d' % camera_id

        for key, value in self.data.items():
            if key.endswith('_number'):
                continue

            try:
                data = '%02d' % int(hex(int(value)).split('x')[1])

                address = self.addresses[key]

                command = template.format(**locals())

                print 'Sending', command[:-1], 'for', key, value
                self.send_command(command, port=self.port)
                print 'command sent'
            except:
                print 'Error:', key, value

    def open(self):
        self.data.pop('camera_selection-camera_id') # 'All', '1', '2'
        camera_config_name = self.data.pop('camera_config-camera_config')
        json_file = '%s/%s.json' % (self.CONFIGS_LOCATION, camera_config_name)
        with open(json_file, 'r') as f:
            config = json.loads(f.read())
        self.current_config_name = camera_config_name
        return config

    def save(self):
        self.data.pop('camera_selection-camera_id') # 'All', '1', '2'
        self.data.pop('camera_selection-camera_id_number')
        self.data.pop('camera_config-camera_config')
        camera_config_name = self.data.pop('config_name')
        json_file = '%s/%s.json' % (self.CONFIGS_LOCATION, camera_config_name)
        json_content = json.dumps(self.data, sort_keys=True, indent=4)

        results = {}
        try:
            with open(json_file, 'w') as f:
                f.write(json_content)
            results.update(
                dict(
                    message='%s saved.'% camera_config_name.title(),
                    category='success',
                    success=1
                )
            )
        except Exception as e:
            results.update(
                dict(
                    category='danger',
                    message=e.message,
                )
            )
        self.current_config_name = camera_config_name
        return results

    def delete(self):
        camera_config_name = self.data.pop('camera_config-camera_config')
        results = {}

        if camera_config_name != 'default':
            json_file = '%s/%s.json' % (self.CONFIGS_LOCATION, camera_config_name)
            deleted_json_file = '%s/%s.json' % (self.DELETED_CONFIGS_LOCATION, camera_config_name)
            print deleted_json_file

            try:
                if not os.path.exists(self.DELETED_CONFIGS_LOCATION):
                    os.makedirs(self.DELETED_CONFIGS_LOCATION)

                if os.path.exists(json_file):
                    if os.path.exists(deleted_json_file):
                        os.remove(deleted_json_file)
                    shutil.move(json_file, self.DELETED_CONFIGS_LOCATION)

                results.update(
                    dict(
                        message='%s deleted.'% camera_config_name,
                        category='success',
                        success=1
                    )
                )
                self.current_config_name = 'default'
            except Exception as e:
                results.update(
                    dict(
                        category='danger',
                        message=e.message,
                    )
                )
        else:
            results.update(
                dict(
                    category='danger',
                    message='Cannot delete default config!'
                )
            )
        return results


class CISCamera(Camera):
    pass
