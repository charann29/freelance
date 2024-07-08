from flaskmarketplace import app,db, bcrypt
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from flaskmarketplace.models import * 
from flaskmarketplace.forms import (LoginForm, RegisterForm,AddProductForm, EditAccountForm, 
                                EditProductForm, SearchForm,CommentForm, ReviewForm, OrderByForm)
import os, secrets
from PIL import Image


# sorting this way because i didnt want to use js in this project
@app.route("/", methods=["GET","POST"])
@app.route("/home", methods=["GET","POST"])
def home(): 
    page = request.args.get("page", 1, type=int)
    form=OrderByForm(request.form)
    if form.validate_on_submit() and request.method=="POST":
        if form.order_by.data=="Price descending":
                products=db.session.query(Product).order_by(Product.price.asc()).paginate(page=page, per_page=15)
        elif form.order_by.data=="Price ascending":
            products=db.session.query(Product).order_by(Product.price.desc()).paginate(page=page, per_page=15)
        elif form.order_by.data=="Oldest to newest":
            products=db.session.query(Product).order_by(Product.created_at.asc()).paginate(page=page, per_page=15)
        else:
            products=db.session.query(Product).order_by(Product.created_at.desc()).paginate(page=page, per_page=15)
    else:
        products = db.session.query(Product).order_by(Product.created_at.desc()).paginate(page=page,per_page=15)
    return render_template("home.html", title="Home", products=products, form=form)

@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route("/search", methods=["POST"])
def search():
    form=SearchForm()
    if form.validate_on_submit():
        product_searhced=form.searched.data
        products=db.session.query(Product).filter(Product.title.like(product_searhced)).all()
        return render_template("search.html",form=form,
                            title="Search results", query=product_searhced, products=products)


@app.route("/about")
def about():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in", "warning")
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user=db.session.query(User).filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user=user,remember=form.rememberme.data)
            flash(f"Succesuly logged in as {user.username}","success")
            return redirect(url_for("home"))
        else:
            flash(f"Login failed, please check email and password","danger")
    return render_template("login.html", form=form, title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in", "warning")
        return redirect(url_for("home"))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed=bcrypt.generate_password_hash(form.password2.data).decode("utf-8")
        user=User(username=form.username.data, password=hashed,
                  email=form.email.data, city=form.city.data, location=form.city.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created!","success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form, title="Register")


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You are now logged out.","info")
        return redirect(url_for("home"))
    else:
        flash("You are not logged in.", "info")
        return url_for("login")


def save_pic(input_pic, location):
    random=secrets.token_hex(16)
    pic_name=random+input_pic.filename
    pic_path=os.path.join(app.root_path,f"static/{location}", pic_name)

    pic_size=(300,300)
    image=Image.open(input_pic)
    image.thumbnail(pic_size)
    image.save(pic_path)

    return pic_name


def delete_pic(folder,pic_name):
    try:
        todelete=os.path.join(app.root_path,f"static/{folder}/{pic_name}")
        os.remove(todelete)
    except Exception as e:
        flash(f"Deleting failed")


@app.route("/myaccount", methods=["GET","POST"])
@login_required
def myaccount():
    myproducts=db.session.query(Product).filter_by(user_id=current_user.user_id).all()
    form = EditAccountForm(email=current_user.email, username=current_user.username,
                           city=current_user.city)
    if request.method=="POST":
        if form.validate_on_submit():
            file=save_pic(form.image.data, location="profile_pics")
            current_user.image=file
            print(form.image.data.filename)
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for("myaccount"))
    return render_template("myaccount.html", title="Account", form=form, products=myproducts)
   

@app.route("/deleteacc")
@login_required
def delete_account():
    user=db.session.query(User).filter_by(user_id=current_user.user_id).first()
    products=db.session.query(Product).filter_by(user_id=current_user.user_id).all()
    comments=db.session.query(Comment).filter_by(user_id=current_user.user_id).all()
    reviews=db.session.query(Review).filter_by(user_id=current_user.user_id).all()
    incart=db.session.query(Cart).filter_by(user_id=current_user.user_id).all()
    if comments:
        for comment in comments:
            db.session.delete(comment)
            db.session.commit()
    if reviews:
        for review in reviews:
            db.session.delete(review)
            db.session.commit()
    if incart:
        for item in incart:
            db.session.delete(item)
            db.session.commit()
    if products:
        for product in products:
            db.session.delete(product)
            db.session.commit()
            delete_pic("product_pics",product.image)
    try:
        if current_user.image!="default.jpg":
            delete_pic("profile_pics",current_user.image)
        db.session.delete(user)
        db.session.commit()
        flash(f"Account {user.username} deleted!", "success")
        return redirect(url_for("home"))
    except:
        db.session.rollback()
        flash("Error deleting account", "warning")

    return redirect(url_for("home"))


@app.route("/add_product", methods=["GET","POST"])
@login_required
def add_product():
    form=AddProductForm()
    if form.validate_on_submit():
        if form.image.data:
            filename=save_pic(form.image.data, location="product_pics")
            product=Product(user_id=current_user.user_id,title=form.title.data,image=filename,
            description=form.description.data,price=form.price.data)
        else:
            product=Product(user_id=current_user.user_id,title=form.title.data,image=form.image.data,
            description=form.description.data,price=form.price.data)
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully!","success")
        return redirect(url_for("home"))
    return render_template("addproduct.html",title="Add product", form=form)


@app.route("/delete_product/<int:product>")
@login_required
def delete_product(product):
    product_todelete=db.session.query(Product).filter_by(product_id=product).first()
    if product_todelete:
        if current_user.user_id==product_todelete.user_id:
            try:
                comments=db.session.query(Comment).filter_by(product_id=product).all()
                reviews=db.session.query(Review).filter_by(product_id=product).all()
                for i in comments:
                    db.session.delete(i)
                for i in reviews:
                    db.session.delete(i)
                db.session.commit()
                db.session.delete(product_todelete)
                db.session.commit()
                delete_pic("product_pics",product_todelete.image)
                flash(f"Product deleed successfully!","success")
                return redirect(url_for("home"))
            except:
                flash("There was an error in deleting the product")
        else:
            flash("You are not the product owner.","warning")
            return redirect(url_for("home"))
    else:
        flash("No product under this id","warning")
        return redirect(url_for("home"))
    return redirect(url_for("home"))


@app.route("/edit_product/<int:product>", methods=["GET","POST"])
@login_required
def edit_product(product):
    product=db.session.query(Product).filter_by(product_id=product).first()
    if not product:
        flash("No product under this name","warning")
        return redirect(url_for("home"))
    if current_user.user_id!=product.user_id:
        flash("You are not the product owner","warning")
        return redirect(url_for("home"))
    form = EditProductForm(title=product.title,description=product.description, price=product.price)
    if request.method=="POST":
        if form.validate_on_submit():
            if form.image.data:
                delete_pic("product_pics",product.image)
                filename=save_pic(form.image.data, location="product_pics")
            product.title=form.title.data 
            product.description=form.description.data
            product.price=form.price.data
            product.image=filename
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for("home"))
    return render_template("editproduct.html",form=form, title="Edit post", product=product)


@app.route("/view_account/<int:user_id>")
def view_account(user_id):
    if current_user.is_authenticated and current_user.user_id==user_id:
        return redirect(url_for("myaccount"))
    user=db.session.query(User).filter_by(user_id=user_id).first()
    products=db.session.query(Product).filter_by(user_id=user_id).all()
    return render_template("view_account.html", user=user, products=products, title=f"viewing: {user.username}")


@app.route("/view_product/<int:product_id>")
def view_product(product_id):
    product=db.session.query(Product).filter_by(product_id=product_id).first()
    comments=db.session.query(Comment).filter_by(product_id=product_id).all()
    reviews=db.session.query(Review).filter_by(product_id=product_id).all()
    return render_template("view_product.html", product=product,comments=comments,reviews=reviews)


@app.route("/add_comment/<int:product_id>", methods=["GET","POST"])
@login_required
def add_comment(product_id):
    exists=db.session.query(Comment).filter_by(user_id=current_user.user_id, product_id=product_id).first()
    if exists:
        flash("You have already left a comment on this product","danger")
        return redirect(url_for("view_product",product_id=product_id))
    form=CommentForm()
    product=db.session.query(Product).filter_by(product_id=product_id).first()
    if form.validate_on_submit():
        comment=Comment(user_id=current_user.user_id, content=form.content.data, product_id=product_id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("view_product",product_id=product_id))
    return render_template("add_comment.html", form=form, product=product)


@app.route("/add_review/<int:product_id>", methods=["GET","POST"])
@login_required
def add_review(product_id):
    exists=db.session.query(Review).filter_by(user_id=current_user.user_id, product_id=product_id).first()
    if exists:
        flash("You have already left a review for this product","danger")
        return redirect(url_for("view_product",product_id=product_id))
    form=ReviewForm()
    product=db.session.query(Product).filter_by(product_id=product_id).first()
    if form.validate_on_submit():
        review=Review(user_id=current_user.user_id, rating=form.content.data, product_id=product_id)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for("view_product",product_id=product_id))
    return render_template("add_review.html", form=form, product=product)


#takes query objects as arguments 
def buy_product_func(product,seller,user):
    if user.balance<product.price:
        flash(f"Transaction failed - your balance:{user.balance}, product price: {product.price}")
        raise InvalidFundsException 
    if user.user_id==product.user_id:
        flash("You are the owner of this item","warning")
        return
    seller.balance+=product.price
    user.balance-=product.price
    db.session.commit()
    delete_pic("product_pics",product.image)


class InvalidFundsException(Exception):
    "You do not have sufficient funds for this transaction"


@app.route("/buy_product/<int:product_id>")
@login_required
def buy_product(product_id):
    product=db.session.query(Product).filter_by(product_id=product_id).first()
    seller=db.session.query(User).filter_by(user_id=product.user_id).first()
    if current_user.user_id==product.user_id:
        flash("You are the owner of this product","danger")
        return redirect(url_for("home"))
    price=product.price
    if current_user.balance>=price:
        buy_product_func(product,seller,current_user)
        db.session.delete(product)
        db.session.commit()
        flash("Product bought!", "success")
    else:
        flash("You dont have the funds to buy this product.","danger")
    return redirect(url_for("home"))


@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    product=db.session.query(Product).filter_by(product_id=product_id).first()
    if db.session.query(Cart).filter_by(user_id=current_user.user_id, product_id=product_id).first():
        flash("You already have this product in your cart","warning")
        return redirect(url_for("mycart"))
    if current_user.user_id==product.user_id:
        flash("You are the owner of this product","warning")
        return redirect(url_for("home"))
    if not db.session.query(Product).filter_by(product_id=product_id).first():
        flash("This product doesnt exist","warning")
        return redirect(url_for("home"))
    if current_user.balance<product.price:
        flash("You do not have the funds to buy this product","danger")
    cart_obj=Cart(product_id=product.product_id, user_id=current_user.user_id)
    db.session.add(cart_obj)
    db.session.commit()

    flash(f"Added to cart: {product.title}","success") 
    return redirect(url_for("mycart"))


@app.route("/buy_all")
@login_required
def buy_all():
    mycart=db.session.query(Cart).filter_by(user_id=current_user.user_id).all()
    products=[db.session.query(Product).filter_by(product_id=prod.product_id).first() for prod in mycart]
    total_price=sum([product.price for product in products])
    if total_price>current_user.balance:
        flash("You do not have enough funds to buy all products","danger")
        return redirect(url_for("mycart"))
    if not mycart:
        flash("No items in your cart!")
        return redirect(url_for("home"))
    try:
        for i in products:
            product=db.session.query(Product).filter_by(product_id=i.product_id).first()
            seller=db.session.query(User).filter_by(user_id=product.user_id).first()
            buy_product_func(seller=seller,product=product,user=current_user)
            db.session.delete(product)
            db.session.commit()
    except Exception as e:
        flash(f"Error {e}","danger")
    else:
        flash("Success!","success")
    return redirect(url_for("home"))


@app.route("/delete_from_cart/<int:product_id>")
@login_required
def delete_from_cart(product_id):
    mycart=db.session.query(Cart).filter_by(user_id=current_user.user_id).all()
    products=[db.session.query(Cart).filter_by(product_id=prod.product_id).first() for prod in mycart]
    todelete=db.session.query(Cart).filter_by(product_id=product_id).first()
    if todelete in products:
        db.session.delete(todelete)
        db.session.commit()
    else:
        flash("This product is not in your cart!","danger")
    return redirect(url_for("mycart"))


@app.route("/mycart")
@login_required
def mycart():
    mycart=db.session.query(Cart).filter_by(user_id=current_user.user_id).all()
    products=[db.session.query(Product).filter_by(product_id=prod.product_id).first() for prod in mycart]
    return render_template("mycart.html",products=products,title="Cart")