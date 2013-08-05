import flask
#import functools

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