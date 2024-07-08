from flaskmarketplace import db
from flask_login import UserMixin
from flaskmarketplace import login_manager
from flask_login import current_user

@login_manager.user_loader 
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['user']

    def get_id(self):
        return (self.user_id)

    def __repr__(self):
        return f"username: {self.username}\nmail: {self.email}, pw: {self.password}, balance: {self.balance}"
    
    
class Product(db.Model):
    __table__= db.Model.metadata.tables["product"]

    
class Comment(db.Model):
    __table__= db.Model.metadata.tables["comment"]

class Review(db.Model):
    __table__= db.Model.metadata.tables["review"]

class Cart(db.Model):
    __table__= db.Model.metadata.tables["cart"]
