from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:database@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def get_blog_list():
	return Blog.query.all()


@app.route('/newpost', methods=['GET'])
def newpost():

	# Hard time refreshing with previously typed

	return render_template('newpost.html', page_title='Add a Blog')


@app.route('/blog', methods=['GET', 'POST'])
def index():

	if request.method == 'GET':
		if request.args.get('id'):
		
			blog_id = request.args.get('id')
			blog_title = Blog.query.filter_by(id=blog_id).first()
			#title = blog_title.title
			blog_body = Blog.query.filter_by(id=blog_id).first()
			#body = blog_body.body

			title = str(blog_title.title)
			body = str(blog_body.body)

			return render_template('blog.html', blog_list=get_blog_list(), 
			page_title='Blog', blog_id=blog_id, title=title, body=body)

		else:
			return render_template('blog.html', blog_list=get_blog_list())

	if request.method == 'POST':

		title = request.form['title']
		body = request.form['body']

		if not title or not body:

			#PROBLEM WITH FLASH

			flash('Please make sure to enter a title and body for your blog')
			return redirect('/newpost')

		else:

			blog_post = Blog(title=title, body=body)

			db.session.add(blog_post)
			db.session.commit()

			blog_post = Blog.query.filter_by(title = title).first()

			return render_template('blog.html', blog_list=get_blog_list(), 
			page_title='Blog', blog_id=blog_post.id, title=blog_post.title, body=blog_post.body)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
	app.run()