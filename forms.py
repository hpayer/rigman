from flask_wtf import Form
from wtforms import widgets
from wtforms import TextField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField
from wtforms.widgets import HTMLString, html_params
# Set your classes here.


class RegisterForm(Form):
    name = TextField(
        'Username', validators=[DataRequired(), Length(min=6, max=25)]
    )
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )


class LoginForm(Form):
    name = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])


class ForgotForm(Form):
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )


class RemoteConfig(Form):
    port = SelectField(
        label='Port:',
        choices=[("COM%d"%port, "COM%d"%port) for port in xrange(0,10)]
    )

    ids = [('All', 'all')]
    ids.extend([(id, id) for id in xrange(1, 53)])

    camera_id = SelectField(
        label='Camera ID:',
        choices=ids
    )


class ToggleWidget(widgets.CheckboxInput):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-toggle', 'toggle')
        # kwargs.setdefault('data-size', 'mini')
        kwargs.setdefault('data-width', '45%')
        kwargs.setdefault('data-height', '30')
        kwargs['float'] = 'left'
        return super(ToggleWidget, self).__call__(field, **kwargs)


class ToggleField(BooleanField):
    input_type = 'range'
    widget = ToggleWidget()


class RangeInputWithNumber(object):
    html_params = staticmethod(html_params)

    def __init__(self, step=None, minimum=1, maximum=100):
        self.step = step
        self.min = minimum
        self.max = maximum

    def __call__(self, field, **kwargs):
        number_kwargs = kwargs.copy()
        # number_kwargs.pop('min')
        # number_kwargs.pop('max')
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'range')
        # kwargs.setdefault('min', self.min)
        # kwargs.setdefault('max', self.max)

        kwargs.update(
            oninput="UpdateRangeText(value, id)",
            name=field.name,
            min=self.min,
            max=self.max
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


class IntegerRangeWithNumberField(IntegerRangeField):

    def __init__(self, label=None, validators=None, minimum=1, maximum=100, **kwargs):
        self.widget = RangeInputWithNumber(step=1, minimum=minimum, maximum=maximum)
        super(IntegerRangeWithNumberField, self).__init__(label, validators, **kwargs)


