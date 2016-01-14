
from flask_wtf import Form
from wtforms import widgets
from wtforms import TextField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from wtforms.fields.html5 import DecimalRangeField, IntegerRangeField
from wtforms.widgets import HTMLString, html_params


CANCEL_OK_DIALOG_TEMPLATE = """
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

INPUT_DIALOG_TEMPLATE = """
    <div class="modal fade" id="{command}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title" id="myModalLabel">Rigman</h4>
          </div>
          <div class="modal-body">
            <h4 >{message}</h4>
            <p><input type="text" class="span3" name="config_name" id="config_name" placeholder="{config_name}"></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
            <button type="button" name="command" class="btn btn-default btn-primary" data-dismiss="modal" value="{command}" onClick="command_click(this)">Ok</button>
          </div>
        </div>
      </div>
    </div>
"""

DELETE_DIALOG_TEMPLATE = """
    <div class="modal fade" id="{command}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title" id="myModalLabel">Rigman</h4>
          </div>
          <div class="modal-body">
            <h4>{message} </h4>
            <h4 name="config_name" id="delete_config_name"></h4>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
            <button type="button" name="command" class="btn btn-default btn-primary" data-dismiss="modal" value="{command}" onClick="command_click(this)">Ok</button>
          </div>
        </div>
      </div>
    </div>
"""


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
    # input_type = 'range'
    widget = ToggleWidget()
    # widget = widgets.CheckboxInput()



class CommandButtonWidget(object):

    html = """
    <button type="button" class="btn btn-default btn-lg2 {icon}" data-toggle="modal" role="dialog" data-target="#{command}">{label}</button>
    """
    dialog_html = CANCEL_OK_DIALOG_TEMPLATE

    html_old = """
    <button type="button" name="command" class="btn btn-default btn-mxlarge {icon}" value="{command}" onClick="command_click(this)">
    </button>
    """

    def __init__(self, input_type='button', dialog_html=''):
        self.input_type = input_type
        if dialog_html:
            self.dialog_html = dialog_html

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        result_html = self.html + self.dialog_html
        return HTMLString(result_html.format(**field.__dict__
                # icon=field.icon,
                # command=field.command,
                # message=field.message,
                # label=field.label,
        ))  # , title=field.title))


class CommandButtonField(BooleanField):
    widget = CommandButtonWidget()

    def __init__(self, label=None, validators=None, false_values=None, icon='', command='', title='', message='',
                 **kwargs):
        super(CommandButtonField, self).__init__(label, validators, **kwargs)
        self.icon = icon
        self.command = command
        self.title = title
        self.message = message
        self.config_name = ''

class CommandButtonFieldWithInputDialog(CommandButtonField):
    widget = CommandButtonWidget(dialog_html=INPUT_DIALOG_TEMPLATE)


class CommandButtonFieldWithDeleteWarningDialog(CommandButtonField):
    widget = CommandButtonWidget(dialog_html=DELETE_DIALOG_TEMPLATE)



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
        return '<div class="col-xs-4">%s</div><div class="col-xs-4">%s</div>' % (number_html, range_html)


class IntegerRangeWithNumberField(IntegerRangeField):
    def __init__(self, label=None, validators=None, minimum=1, maximum=100, **kwargs):
        self.widget = RangeInputWithNumber(step=1, minimum=minimum, maximum=maximum)
        super(IntegerRangeWithNumberField, self).__init__(label, validators, **kwargs)


class RemoteForm(Form):
    port = SelectField(
            label='Port:',
            choices=[("COM%d" % port, "COM%d" % port) for port in xrange(0, 10)]
    )

    # ids = [('All', 'all')]
    # ids.extend([(id, id) for id in xrange(1, 53)])
    #
    # camera_id = SelectField(
    #         label='Camera ID:',
    #         choices=ids
    # )
    #

    camera_id = IntegerRangeWithNumberField(
        "Camera (-1=All)",
        validators=[
            DataRequired(),
            NumberRange(min=-1, max=255, message='min:%(min)s max%(max)s')
        ],
        minimum=-1,
        maximum=255,
        default=-1
    )