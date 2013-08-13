from flask.ext.wtf import Form, TextField, BooleanField, PasswordField
from flask.ext.wtf import Required

class NewFtpForm(Form):
  ftp_username = TextField('ftp_account', validators = [Required()] )
  remember_me = BooleanField('remember_me', default = False)

class LoginForm(Form):
  username = TextField('username', validators = [Required()] )
  password = PasswordField('password', validators = [Required()] )
