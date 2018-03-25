from flask import render_template,flash,redirect,url_for,request
from app import app,db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user,login_user, login_required,logout_user
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime
from app.forms import EditProfileForm


@app.route('/')
@app.route('/index')
@login_required #protect this function..
def index():
    user = {'username':'extreme45nm'}
    posts = [
        {
            'author':{'username':'John'},
            'body':'Beautiful day in Portland'
        },
        {
            'author':{'username':'Susan'},
            'body':'pornhub is an amazing site'
        }
    ]
    return render_template('index.html',title="home",posts = posts)

@app.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_pass(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        #flash("login requested for user {}, remember_me = {}".format(form.username.data,form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html',title="Sign In",form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_pass(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('congratz, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)


@app.route('/user/<username>')#this time uses a dynamic component
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts=[
        {'author':user, 'body':'Test post #1'},
        {'author':user, 'body':'Test post #2'}
    ]
    return render_template('user.html',user=user,posts=posts)


@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("your fookin change have been saved")
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',title='Edit Profile',form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
