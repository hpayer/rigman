import serial
import time
from wtforms import BooleanField, IntegerField, FloatField, StringField, SelectField, FormField, SubmitField
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField
from wtforms import validators
from wtforms import Form
from forms import ToggleField, IntegerRangeWithNumberField
from rig_io import Rig_io


class CameraConfigForm(Form):
    camera_config = SelectField(
        "Config",
        choices=[('exterior', 'Exterior'), ('test', 'Test'), ]
    )
    save_config = SubmitField(
        'Save',
    )


class CameraSelectionForm(Form):
    ids = [('All', 'all')]
    ids.extend([(id, id) for id in xrange(1, 53)])
    camera_config = SelectField(
        "Camera",
        choices=ids
    )


class IMIWhiteBalanceForm(Form):
    white_balance_mode = SelectField(
        "Mode",
        choices=[(0, 'ATW'), (1, 'AWC'), (2, 'INDOOR'), (3, 'OUTDOOR'), (4, 'MANUAL'), (5, 'AWB')]
    )
    manual_blue_gain = IntegerRangeWithNumberField(
        "Blue Gain",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=1, max=100, message='min:%(min)s max%(max)s')
        ],
        default=100
    )
    manual_red_gain = IntegerRangeWithNumberField(
       "Red Gain",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=1, max=100, message='min:%(min)s max%(max)s')
        ],
        default=100
    )
    awc_set = ToggleField('AWC Set')


class IMIHueForm(Form):
    hue_gain_r = IntegerRangeWithNumberField(
        "Red",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=255,
        minimum=1,
        maximum=255,
    )

    hue_gain_g = IntegerRangeWithNumberField(
        "Green",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=255,
        minimum=1,
        maximum=255,
    )

    hue_gain_b = IntegerRangeWithNumberField(
        "Blue",
        validators=[
            validators.DataRequired(),
            validators.NumberRange(min=0, max=255, message='min:%(min)s max%(max)s')
        ],
        default=255,
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
    # camera_config = FormField(CameraConfigForm, label="Config")
    camera_selection = FormField(CameraSelectionForm, label="Selection")
    white_balance = FormField(IMIWhiteBalanceForm, label="White Balance")
    exposure = FormField(IMIExposureForm, label="Exposure")
    hue = FormField(IMIHueForm, label='Hue')


class IMIRemote(Form):
    camera_id = SelectField(
        "Camera ID",
        choices=[(c, c) for c in ['all', 1, 2, 3, 4, 5, 6]]
    )
    port = SelectField(
        "Port",
        choices=[('usb0', 'usb0')]
    )


class IMIRemoteForm(Form):
    config = FormField(IMIRemote, label='Selection')


class Camera(object):

    @property
    def port(self):
        raise NotImplemented('not impllemented')

    # def execute(self, command, camera_id='all'):
    #     ser = serial.Serial(self.port)
    #     result = ser.write(self.commands[command])
    #     ser.close()

    # def execute(self, command, camera_id='all'):
        # print 'execute:', command, camera_id

    def execute(self, data):
        getattr(self, data.pop('command'))(data)


class IMICamera(Camera):
    delay = 1

    port = '/dev/ttyUSB0'
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
    control_commands = dict([(key, '#OKC=%s\r' % value) for key, value in _control_commands.iteritems()])

    def __init__(self):
        self.bus = Rig_io()
        self.bus_methods =[
            method for method in dir(self.bus) if callable(getattr(self.bus, method)) and method != "__init__"
        ]

    def execute(self, data):
        command = data.pop('command')
        self.data = data
        print 'executing:', command

        if command in self._control_commands:
            self.send_command(self.control_commands[command], port=self.port)
            print command, 'executed'
            return

        local_command = getattr(self, command, None)
        if local_command:
            local_command()

        # see if bus has command
        elif command in self.bus_methods:
            getattr(self.bus, command)()
        else:
            print command, 'not found'
            return

        print command, 'executed'
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
	slef.bus.rec_off()	

    @staticmethod
    def send_command(command='', port='',):
        try:
            ser = serial.Serial(port=port)
            result = ser.write(command)
            # print result
            ser.close()
        except OSError:
            print 'Serial device %s not found'%port

    def send_config(self):
        print self.data
        camera_id = self.data.pop('camera_selection-camera_config') # 'All', '1', '2'
        print camera_id
        addresses = dict(
            white_balance_mode='E200',
            manual_blue_gain='E201',
            manual_red_gain='E202',
        )

        if camera_id != 'All':
            camera_id = '%02d' % int(camera_id)
            for key, value in self.data.items():
                # print key, value
                key = key.split('-')[-1]
                if key in addresses:
                    # command = "#ISPW2=%s"%(camera_id)
                    command = "#ISPW2={camera_id}{address}{data}".format(
                        camera_id=camera_id,
                        address=addresses[key],
                        data='%02d'%int(value)
                    )

                    print 'Sending', command, 'from', key, value
                    self.send_command(command, port=self.port)
                    print 'command sent'



class CISCamera(Camera):
    pass
