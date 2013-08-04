import flask, flask.views
from app import app

users = {'admin': {'password':'admin', 'admin':'True'} }

class Login(flask.views.MethodView):
  def get(self):
    return flask.render_template('index.html')

  def post(self):
  	if 'logout' in flask.request.form:
  		flask.session.pop('username', None)
  		return flask.redirect(flask.url_for('main'))
  	required = ['username','password']
  	app.logger.debug("required = " + required[0])
  	for r in required:
  		if r not in flask.request.form:
  			flask.flash("Error: {0} is required.".format(r))
  			return flask.redirect(flask.url_for('main'))
  	username = flask.request.form['username']
  	password = flask.request.form['password']
  	app.logger.debug("username = " + username)
  	if username in users and users[username]['password'] == password:
  		app.logger.debug("password = " + password)
  		app.logger.debug("users[username]['password'] = " + users[username]['password'])
  		flask.session['username'] = username
  	else:
  		app.logger.debug("password after = " + password)
  		flask.flash("Username doesn't exist or incorrect password")
  		return flask.redirect(flask.url_for('main'))
  	return flask.redirect(flask.url_for('new_ftp_user'))
