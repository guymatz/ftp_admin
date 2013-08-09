import flask
from flask import flash, redirect
from app import app
import subprocess
import json
import os
import string
import random
import git
import types
#from config import DATA_BAG, DATA_BAG_ITEM, REPO_DIR
#import functools

DATA_BAG=app.config['DATA_BAG']
DATA_BAG_ITEM=app.config['DATA_BAG_ITEM']
REPO_DIR=app.config['REPO_DIR']
ADMIN_DB=app.config['ADMIN_DB']

def login_required(method):
  #@functools.wraps(method)
  def wrapper(*args, **kwargs):
    if 'username' in flask.session:
      return method(*args, **kwargs)
    else:
      flask.flash("A login is required to see the page!")
      return flask.redirect(flask.url_for('login'))
  return wrapper

def load_users(encryption_required = True):
  knife_args = []
  try:
    app.logger.debug("Is the error here?")
    knife_args = ["knife", "data", "bag", "show",
                        DATA_BAG,
                        DATA_BAG_ITEM,
                        "-f", "json"]
    app.logger.debug("Or here?")
    if encryption_required:
       knife_args.append("--secret-file=/etc/chef/encrypted_data_bag_secret")
    app.logger.debug("Knife_args: " + str(knife_args))
    ftp_users = subprocess.check_output(knife_args)
    app.logger.debug("Can't be here!")
  except Exception, e:
    raise e
  try:
    ftp_users = json.loads(ftp_users)
  except Exception, e:
    raise e
  return ftp_users

def load_admins():
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

def admin_check(admin_user):
  try:
    ADMIN_DB='admins.json'
    current_user = flask.session['username']
    app.logger.debug("In load_admins")
    db = open(ADMIN_DB).read()
    jdb = json.loads(db)
    app.logger.debug("In load_admins, admin_user = " + admin_user)
    app.logger.debug("In load_admins, admin_user's admin status = " + jdb[admin_user]['admin'])
    if jdb[admin_user]['admin'] and jdb[admin_user]['admin'] == 'True':
      app.logger.debug("In load_admins, jdb[admin_user]['admin'] = " + jdb[admin_user]['admin'])
      return True
    else:
      app.logger.debug("In load_admins, jdb[admin_user]['admin'] = " + jdb[admin_user]['admin'])
      return False
  except Exception, e:
    raise Exception("Error checking for admin user:" + str(e) )

# persist the user to databag, chef server, git, etc.
def persist_users(new_user, ftp_users, crud_process):
  try:
    save_users_to_chef(ftp_users)
    save_users_to_git(new_user, crud_process)
  except Exception, e:
    raise e

# Save users dict to temp file, then upload to chef server
def save_users_to_chef(ftp_users):
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

def save_users_to_git(user, crud_process):
  app.logger.debug("In git")
  # location of the file in the git repo
  REPO_FILE = "data_bags/" + DATA_BAG + "/" + DATA_BAG_ITEM + ".json"
  # file on th FS
  USERS_FILE= REPO_DIR + "/" + REPO_FILE
  app.logger.debug("Users file: " + USERS_FILE)
  ftp_users = load_users(encryption_required = False)
  app.logger.debug("Just got ftp_users")
  # Update git
  try:
    app.logger.debug("REPO_DIR = " + REPO_DIR)
    repo = git.Repo(REPO_DIR)
  except Exception, e:
    raise e
  try:
    current_branch = get_current_branch(repo)
  except Exception, e:
    raise e

  try:
    app.logger.debug("Now a pull to " + current_branch)
    repo.git.pull("origin", current_branch)
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
    commit_string='FTP account ' + crud_process + ' by ' + 'username ' + ':'  + str(user)
    repo.git.commit(m=commit_string)
    app.logger.debug("git add/commit successful: " + commit_string)
  except Exception, e:
    app.logger.debug("Tried git add/commit: " + commit_string)
    raise e
  # TODO change username above to the currently logged in user
  # TODO push changes to master
  return

def new_random_password():
  app.logger.debug("Generating password . . .")
  PWD_LENGTH = 8
  chars = string.ascii_letters + string.digits + '!@#$%^&*()'
  random.seed = (os.urandom(1024))
  pwd = ''.join(random.choice(chars) for i in range(PWD_LENGTH))
  return pwd

def user_exists(new_user, hash_of_users):
  # lower-case everything and check for dupes
  new_user = new_user.lower()
  hash_of_users = {k.lower():v for k,v in hash_of_users.items()}
  if new_user in hash_of_users:
    return True
  else:
    return False
    

# persist the admin in a simple json file
def persist_admins(new_user,admin_users):
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

def get_current_branch(repo):
  branches = repo.git.branch().split('\n')
  for b in branches:
    if b.startswith('*'):
      return b.split(' ')[1]