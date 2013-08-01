from flask import render_template, flash, redirect
from app import app
from forms import NewFtpForm
import subprocess
import json
import string, os, random
import tempfile

DATA_BAG='music_upload'
DATA_BAG_ITEM='upload_users-dev'

@app.route('/')
@app.route('/index')
def index():
  return render_template("index.html",
                          title = 'Home'
			)

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
    ftp_users[new_user] = pwd
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
  _, tmp_file = tempfile.mkstemp()
  tmp_file = open(tmp_file, 'w')
  tmp_file.write(json.dumps(ftp_users))
  tmp_file.close()
  try:
    knife_args = ["knife", "data", "bag", "from", 
                  "file", DATA_BAG, tmp_file,
                  "--secret-file=/etc/chef/encrypted_data_bag_secret"
                  ]
    app.logger.debug("Knife_args in save_users_to_chef: " + ' '.join(knife_args))
    ftp_users = subprocess.check_output(knife_args)
    ftp_users = json.loads(ftp_users)
  except:
    flash('Unexpected knife error:')
    return redirect('/index')
  os.unlink(tmp_file.name)
  return 

# Save users dict to temp file, then upload to chef server
def save_users_to_git(new_user):
  USERS_FILE="repo/data_bags/" + DATA_BAG + "/" + DATA_BAG_ITEM + ".json"
  ftp_users = load_users(encryption_required = False)
  
  # TODO save file and git commit/push
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