from flask import Flask,render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

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

        return redirect(url_for('register'))
    return render_template('register.html',form=form)



if __name__ == "__main__":
    app.secret_key='shoot123'
    app.run(debug=True)
