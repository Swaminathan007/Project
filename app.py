from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/project'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(80), unique=True, nullable=False)
    content = db.Column(db.String(5000), unique=True, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(80),nullable=False)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")
@app.route("/signup",methods = ["GET","POST"])
def signup():
    if(request.method == "POST"):
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")
        if(cpassword != password):
            flash("Passwords doesn't match")
        if(User.query.filter_by(username=name).first()):
            flash("Username taken already")
        if(User.query.filter_by(email=email).first()):
            flash("Email take already")
        else:
            user = User(username = name,email=email,password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("/success")
    return render_template("signup.html")
@app.route("/success")
def success():
    return render_template("success.html")
@app.route("/login",methods = ["GET","POST"])
def login():
    if(request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email = email).first()
        if(user and user.password == password):
            login_user(user)
            return redirect("/logged")
        else:
            flash("Incorrect credentials")
    return render_template("login.html")
@app.route("/logged")
@login_required
def logged():
    posts = Post.query.filter_by(email = current_user.email).all()
    return render_template("userpage.html",posts = posts)
@app.route("/createpost",methods = ["GET","POST"])
@login_required
def create():
    if(request.method == "POST"):
        header = request.form.get("header")
        text = request.form.get("content")
        post = Post(header=header,content=text,email=current_user.email,time=datetime.now())
        db.session.add(post)
        db.session.commit()
        flash("Post created")
        return redirect("/logged")
    return render_template("create.html")
@app.route("/view/<int:id>")
@login_required
def view(id):
    post = Post.query.filter_by(id=id).first()
    return render_template("view.html",post=post)
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Post Deleted")
    return redirect("/logged")
@app.route("/update/<int:id>",methods = ["GET","POST"])
@login_required
def update(id):
    post = Post.query.filter_by(id=id).first()
    if(request.method == "POST"):
        header = request.form.get("header")
        text = request.form.get("content")
        post.header = header
        post.content = text
        db.session.commit()
        flash("Post updated")
        return redirect("/logged")
    return render_template("update.html",post=post)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
if __name__ == "__main__":
    app.run(debug = True,host="0.0.0.0")