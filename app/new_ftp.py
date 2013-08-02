from flask import render_template, flash, redirect
import flask, flask.views
from app import app
from forms import NewFtpForm, LoginForm
import subprocess
import json
import string, os, random
import tempfile
import git

DATA_BAG='music_upload'
DATA_BAG_ITEM='upload_users-dev'
REPO_DIR='repo'

class NewFTP(flask.views.MethodView):
  def get(self):
    return flask.render_template('new_ftp.html', title='Create New FTP User')
  def post(self):
    # Maybe use this later?
    # form = NewFtpForm()
    # Check to see if we're valid
    #f not flask.request.form.validate_on_submit():
    #  flask.flash("Invalid username")
    #  return self.get
    # Load in users from chef and check to see if we're putting in a duplicate
    ftp_users = self.load_users()
    new_user = flask.request.form['ftp_username']
    app.logger.debug("new_user = " + new_user)
    if self.user_exists(new_user, ftp_users):
      flash('FTP account for ' + new_user + ' already exists!')
      return self.get()
    # Generate password (see below) and return back to ftp, displaying new pwd
    pwd = self.new_random_password()
    app.logger.debug(new_user + "=" + pwd)
    app.logger.debug("ftp_users has this many entries:" + str(len(ftp_users)))
    ftp_users[new_user] = { "password": pwd }
    self.persist_users(new_user, ftp_users)
    flash('FTP account for ' + new_user + ' created!  Password is ' + pwd)
    return self.get()
    
  def load_users(self, encryption_required=True):
    try:
      app.logger.debug("In load_users")
      knife_args = ["knife", "data", "bag", "show", DATA_BAG, DATA_BAG_ITEM,
                    "-f", "json",  ]
      if encryption_required:
         knife_args.append("--secret-file=/etc/chef/encrypted_data_bag_secret")
      app.logger.debug("Knife_args: " + ' '.join(knife_args))
      ftp_users = subprocess.check_output(knife_args)
      ftp_users = json.loads(ftp_users)
    except Exception, e:
      raise e
    return ftp_users  

  # persist the user to databag, chef server, git, etc.
  def persist_users(self, new_user,ftp_users):
    try:
      self.save_users_to_chef(ftp_users)
      self.save_users_to_git(new_user)
    except Exception, e:
      raise e

  # Save users dict to temp file, then upload to chef server
  def save_users_to_chef(self, ftp_users):
    app.logger.debug("Saving users to chef server")
    tmp_file = '/tmp/tmp.FTP_ADMIN.json'
    tf = open(tmp_file, 'w')
    tf.write(json.dumps(ftp_users))
    tf.close()
    try:
      knife_args = ["knife", "data", "bag", "from", 
                    "file", DATA_BAG, tmp_file,
                    "--secret-file=/etc/chef/encrypted_data_bag_secret"
                    ]
      app.logger.debug("Knife_args in save_users_to_chef: " + ' '.join(knife_args))
      ftp_users = subprocess.check_output(knife_args)
      #ftp_users = json.loads(ftp_users)
    except:
      flash('Unexpected knife error:')
    finally:
      os.unlink(tmp_file)
      return redirect('/index')
    return 

  def save_users_to_git(self, new_user):
    app.logger.debug("In git")
    # location of the file in the git repo
    REPO_FILE = "data_bags/" + DATA_BAG + "/" + DATA_BAG_ITEM + ".json"
    # file on th FS
    USERS_FILE= REPO_DIR + "/" + REPO_FILE
    app.logger.debug("Users file: " + USERS_FILE)
    ftp_users = self.load_users(encryption_required = False)
    app.logger.debug("Just got ftp_users")
    # Update git
    try:
      app.logger.debug("REPO_DIR = " + REPO_DIR)
      repo = git.Repo(REPO_DIR)
    except Exception, e:
      raise e
    try:
      app.logger.debug("Now a pull")
      repo.git.pull()  
    except Exception, e:
      raise e

    # get unexcrypted users
    try:
      knife_args = ["knife", "data", "bag", "show",
                    DATA_BAG, DATA_BAG_ITEM, "-f", "json"
                    ]
      app.logger.debug("Knife_args in save_users_to_git: " + ' '.join(knife_args))
      output = subprocess.check_output(knife_args)
    except Exception, e:
      raise e
    try:
      app.logger.debug("In git write")
      f = open(USERS_FILE, 'w')
    except:
      raise Exception("Could not open file: " + USERS_FILE)
    try:
      f.write(output)
      f.close()
    except:
      raise Exception("Could write to file")
    app.logger.debug("Here in git?")
    try:
      repo.git.add(REPO_FILE)
      commit_string='FTP account added by ' + 'username ' + ':'  + new_user
      repo.git.commit(m=commit_string)
      app.logger.debug("git add/commit successful: " + commit_string)
    except Exception, e:
      app.logger.debug("Tried git add/commit: " + commit_string)
      raise e
    # TODO change username above to the currently logged in user
    return


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