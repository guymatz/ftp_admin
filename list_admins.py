from flask import render_template, flash, redirect
import flask, flask.views
from app import app
import json
import utils



class ListAdmins(flask.views.MethodView):
  @utils.login_required
  def get(self):
    admin_users = utils.load_admins()
    app.logger.debug("In get, admin_user = " + str(admin_users) )
    return render_template('admin_users.html', title='Admin Users', admin_users=admin_users)