import flask, flask.views
from app import app

users = {'admin': {'password':'admin', 'admin':'True'}, 'gmatz':  {'password':'gmatz', 'admin':'False'}}

class Login(flask.views.MethodView):
  def get(self):
    return flask.render_template('login.html')

  def post(self):
    if 'logout' in flask.request.form:
      flask.session.pop('username', None)
      flask.session.pop('admin', None)
      return flask.redirect(flask.url_for('main'))
    required = ['username','password']
    app.logger.debug("required = " + required[0] + " & " + required[1])
    for r in required:
      if r not in flask.request.form or flask.request.form[r] == "":
        flask.flash("Error: {0} is required.".format(r))
        return flask.redirect(flask.url_for('login'))
    username = flask.request.form['username']
    password = flask.request.form['password']
    app.logger.debug("username = " + username)
    if username in users and users[username]['password'] == password:
      app.logger.debug("password = " + password)
      app.logger.debug("users[username]['password'] = " + users[username]['password'])
      flask.session['username'] = username
      app.logger.debug("admin status = " + users[username]['admin'])
      if users[username]['admin'] == 'True':
        app.logger.debug("users[username]['admin'] = " + users[username]['admin'])
        flask.session['admin'] = 'True'
    else:
      app.logger.debug("password after = " + password)
      flask.flash("Username doesn't exist or incorrect password")
      return flask.redirect(flask.url_for('login'))
    return flask.redirect(flask.url_for('new_ftp_user'))

  def load_admins(self):
    ADMIN_DB='admins.json'
    db = open(ADMIN_DB).read()
    jdb = json.loads(db)
    return jdb
