from flask import render_template, flash, redirect
import flask, flask.views
from app import app
import subprocess
import json
import utils

DATA_BAG='music_upload'
DATA_BAG_ITEM='upload_users-dev'
REPO_DIR='repo'

class ListFTP(flask.views.MethodView):
  @utils.login_required
  def get(self):
    ftp_users = self.load_users(encryption_required=True)
    return render_template('ftp_users.html', title='FTP Users', ftp_users=ftp_users)

  # TODO Remove this in favor of method in utils.  Remember to change call above!
  def load_users(self, encryption_required=True):
      try:
        app.logger.debug("In load_users")
        knife_args = ["knife", "data", "bag", "show", DATA_BAG, DATA_BAG_ITEM,
                      "-f", "json",  ]
        if encryption_required:
           knife_args.append("--secret-file=/etc/chef/encrypted_data_bag_secret")
        app.logger.debug("Knife_args: " + ' '.join(knife_args))
        ftp_users = subprocess.check_output(knife_args)
        ftp_users = json.loads(ftp_users)
      except:
        raise Exception("Error getting databag with knife using:" + 
          ' '.join(knife_args))
      return ftp_users