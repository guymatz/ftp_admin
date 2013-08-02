from flask import render_template, flash, redirect
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

@app.route('/')
@app.route('/index')
def index():
  return render_template("index.html",
                          title = 'Home'
			)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  form = LoginForm()
  # Check to see if we're getting a post
  if form.validate_on_submit():
    # Load in users from chef and check to see if we're putting in a duplicate
    #app_users = load_app_users()
    app_users = {'admin': 'admin'}
    login_user = form.username.data
    login_pwd = form.password.data
    app.logger.debug("login_user = " + login_user)
    if login_user not in app_users or login_pwd != app_users[login_user]:
      flash('Sorry!!  Account does not exist or password is wrong . . .')
      return redirect('/login')
    #session[login_user]="Logged In"
    return redirect('/new_ftp')
  # Must be a GET . . .  create form
  return render_template('login.html', title = 'Sign In', form = form)

@app.route('/logout', methods = ['GET'])
def logout():
  session['login_user'] = False
  return render_template('login.html', title = 'Sign In', form = form)

@app.route('/new_ftp', methods = ['GET', 'POST'])
def new_ftp():
  form = NewFtpForm()
  # Check to see if we're getting a post
  if form.validate_on_submit():
    # Load in users from chef and check to see if we're putting in a duplicate
    ftp_users = load_users()
    new_user = form.ftp_username.data
    app.logger.debug("new_user = " + new_user)
    if user_exists(new_user, ftp_users):
      flash('FTP account for ' + new_user + ' already exists!')
      return redirect('/new_ftp')
    # Generate password (see below) and return back to ftp, displaying new pwd
    pwd = new_random_password()
    app.logger.debug(new_user + "=" + pwd)
    app.logger.debug("ftp_users has this many entries:" + str(len(ftp_users)))
    ftp_users[new_user] = { "password": pwd }
    persist_users(new_user, ftp_users)
    flash('FTP account for ' + new_user + ' created!  Password is ' + pwd)
    return redirect('/new_ftp')
  # Must be a GET . . .  create form
  return render_template('new_ftp.html', title = 'Sign In', form = form)

@app.route('/list_ftp', methods = ['GET'])
def list_ftp():
  ftp_users = load_users()
  return render_template('ftp_users.html', title = 'FTP Users', ftp_users = ftp_users)

def load_users(encryption_required = True):
  try:
    knife_args = ["knife", "data", "bag", "show", DATA_BAG, "-f",
                  "json", DATA_BAG_ITEM ]
    if encryption_required:
       knife_args.append("--secret-file=/etc/chef/encrypted_data_bag_secret")
    app.logger.debug("Knife_args: " + ' '.join(knife_args))
    ftp_users = subprocess.check_output(knife_args)
    ftp_users = json.loads(ftp_users)
  except:
    raise Exception("Error getting databag with knife using:" + 
      ' '.join(knife_args))
  return ftp_users

# persist the user to databag, chef server, git, etc.
def persist_users(new_user,ftp_users):
  try:
    save_users_to_chef(ftp_users)
    save_users_to_git(new_user)
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

def save_users_to_git(new_user):
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
    repo.git.commit(m='FTP account added by ' + 'username ' + ':'  + new_user)
  except Exception, e:
    app.logger.debug("Tried git add/commit")
    #raise e
  # TODO change username above to the currently logged in user
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
