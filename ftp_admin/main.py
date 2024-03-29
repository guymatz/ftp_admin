import flask, flask.views
import os
from ftp_admin import app

class Main(flask.views.MethodView):
  def get(self, page="index"):
    if os.path.isfile('static/' + page):
      return flask.url_for('static', filename=page)
    elif os.path.isfile('templates/' + page + '.html'):
      return flask.render_template(page + '.html')
    app.logger.debug("Could not find page: " + page)
    flask.abort(404)
