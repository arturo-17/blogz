from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz2017@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'tssfgre4353DSFs'

class Blog(db.Model):

    blog_id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_content = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, blog_title, blog_content, owner):
        self.blog_title = blog_title
        self.blog_content = blog_content
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(25), unique = True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        login_username_error = ""

        if user and user.password == password:
            session['username'] = username
            #flash("Welcome back, " + username)
            return redirect('/newpost')
        else:
            login_error = "No user by this username or password is incorrect"
            return render_template("login.html", login_error=login_error)

    return render_template('login.html')

    if request.method == 'GET':
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ""
    password_error = ""
    verify_password_error = ""
    user_exists_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        if len(username) < 3 or len(username) > 20:
            flash('please enter a user name more then 3 characters')
            #username_error = "Please enter a username between 3 and 50 chr"

            return render_template("signup.html", username_error=username_error)

        if " " in username:
            flash('Username cannot contain spaces')

            #username_error = "Username cannot contain spaces"
            return render_template("signup.html", username_error=username_error)

        if len(password) < 3 or len(password) > 20:
            flash('Please enter a password between 3 and 50 chr')
            #password_error = "Please enter a password between 3 and 50 chr"
            return render_template("signup.html", password_error=password_error)

        if " " in password:
            flash('password cannot have spaces')
            #password_error = "Password cannot contain space"
            return render_template("signup.html", password_error=password_error)

        if password != verify_password:
            flash('passowords dont match')
            #verify_password_error = "Password and verify password must be the same"
            return render_template("signup.html", verify_password_error=verify_password_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            user_exists_error = "Username already exists"
            return render_template("signup.html", user_exists_error=user_exists_error)

    return render_template('signup.html', username_error=username_error, password_error=password_error, verify_password_error=verify_password_error)

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out")

    return redirect('/blog')



@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users)







@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.args.get('id'):
        blog_id = request.args.get('id')
        post = Blog.query.get(blog_id)
        owner_id = request.args.get('id')
        owner = Blog.query.get(owner_id)
        return render_template('post.html', post=post, owner=owner)

    
    if request.args.get('user'):
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        posts = user.blogs
        return render_template('user.html', posts=posts, user=user)
    
    if request.method == 'POST':
        blog_title = request.form['blog_entry_title']
        blog_content = request.form['blog_entry_content']

        if not blog_title or not blog_content:
            flash('Please fill in both fields', 'error')
            return render_template('newpost.html')

        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Blog(blog_title, blog_content, owner)
            db.session.add(new_post)
            db.session.commit()
            new_post = Blog.query.filter_by(blog_title=blog_title).first()

            return redirect('/blog?id={0}'.format(new_post.blog_id))

            

    posts = Blog.query.all()
    users = User.query.all()

    return render_template('blog.html', posts=posts, users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()

