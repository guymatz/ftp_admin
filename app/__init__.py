from flask import Flask
import flask.views

app = Flask(__name__)
app.config.from_object('config')

#from app import views
from main import Main
from list_ftp import ListFTP
from new_ftp import NewFTP

app.add_url_rule('/', 
				view_func=Main.as_view('main'))

app.add_url_rule('/<page>/',
                view_func=Main.as_view('main'))

app.add_url_rule('/ftp/list',
				view_func=ListFTP.as_view('ftp_users'),
				methods=['GET'])

app.add_url_rule('/ftp/new',
				view_func=NewFTP.as_view('new_ftp_user'),
				methods=['GET', 'POST'])

@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('404.html'), 404
