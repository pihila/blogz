from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogit@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

@app.before_request
def require_login():
    not_allowed_routes = ['newpost']
    if request.endpoint  in not_allowed_routes and 'user_name' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():


    user_names = User.query.all()
    return render_template('bloguser.html',title="Blog users!", 
        user_names=user_names)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        user = User.query.filter_by(user_name=user_name).first()
        if user and user.password == password:
            session['user_name'] = user_name
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        verify = request.form['verify']
        if not user_name:
            flash('Username is required', 'error')
            return render_template('register.html')
        if not password:
            flash('Password is required', 'error')
            return render_template('register.html')
        if not verify :
            flash('Verify  is required', 'error')
            return render_template('register.html')
        if len(password)!=8:
            flash('password must be 8 character long', 'error')
            return render_template('register.html')
        if len(user_name) < 8:
            flash('user name must be at least 8 characters long')
            return render_template('register.html')
        if password  != verify:
            flash('Password must match Verify') 
            return render_template('register.html')

        existing_user = User.query.filter_by(user_name=user_name).first()
        if not existing_user:
            new_user = User(user_name, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        else:
        
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['user_name']
    return redirect('/')

@app.route('/blog', methods=['POST', 'GET'])
def blog():


    blogs = Blog.query.all()
    return render_template('blog.html',title="All Blogz!", 
        blogs=blogs)

@app.route('/print_blog', methods=['GET','POST'])
def print_blog():

    blog_id = request.args.get('id')
    new_blog = Blog.query.get(blog_id)
    return render_template('post.html',  new_blog=new_blog)

@app.route('/userblog', methods=['POST', 'GET'])
def userblog():
    
    owner_id= User.query.get(request.args.get('id'))
    blogs = Blog.query.filter_by(owner=owner_id).all()


    #blogs=Blog.query.filter_by(owner=owner).all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
        
        
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            owner_id = User.query.filter_by(user_name=session['user_name']).first()

            if title=="" or body=="":
                flash("title or body can't be empty!" , 'error')
            else:
                new_blog = Blog(title, body, owner_id)
                db.session.add(new_blog)
                db.session.commit()
                blog = Blog.query.get(new_blog.body)
                return render_template('post.html', new_blog=new_blog)


        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()