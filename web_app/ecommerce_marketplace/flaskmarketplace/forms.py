from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                BooleanField, TextAreaField, SelectField, FloatField)
from wtforms.validators import (DataRequired, Length, Email, EqualTo,
                ValidationError, Optional, InputRequired, NumberRange)
from flaskmarketplace import db
from flaskmarketplace.models import User
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user


class LoginForm(FlaskForm):
    email=StringField("Email:",validators=[DataRequired(), Email()], render_kw={"placeholder":"Please enter your email:"})
    password=PasswordField("Password:", validators=[DataRequired(), Length(min=5,max=60)], render_kw={"placeholder":"Please enter your password:"})
    rememberme=BooleanField("Remember me")
    submit=SubmitField("Login")


class RegisterForm(FlaskForm):
    email=StringField("Email:",validators=[DataRequired(), Email()], render_kw={"placeholder":"Please enter your email:"})
    username=StringField("Username:",validators=[DataRequired(), Length(min=5,max=44)], render_kw={"placeholder":"Choose a username:"})
    Password=PasswordField("Password:", validators=[DataRequired(), Length(min=5,max=60)], render_kw={"placeholder":"Create a password:"})
    password2=PasswordField("Confirm password:", validators=[DataRequired(), EqualTo("Password")], render_kw={"placeholder":"Retype your password:"})
    city=SelectField("Choose your city", validators=[InputRequired()], choices=["Sarajevo","Mostar","Tuzla","Other"])
    submit=SubmitField("Sign up")

    def validate_username(self, username):
        exists = db.session.query(User).filter_by(username=username.data).first()
        if exists:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        exists = db.session.query(User).filter_by(email=email.data).first()
        if exists:
            raise ValidationError('That email is taken. Please choose a different one.')


class EditAccountForm(FlaskForm):
    email=StringField("Edit email:",validators=[DataRequired(), Email()])
    username=StringField("Edit username:",validators=[DataRequired(), Length(min=5,max=44)])
    city=SelectField("Change your city", validators=[InputRequired()], choices=["Sarajevo","Mostar","Tuzla","Other"])
    image=FileField("Upload a profile picture:", validators=[FileAllowed(["jpg","png"])])
    submit=SubmitField("Apply changes")

    def validate_username(self, username):
        if username.data != current_user.username:
            exists = db.session.query(User).filter_by(username=username.data).first()
            if exists:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            exists = db.session.query(User).filter_by(email=email.data).first()
            if exists:
                raise ValidationError('That email is taken. Please choose a different one.')
            

class AddProductForm(FlaskForm):
    title=StringField("Enter the name of your product", validators=[DataRequired(),Length(min=5,max=199)])
    image=FileField("Attach a picture of your product", validators=[FileAllowed(["jpg","png"]), DataRequired()])
    description=TextAreaField("Write a description of your product", validators=[Length(min=5,max=500)])
    price=FloatField("Add your product's price", validators=[DataRequired(), NumberRange(min=1,max=99999.0)])
    submit=SubmitField("Create product!")


class EditProductForm(FlaskForm):
    title=StringField("Change name of your product", validators=[DataRequired(),Length(min=5,max=199)])
    image=FileField("Attach a different picture of your product", validators=[FileAllowed(["jpg","png"]),DataRequired()])
    description=TextAreaField("Change the description of your product", validators=[Length(min=5,max=500)])
    price=FloatField("Change your product's price", validators=[DataRequired(), NumberRange(min=1,max=99999.0)])
    submit=SubmitField("Apply changes!")


class SearchForm(FlaskForm):
    searched=StringField(validators=[DataRequired(), Length(min=3)])
    submit=SubmitField("Search!")


class CommentForm(FlaskForm):
    content=StringField("Add a comment:",validators=[DataRequired(),Length(min=5, max=200)])
    submit=SubmitField("Post comment!")


class ReviewForm(FlaskForm):
    content=SelectField("Rate the product:",choices=[str(i) for i in range(1,6)])
    submit=SubmitField("Add review!")


class OrderByForm(FlaskForm):
    order_by=SelectField("Order by", validators=[InputRequired()], choices=["Price descending","Price ascending","Oldest to newest","Newest to oldest"])