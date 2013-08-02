from flask import Flask
import flask.views

app = Flask(__name__)
app.config.from_object('config')

#from app import views
from index import Index
from list_ftp import ListFTP
from new_ftp import NewFTP

app.add_url_rule('/', view_func=Index.as_view('main'))
app.add_url_rule('/ftp/list', view_func=ListFTP.as_view('ftp_users'), methods=['GET'])
app.add_url_rule('/ftp/new', view_func=NewFTP.as_view('new_ftp_user'), methods=['GET', 'POST'])