from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
from flask_wtf import FlaskForm
from flask_admin import Admin, AdminIndexView, BaseView, expose
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired, NumberRange
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_wtf.file import FileField, FileAllowed
import os
import secrets
from PIL import Image
import bcrypt

# Initialize Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["MONGO_URI"] = "mongodb://localhost:27017/ecommerce_db"

# Initialize PyMongo
mongo = PyMongo(app)

# Setup Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Custom Admin Views for MongoDB
class CustomAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.role == "admin":
            return self.render("admin/index.html")
        else:
            flash("You are not the admin!", "danger")
            return redirect(url_for("home"))

class UserAdminView(BaseView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.role == "admin":
            users = mongo.db.users.find()
            return self.render("admin/user_admin.html", users=users)
        else:
            flash("You are not authorized to access this page!", "danger")
            return redirect(url_for("home"))

class ProductAdminView(BaseView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.role == "admin":
            products = mongo.db.products.find()
            return self.render("admin/product_admin.html", products=products)
        else:
            flash("You are not authorized to access this page!", "danger")
            return redirect(url_for("home"))

# Initialize Flask Admin with Custom Index View
admin = Admin(app, index_view=CustomAdminIndexView())
admin.add_view(UserAdminView(name="User Admin"))
admin.add_view(ProductAdminView(name="Product Admin"))

# User model
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.password = user_data["password"]
        self.city = user_data["city"]
        self.image = user_data.get("image", "default.jpg")
        self.role = user_data.get("role", "user")

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# FlaskForm for Login
class LoginForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired(), Email()], render_kw={"placeholder": "Please enter your email:"})
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=5, max=60)], render_kw={"placeholder": "Please enter your password:"})
    rememberme = BooleanField("Remember me")
    submit = SubmitField("Login")

# FlaskForm for Registration
class RegisterForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired(), Email()], render_kw={"placeholder": "Please enter your email:"})
    username = StringField("Username:", validators=[DataRequired(), Length(min=5, max=44)], render_kw={"placeholder": "Choose a username:"})
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=5, max=60)], render_kw={"placeholder": "Create a password:"})
    password2 = PasswordField("Confirm password:", validators=[DataRequired(), EqualTo("password")], render_kw={"placeholder": "Retype your password:"})
    city = SelectField("Choose your city", validators=[InputRequired()], choices=["Sarajevo", "Mostar", "Tuzla", "Other"])
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        exists = mongo.db.users.find_one({"username": username.data})
        if exists:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        exists = mongo.db.users.find_one({"email": email.data})
        if exists:
            raise ValidationError('That email is taken. Please choose a different one.')

# FlaskForm for Editing Account
class EditAccountForm(FlaskForm):
    email = StringField("Edit email:", validators=[DataRequired(), Email()])
    username = StringField("Edit username:", validators=[DataRequired(), Length(min=5, max=44)])
    city = SelectField("Change your city", validators=[InputRequired()], choices=["Sarajevo", "Mostar", "Tuzla", "Other"])
    image = FileField("Upload a profile picture:", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("Apply changes")

    def validate_username(self, username):
        user = mongo.db.users.find_one({"_id": {"$ne": ObjectId(current_user.id)}, "username": username.data})
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = mongo.db.users.find_one({"_id": {"$ne": ObjectId(current_user.id)}, "email": email.data})
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

# FlaskForm for Adding Product
class AddProductForm(FlaskForm):
    title = StringField("Enter the name of your product", validators=[DataRequired(), Length(min=5, max=199)])
    image = FileField("Attach a picture of your product", validators=[FileAllowed(["jpg", "png"]), DataRequired()])
    description = TextAreaField("Write a description of your product", validators=[Length(min=5, max=500)])
    price = FloatField("Add your product's price", validators=[DataRequired(), NumberRange(min=1, max=99999.0)])
    submit = SubmitField("Create product!")

# FlaskForm for Searching Products
class SearchForm(FlaskForm):
    searched = StringField(validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("Search!")

# FlaskForm for Ordering Products
class OrderByForm(FlaskForm):
    order_by = SelectField("Order by", validators=[InputRequired()], choices=["Price descending", "Price ascending", "Oldest to newest", "Newest to oldest"])

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    page = int(request.args.get("page", 1))
    form = OrderByForm(request.form)
    query = {}
    sort_field = "created_at"
    sort_direction = -1

    if form.validate_on_submit() and request.method == "POST":
        if form.order_by.data == "Price descending":
            sort_field = "price"
            sort_direction = -1
        elif form.order_by.data == "Price ascending":
            sort_field = "price"
            sort_direction = 1
        elif form.order_by.data == "Oldest to newest":
            sort_field = "created_at"
            sort_direction = 1

    products = mongo.db.products.find(query).sort([(sort_field, sort_direction)]).skip((page - 1) * 15).limit(15)
    return render_template("home.html", title="Home", products=products, form=form)

@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        product_searched = form.searched.data
        products = mongo.db.products.find({"title": {"$regex": product_searched}})
        return render_template("search.html", form=form, title="Search results", query=product_searched, products=products)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in", "warning")
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            login_user(User(user), remember=form.rememberme.data)
            flash(f"Successfully logged in as {user['username']}", "success")
            return redirect(url_for("home"))
        else:
            flash(f"Login failed, please check email and password", "danger")
    return render_template("login.html", form=form, title="Login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in", "warning")
        return redirect(url_for("home"))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = {
            "username": form.username.data,
            "password": hashed,
            "email": form.email.data,
            "city": form.city.data
        }
        mongo.db.users.insert_one(user)
        flash("Account created!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form, title="Register")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.", "info")
    return redirect(url_for("home"))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/product_pics', picture_fn)

    output_size = (800, 800)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = EditAccountForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data)
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.city = form.city.data
        mongo.db.users.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"username": current_user.username, "email": current_user.email, "city": current_user.city, "image": current_user.image}})
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.city.data = current_user.city
    image_file = url_for('static', filename='product_pics/' + current_user.image)
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.image.data)
        product = {
            "title": form.title.data,
            "image": picture_file,
            "description": form.description.data,
            "price": form.price.data,
        }
        mongo.db.products.insert_one(product)
        flash(f'Your product has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('add_product.html', title='Add Product', form=form)

@app.route("/product/<string:product_id>", methods=["GET", "POST"])
def product(product_id):
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    return render_template('product.html', title=product['title'], product=product)

@app.route("/product/<string:product_id>/update", methods=["GET", "POST"])
@login_required
def update_product(product_id):
    form = AddProductForm()
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    if form.validate_on_submit():
        picture_file = save_picture(form.image.data)
        mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": {
            "title": form.title.data,
            "image": picture_file,
            "description": form.description.data,
            "price": form.price.data,
        }})
        flash('Your product has been updated!', 'success')
        return redirect(url_for('product', product_id=product_id))

    form.title.data = product['title']
    form.description.data = product['description']
    form.price.data = product['price']
    return render_template('add_product.html', title='Update Product', form=form)

@app.route("/product/<string:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
