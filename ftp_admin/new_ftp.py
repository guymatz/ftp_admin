from flask import render_template, flash, redirect
import flask, flask.views
from ftp_admin import app
#from forms import NewFtpForm
import datetime
import utils
#from config import DATA_BAG, DATA_BAG_ITEM, REPO_DIR
#import functools

class NewFTP(flask.views.MethodView):
  @utils.login_required
  def get(self):
    return flask.render_template('new_ftp.html', title='Create FTP User')

  @utils.login_required
  def post(self):
    # Maybe use this later?
    # form = NewFtpForm()
    # Check to see if we're valid
    #f not flask.request.form.validate_on_submit():
    #  flask.flash("Invalid username")
    #  return self.get
    # Load in users from chef and check to see if we're putting in a duplicate
    ftp_users = utils.load_users()
    new_user = flask.request.form['ftp_username']
    media_type = flask.request.form['media_type']
    app.logger.debug("new_user = " + new_user)
    if new_user == '' or media_type == '':
      flash('Username and Media Type are required!')
      return self.get()
    if utils.user_exists(new_user, ftp_users):
      flash('FTP account for ' + new_user + ' already exists!')
      return self.get()
    # Generate password (see below) and return back to ftp, displaying new pwd
    pwd = utils.new_random_password()
    app.logger.debug(new_user + "=" + pwd)
    app.logger.debug("media_type = " + media_type)
    app.logger.debug("ftp_users has this many entries:" + str(len(ftp_users)))
    ftp_users[new_user] = { "password": pwd,
                            "media_type": media_type,
                            "_comment": "Added by " + flask.session['username'] + " on "
                            + datetime.datetime.now().strftime("%Y-%m-%d %T") }
    utils.persist_users(new_user, ftp_users, 'added')
    flash('FTP account for ' + media_type + ' ' + new_user + ' created!  Password is ' + pwd)
    return self.get()
  
