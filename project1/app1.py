from flask import Flask,render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jungle'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)
@app.route("/")
def HomePage():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()
    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)


@app.route('/article/<string:id>')
def article(id):
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    return render_template('article.html', article=article)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=50)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    remember_me = BooleanField('Remember me.')

#User Register
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s, %s, %s, %s)",(name, email, username, password))

        #Commit to DB
        mysql.connection.commit()

        #Close connecction
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html',form=form)
#user login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        #get user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # Compare password
            if sha256_crypt.verify(password_candidate,password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# For checking whether login or not
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# Log out
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('HomePage'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM articles")

        articles = cur.fetchall()
        if result > 0:
            return render_template('dashboard.html', articles=articles)
        else:
            msg = 'No Articles Found'
            return render_template('dashboard.html', msg=msg)
    else:
        return redirect(url_for('login'))

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title',[validators.Length(min=1,max=200)])
    body = TextAreaField('Body',[validators.Length(min=30)])

@app.route('/add_article',methods=['GET','POST'])
def add_article():
    if 'logged_in' in session:
        form = ArticleForm(request.form)
        if request.method == 'POST':
            title = form.title.data
            body = form.body.data

            #create curonnection
            cur = mysql.connection.cursor()

            cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

            mysql.connection.commit()
            cur.close()

            flash('Article Created','success')
            return redirect(url_for('dashboard'))
        return render_template('add_article.html',form=form)
    else:
        return redirect(url_for('login'))

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()
    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)
        # Execute
        cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


#delete article
@app.route('/delete_article/<string:id>',methods=['POST'])
def delete_article(id):
    cur= mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id = %s",[id])
    mysql.connection.commit()
    cur.close()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.secret_key='shoot123'
    app.run(debug=True)
