from flask import Flask, render_template, redirect, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///Login_Exercise"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "NickDesilets"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()




"""HOME"""

@app.route('/', methods=["GET"])
def home():

    return redirect("/login")

"""REGISTER/LOGIN"""

@app.route('/register', methods=['GET', 'POST'])
def register_user():

    form=RegisterForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username,password, email, first_name, last_name)

        db.session.commit()
        session['username'] = user.username

        return redirect(f"/users/{user.username}")

    else:

        return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():

    form = LoginForm()

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username,password)

        if user:
            flash(f"Welcome Back, {user.username}!")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        
        else:
            form.username.error = ["Invalide username or password"]

    return render_template("login.html", form=form)

"""USER ROUTES"""

@app.route("/users/<username>", methods=["GET"])
def show_user(username):

    if 'username' not in session:
        flash("Please login first")
    
    user = User.query.get(username)
    form = FeedbackForm()

    return render_template("show.html", user=user, form=form)


@app.route('/users/<username>/feedback/post', methods=["GET","POST"])
def post_feedback(username):

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback.html", form=form)

"""EDITING/DELETING FEEDBACK"""
@app.route('/feedback/<int:feedback_id>/edit')
def feedback_edit(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("edit.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    else:
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")





"""LOGOUT/DELETE"""

@app.route('/logout', methods=["GET"])
def logout_user():

    session.pop("username")
    return redirect("/login")



@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):

    user = User.query.get_or_404(username)
    
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")