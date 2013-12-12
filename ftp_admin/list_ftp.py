from flask import render_template, flash, redirect
import flask, flask.views
from ftp_admin import app
import utils

class ListFTP(flask.views.MethodView):
  @utils.login_required
  def get(self):
    ftp_users = utils.load_users(encryption_required=True)
    return render_template('ftp_users.html', title='FTP Users', ftp_users=ftp_users)
