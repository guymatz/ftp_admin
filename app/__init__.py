from flask import Flask
import flask.views

app = Flask(__name__)
app.config.from_object('config')

#from app import views
from main import Main
from login import Login
from list_ftp import ListFTP
from del_ftp import DeleteFTP
from new_ftp import NewFTP
from list_admins import ListAdmins
from new_admin import NewAdmin

app.add_url_rule('/', 
				view_func=Main.as_view('main'))

app.add_url_rule('/<page>/',
                view_func=Main.as_view('main'))

app.add_url_rule('/login', 
				view_func=Login.as_view('login'),
				methods=['GET', 'POST'])

app.add_url_rule('/ftp/list',
				view_func=ListFTP.as_view('ftp_users'),
				methods=['GET'])

app.add_url_rule('/ftp/new',
				view_func=NewFTP.as_view('new_ftp_user'),
				methods=['GET', 'POST'])

app.add_url_rule('/ftp/del',
				view_func=DeleteFTP.as_view('del_ftp_users'),
				methods=['GET', 'POST'])

app.add_url_rule('/admin/list',
				view_func=ListAdmins.as_view('list_admins'),
				methods=['GET'])

app.add_url_rule('/admin/new',
				view_func=NewAdmin.as_view('new_admin'),
				methods=['GET', 'POST'])

@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('404.html'), 404
