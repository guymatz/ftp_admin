from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required

class NewFtpForm(Form):
  ftp_username = TextField('ftp_account', validators = [Required()] )
  remember_me = BooleanField('remember_me', default = False)
