import flask, flask.views

class Index(flask.views.MethodView):
  def get(self):
    return flask.render_template('index.html')