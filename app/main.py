import flask, flask.views
import os
from app import app

class Main(flask.views.MethodView):
  def get(self, page="index"):
    if os.path.isfile('app/static/' + page):
      return flask.url_for('static', filename=page)
    elif os.path.isfile('app/templates/' + page + '.html'):
      return flask.render_template(page + '.html')
    app.logger.debug("Could not find page: " + page)
    flask.abort(404)