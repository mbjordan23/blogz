from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:database@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():

	allowed_routes = ['login', 'signup']

	if request.endpoint not in allowed_routes and 'username' not in session:
		return redirect('/login')


def get_user_blog_list(user_id):
	
	owner = User.query.filter_by(id=user_id).first()

	blog_list = Blog.query.filter_by(owner=owner).all()

	return blog_list


def get_blog_list():
	blog_list = Blog.query.all()
	return blog_list

@app.route('/newpost', methods=['GET'])
def newpost():

	return render_template('newpost.html', page_title='Add a Blog')

@app.route('/login', methods=['GET', 'POST'])
def login():

	if request.method == 'GET':
		return render_template('login.html')

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()


		if user and user.password == password:

			session['username'] = username

			return redirect('/newpost')

		if user:
			flash('Incorrect password')
			return redirect('/login')
		else:
			flash('User does not exist')
			return redirect('/login')


	return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

	if request.method == 'GET':
		return render_template('signup.html')

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		verify = request.form['verify']


		if User.query.filter_by(username=username).first():
			flash('Username is already taken')
			return render_template('signup.html')
		elif username == '':
			flash('Username cannot be blank')
			return render_template('signup.html', username=username)
		elif ' ' in username == True:
			flash('Invalid username - no spaces')
			return render_template('signup.html', username=username)
		else:
			if len(username) > 20 or len(username) < 3:
				flash('Username must be between 3 and 20 characters')
				return render_template('signup.html', username=username)

		if password == '':
			flash('Please enter a password')
			return render_template('signup.html', username=username)
		elif ' ' in password == True:
			flash('Invalid password - no spaces')
			return render_template('signup.html', username=username)
		elif password != verify:
			flash('Passwords do not match')
			return render_template('signup.html', username=username)
		else:
			if len(password) > 20 or len(password) < 3:
				flash('Password must be between 3 and 20 characters')
				return render_template('signup.html', username=username)


		new_user = User(username, password)
		
		db.session.add(new_user)
		db.session.commit()

		session['username'] = username

		return redirect('/newpost')


@app.route('/logout')
def logout():
	del session['username']
	return redirect('/blog')

@app.route('/')
def home():
	users = User.query.all()
	return render_template('index.html', users=users)


@app.route('/blog', methods=['GET', 'POST'])
def index():

	if request.method == 'GET':
		if request.args.get('id'):
		
			blog_id = request.args.get('id')
			blog_title = Blog.query.filter_by(id=blog_id).first()
			blog_body = Blog.query.filter_by(id=blog_id).first()
		
			title = str(blog_title.title)
			body = str(blog_body.body)
		
			return render_template('blog.html', page_title='Blog', 
				blog_id=blog_id, title=title, body=body)

		
		user_id = request.args.get('userid')

		if request.args.get('userid'):
	
			
			blog_owner = User.query.filter_by(id=user_id).first()
			blog_title = Blog.query.filter_by(owner_id=user_id).first()
			blog_body = Blog.query.filter_by(owner_id=user_id).first()

			title = str(blog_title.title)
			body = str(blog_body.body)
			owner = (blog_owner.username)

			return render_template('user_posts.html', user=blog_owner, page_title='Blog', 
				title=title, body=body, blog_list=get_user_blog_list(user_id))

		else:

			return render_template('blog.html', blog_list=get_blog_list())

	owner = User.query.filter_by(username=session['username']).first()

	if request.method == 'POST':

		title = request.form['title']
		body = request.form['body']

		if not title or not body:

			flash("Please make sure to enter a title and body for your blog")
			return render_template('newpost.html', title=title, body=body)

		else:

			blog_post = Blog(title=title, body=body, owner=owner)

			db.session.add(blog_post)
			db.session.commit()

			blog_post = Blog.query.filter_by(title = title, owner=owner).first()

			return redirect('/blog?id=' + str(blog_post.id))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
	app.run()