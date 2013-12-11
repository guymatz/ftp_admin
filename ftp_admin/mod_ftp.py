from flask import render_template, flash, redirect
import flask, flask.views
#from app import app
import utils

class ModifyFTP(flask.views.MethodView):
  @utils.login_required
  def get(self):
    ftp_users = utils.load_users(encryption_required=True)
    return render_template('mod_ftp_users.html', title='Change FTP User', ftp_users=ftp_users)

  def post(self):
  	ftp_users = utils.load_users(encryption_required=True)
  	users_to_mod = flask.request.form.getlist('mod_list')
  	app.logger.debug("users to mod = " + str(users_to_mod) )
  	for user in users_to_mod:
  		new_password = flask.request.form[user + '_password']
  		app.logger.debug(user + '=' + new_password)
  		new_media_type = flask.request.form[user + '_media_type']
  		app.logger.debug(user + '=' + new_media_type)
  		if new_password != "":
  			ftp_users[user]['password'] = new_password
  		if new_media_type != "":
  			ftp_users[user]['media_type'] = new_media_type
  	utils.persist_users(users_to_mod, ftp_users, 'modified')
  	flask.flash("Users Modified: " + str(users_to_mod))
  	return redirect(flask.url_for('ftp_users'))
