from flask import render_template, flash, redirect
from app import app
from forms import NewFtpForm
import subprocess
import json
import string, os, random
import tempfile

@app.route('/')
@app.route('/index')
def index():
  user = { 'nickname': 'Carlos Danger' }

  return render_template("index.html",
                          title = 'Home',
                          user = user
			)

@app.route('/new_ftp', methods = ['GET', 'POST'])
def new_ftp():
  form = NewFtpForm()
  # Check to see if we're getting a post
  if form.validate_on_submit():
    # Load in users from chef and cehck to see if we're putting in a duplicate
    ftp_users = load_users()
    ftp_username = form.ftp_username.data
    app.logger.debug("ftp_username = " + ftp_username)
    if ftp_username in ftp_users:
      flash('FTP account for ' + ftp_username + ' already exists!')
      return redirect('/index')
    # Generate password (see below) and return home, displaying new pwd
    pwd = new_random_password()
    app.logger.debug(ftp_username + "=" + pwd)
    app.logger.debug("ftp_users has this many entries:" + str(len(ftp_users)))
    ftp_users[form.ftp_username.data] = pwd
    save_users(ftp_users)
    flash('FTP account for ' + form.ftp_username.data + ' created!  Password is ' + pwd)
    return redirect('/new_ftp')
  # Must be a GET . . .  create form
  return render_template('new_ftp.html', title = 'Sign In', form = form)

@app.route('/list_ftp', methods = ['GET'])
def list_ftp():
  ftp_users = load_users()
  return render_template('ftp_users.html', title = 'FTP Users', ftp_users = ftp_users)

def load_users():
  try:
    knife_args = ["knife", "data", "bag", "show", "music_upload", "-f",
                  "json", "upload_users",
                  "--secret-file=/etc/chef/encrypted_data_bag_secret"
                  ]
    ftp_users = subprocess.check_output(knife_args)
    ftp_users = json.loads(ftp_users)
  except:
    flash('Unexpected error:')
    return redirect('/index')
  return ftp_users

def save_users(ftp_users):
  try:
    save_users_to_chef(ftp_users)
    save_users_to_git()
  except Exception, e:
    raise e
  

# Save users dict to temp file, then upload to chef server
def save_users_to_chef(ftp_users):
  _, tmp_file = tempfile.mkstemp()
  tmp_file = open(tmp_file, 'w')
  tmp_file.write(json.dumps(ftp_users))
  tmp_file.close()
  return
  try:
    knife_args = ["knife", "data", "bag", "from", 
                  "file", "music_upload", tmp_file,
                  "--secret-file=/etc/chef/encrypted_data_bag_secret"
                  ]
    ftp_users = subprocess.check_output(knife_args)
    ftp_users = json.loads(ftp_users)
  except:
    flash('Unexpected knife error:')
    return redirect('/index')
  os.unlink(tmp_file.name)
  return 

# Save users dict to temp file, then upload to chef server
def save_users_to_git():
  USERS_FILE="repo/data_bags/music_upload/upload_users.json"
  ftp_users = load_users()
  # TODO save file and git commit/push
  return

def new_random_password():
  app.logger.debug("Generating password . . .")
  PWD_LENGTH = 8
  chars = string.ascii_letters + string.digits + '!@#$%^&*()'
  random.seed = (os.urandom(1024))
  pwd = ''.join(random.choice(chars) for i in range(PWD_LENGTH))
  return pwd