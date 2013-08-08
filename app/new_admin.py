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
    admin_users = utils.load_admins()
    new_admin = flask.request.form['admin_username']
    app.logger.debug("Checking. . .")
    app.logger.debug("is_admin = " + str( flask.request.form.getlist('is_admin') ) )
    if str( flask.request.form.getlist('is_admin') ) == 'on':
      admin_status = 'True'
    else:
      admin_status = 'False'
    app.logger.debug("What about here?")
    app.logger.debug("new_admin = " + new_admin)
    if utils.user_exists(new_admin, admin_users):
      flash('Admin account for ' + new_admin + ' already exists!')
      return self.get()
    # Generate password (see below) and return back to ftp, displaying new pwd
    pwd = utils.new_random_password()
    app.logger.debug(new_admin + "=" + pwd)
    admin_users[new_admin] = { "admin": admin_status, "password": pwd }
    utils.persist_admins(new_admin, admin_users)
    flash('Admin account for ' + new_admin + ' created!  Password is ' + pwd)
    return self.get()