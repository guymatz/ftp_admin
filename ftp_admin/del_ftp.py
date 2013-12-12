from flask import render_template, flash, redirect
import flask, flask.views
from ftp_admin import app
import subprocess
import json
import utils

class DeleteFTP(flask.views.MethodView):
  @utils.login_required
  def get(self):
    ftp_users = utils.load_users(encryption_required=True)
    return render_template('del_ftp_users.html', title='Delete FTP Users', ftp_users=ftp_users)

  # TODO Remove this in favor of method in utils.  Remember to change call above!
  @utils.login_required
  def post(self):
    users_to_del = flask.request.form.getlist('del_list')
    app.logger.debug("users to del = " + str(users_to_del) )
    all_users = utils.load_users(encryption_required=True)
    app.logger.debug("all_users size = " + str(len(all_users)) )
    for u in users_to_del:
      all_users.pop(u)
    app.logger.debug("all_users size = " + str(len(all_users)) )
    utils.persist_users(users_to_del, all_users, "deleted")
    flask.flash("FTP Accounts have been deleted: " + json.dumps(users_to_del) )
    return redirect('/ftp/list')
