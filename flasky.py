# coding:utf-8
from flask import Flask

from flask import request # 请求上下文 请求内容
from flask import session # 请求上下文 用户会话 cookie

from flask import url_for # url生成函数
from flask import make_response # 生成响应
from flask import render_template # 模板渲染组件

from flask import redirect # 重定位
from flask import abort # 警告
from flask import flash

#from flask.ext.script import Shell
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.bootstrap import Bootstrap # 前端框架
from flask.ext.moment import Moment # 本地化时间框架
from flask.ext.sqlalchemy import SQLAlchemy #
from flask.ext.wtf import Form # 表单基类
from wtforms import StringField, SubmitField # 文本字段，提交按钮
from wtforms.validators import Required # 验证函数-确保字段中有数据

from datetime import datetime
import os


app = Flask(__name__)


# 配置
#app.config['CSRF'] = True
app.config['SECRET_KEY'] = 'fuck my life, life is bullshit' # 防止跨站点请求伪造密匙
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')

app.config['MAIL_SERVER'] = 'smtp.sina.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('wslshanlin@Sina.com')
app.config['MAIL_PASSWORD'] = os.environ.get('Wls994180438')

app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'


mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# 视图
@app.route('/', methods=['GET', 'POST'])
def index():	
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			session['known'] = False
			if app.config['FLASKY_ADMIN']: # 有新用户时发送电子邮件给管理员
				send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		#form.name.data = ''
		return redirect(url_for('index'))
	return render_template('index.html',
		current_time=datetime.utcnow(),
		form=form,
		name=session.get('name'),
		known=session.get('known', False))
	#return redirect('http://www.baidu.com/')	
	#response = make_response('<h1>This document carries a cookie!</h1>')
	#response.set_cookie('answer', '42')
	#return response
	#return '<h1>Bad Request</h1>', 400
	#user_agent = request.headers.get('User_Agent') #获取文件头用户浏览器信息
	#return '<p>Your browser is {0}</p>'.format(user_agent)
	#return '<h1>Hello world!</h1>'


@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name) # 模板渲染
	#return '<h1>Hello, {0}!</h1>'.format(name)


@app.route('/user/<id>')
def get_user(id):
	user = load_user(id)
	if not user:
		abort(404) # 提示错误信息
	return '<h1>你好, {0}</h1>'.format(user.name)


@app.errorhandler(404)
def page_not_find(e):
	return render_template('404.html'), 404


# 表单
class NameForm(Form):
	name = StringField(u'你的姓名?', validators=[Required()])
	submit = SubmitField(u'提交')


# 数据库
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role')

	def __repr__(self):
		return '<Role {0}>'.format(self.name)


class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User {0}>'.format(self.username)


'''
def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
'''


def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, 
		sender=app.config[FLASKY_MAIL_SENDER],
		recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	mail.send(msg)


if __name__ == '__main__':
	manager.run()
	app.debug = True
	app.run()	