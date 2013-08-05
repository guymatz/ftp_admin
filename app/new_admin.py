from flask import render_template, flash, redirect
import flask, flask.views
from app import app
#from forms import NewFtpForm
import subprocess
import json
import string, os, random
import tempfile
import git
import utils
#import functools

ADMIN_DB='admins.json'

class NewAdmin(flask.views.MethodView):
  @utils.login_required
  def get(self):
    return flask.render_template('new_admin.html', title='Create Admin User')

  @utils.login_required
  def post(self):
    # Maybe use this later?
    # form = NewFtpForm()
    # Check to see if we're valid
    #f not flask.request.form.validate_on_submit():
    #  flask.flash("Invalid username")
    #  return self.get
    # Load in users from chef and check to see if we're putting in a duplicate
    admin_users = self.load_admins()
    new_admin = flask.request.form['admin_username']
    app.logger.debug("Checking. . .")
    app.logger.debug("is_admin = " + str( flask.request.form.getlist('is_admin') ) )
    if str( flask.request.form.getlist('is_admin') ) == 'on':
      admin_status = 'True'
    else:
      admin_status = 'False'
    app.logger.debug("What about here?")
    app.logger.debug("new_admin = " + new_admin)
    if self.user_exists(new_admin, admin_users):
      flash('Admin account for ' + new_admin + ' already exists!')
      return self.get()
    # Generate password (see below) and return back to ftp, displaying new pwd
    pwd = self.new_random_password()
    app.logger.debug(new_admin + "=" + pwd)
    admin_users[new_admin] = { "admin": admin_status, "password": pwd }
    self.persist_admins(new_admin, admin_users)
    flash('Admin account for ' + new_admin + ' created!  Password is ' + pwd)
    return self.get()
    
  def load_admins(self):
    try:
      app.logger.debug("Loading json from " + ADMIN_DB)
      db = open(ADMIN_DB).read()
    except Exception, e:
      raise e
    try:
      app.logger.debug("Converting to JSON")
      app.logger.debug("db = " + db)
      jdb = json.loads(db)
    except Exception, e:

      raise e
    return jdb

  # persist the user to databag, chef server, git, etc.
  def persist_admins(self, new_user,admin_users):
    try:
      f = open(ADMIN_DB, 'w')
    except Exception, e:
      raise e
    try:
      f.write( json.dumps(admin_users, indent=2) )
    except Exception, e:
      raise e
    finally:
      f.close

  def new_random_password(self):
    app.logger.debug("Generating password . . .")
    PWD_LENGTH = 8
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    pwd = ''.join(random.choice(chars) for i in range(PWD_LENGTH))
    return pwd

  def user_exists(self, new_user, hash_of_users):
    # lower-case everything and check for dupes
    new_user = new_user.lower()
    hash_of_users = {k.lower():v for k,v in hash_of_users.items()}
    if new_user in hash_of_users:
      return True
    else:
      return False
