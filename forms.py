
from flask_wtf import Form
from wtforms import widgets
from wtforms import TextField, PasswordField, SelectField, BooleanField, SubmitField
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


class RemoteForm(Form):
    port = SelectField(
            label='Port:',
            choices=[("COM%d" % port, "COM%d" % port) for port in xrange(0, 10)]
    )

    ids = [('All', 'all')]
    ids.extend([(id, id) for id in xrange(1, 53)])

    camera_id = SelectField(
            label='Camera ID:',
            choices=ids
    )


class MultiViewForm(Form):
    port = SelectField(
            label='Port:',
            choices=[("COM%d" % port, "COM%d" % port) for port in xrange(0, 10)]
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


class CommandButtonWidget(object):

    html = """
    <button type="button" class="btn btn-default btn-lg2 {icon}" data-toggle="modal" role="dialog" data-target="#{command}">{label}</button>

    <div class="modal fade" id="{command}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title" id="myModalLabel">Rigman</h4>
          </div>
          <div class="modal-body">
            <h4>{message}</h4>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
            <button type="button" name="command" class="btn btn-default btn-primary" data-dismiss="modal" value="{command}" onClick="command_click(this)">Ok</button>
          </div>
        </div>
      </div>
    </div>
    """
    html_old = """
    <button type="button" name="command" class="btn btn-default btn-mxlarge {icon}" value="{command}" onClick="command_click(this)">
    </button>
    """

    def __init__(self, input_type='button'):
        self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString(self.html.format(
                icon=field.icon,
                command=field.command,
                message=field.message,
                label=field.label,
        ))  # , title=field.title))


class CommandButtonField(BooleanField):
    widget = CommandButtonWidget()

    def __init__(self, label=None, validators=None, false_values=None, icon='', command='', title='', message='',
                 **kwargs):
        super(CommandButtonField, self).__init__(label, validators, **kwargs)

        self.icon = icon
        # if not self.icon:
        #     self.
        self.command = command
        self.title = title
        self.message = message


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

        number_kwargs.setdefault('id', 'selected-%s' % field.id)
        number_kwargs.setdefault('type', 'number')
        number_kwargs.update({
            'class_': "form-control",
            'for': field.id,
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
        return '<div class="col-xs-3">%s</div><div class="col-xs-3">%s</div>' % (number_html, range_html)


class IntegerRangeWithNumberField(IntegerRangeField):
    def __init__(self, label=None, validators=None, minimum=1, maximum=100, **kwargs):
        self.widget = RangeInputWithNumber(step=1, minimum=minimum, maximum=maximum)
        super(IntegerRangeWithNumberField, self).__init__(label, validators, **kwargs)
