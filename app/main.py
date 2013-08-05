import flask, flask.views
import os
from app import app

class Main(flask.views.MethodView):
  def get(self, page="index"):
    page += ".html"
    app.logger.debug("Looking for page: " + page)
    if os.path.isfile('app/templates/' + page):
      return flask.render_template(page)
    app.logger.debug("Could not find page: " + page)
    flask.abort(404)