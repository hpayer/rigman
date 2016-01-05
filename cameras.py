import serial
from collections import OrderedDict
from wtforms import BooleanField, IntegerField, FloatField, StringField, SelectField, FormField
from wtforms import validators
from wtforms import widgets
from wtforms import Form
from wtforms.widgets import HTMLString, html_params
# from wtforms_html5 import NumberRange
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField

class Camera(object):

    @property
    def port(self):
        raise NotImplemented('not impllemented')

    # def execute(self, command, camera_id='all'):
    #     ser = serial.Serial(self.port)
    #     result = ser.write(self.commands[command])
    #     ser.close()

    def execute(self, command, camera_id='all'):
        print command, camera_id


class ToggleWidget(widgets.CheckboxInput):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-toggle', 'toggle')
        # kwargs.setdefault('data-size', 'mini')
        kwargs.setdefault('data-width', '45%')
        kwargs.setdefault('data-height', '30')
        kwargs['float'] = 'left'
        return super(ToggleWidget, self).__call__(field, **kwargs)


class ToggleField(BooleanField):
    widget = ToggleWidget()


class RangeInputWithNumber(object):
    html_params = staticmethod(html_params)

    def __init__(self, step=None):
        self.step = step

    def __call__(self, field, **kwargs):
        number_kwargs = kwargs.copy()

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'range')
        kwargs.update(
            oninput="UpdateRangeText(value, id)",
            name=field.name
        )


        number_kwargs.setdefault('id', 'selected-%s'%field.id)
        number_kwargs.setdefault('type', 'number')
        number_kwargs.update( {
            'class_' : "form-control",
            'for' : field.id,
        })
        number_kwargs.update(
            oninput="UpdateRangeSlider(value, id)",
            name=field.name + '_number'
        )

        if 'value' not in kwargs:
            kwargs['value'] = field._value()
            number_kwargs['value'] = field._value()

        range_html = HTMLString('<input %s>' % self.html_params(**kwargs))
        number_html = HTMLString('<input %s>' % self.html_params(**number_kwargs))
        return '<div class="col-xs-3">%s</div><div class="col-xs-3">%s</div>'%(number_html, range_html)
        # return number_html + range_html


class IntegerRangeWithNumberField(IntegerRangeField):
    widget = RangeInputWithNumber()


class SliderForm(Form):
    slider = IntegerRangeField(
            label="",
                validators=[
                    validators.Required(),
                    validators.NumberRange(min=1, max=100, message='no no no!')
                ],
                default=100
            )
    number = IntegerField(label="")

# class IntegerRangeWithNumberField

class IMICamera(Camera):
    # _commands = dict(
    #     up='01',
    #     down='02',
    #     left='03',
    #     right='04',
    #     enter='00',
    #     # wb = dict(
    #     #     values= []
    #     #         atw=5
    #     # )
    # )
    # port = '/dev/ttyUSB0'

    pages = dict(
        remote=OrderedDict(
            camera_id=SelectField(
                    "Camera ID",
                    choices=[(c, c) for c in ['all', 1, 2, 3, 4, 5, 6]]
            ),
            port=SelectField("port", [('usb0', 'usb0')])
        ),
        registers=OrderedDict(
            white_balance_mode=SelectField(
                "White Balance Mode",
                choices=[(0, 'ATW'), (1, 'AWC'), (2, 'INDOOR'), (3, 'OUTDOOR'), (4, 'MANUAL'), (5, 'AWB')]
            ),
            manual_blue_gain=IntegerRangeWithNumberField(
                label="Blue Gain",
                validators=[
                    validators.Required(),
                    validators.NumberRange(min=1, max=100, message='no no no!')
                ],
                default=100
            ),
            manual_red_gain=IntegerRangeWithNumberField(
                label="Red Gain",
                validators=[
                    validators.Required(),
                    validators.NumberRange(min=1, max=100, message='no no no!')
                ],
                default=100
            ),
            boolean=ToggleField(label='Boolean'),
        )
    )



    @property
    def commands(self):
        return dict([(key, '#OKC=%s\r' % value) for key, value in self._commands.iteritems()] )


class CISCamera(Camera):
    pass
