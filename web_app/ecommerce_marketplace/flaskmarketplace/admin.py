from flask_admin import Admin, AdminIndexView, expose
from flaskmarketplace import app, db
from flask_admin.contrib.sqla import ModelView
from flaskmarketplace.models import User, Product, Comment, Review
from flask_login import current_user, login_required
from flask import redirect, url_for, flash

# in case a user can get to the admin panel
class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role=="admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))
    

# restricts the admin panel only to the users with admin role in the db
class CustomAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.role=="admin":
            return super(CustomAdminIndexView,self).index()
        else:
            flash("You are not the admin!","danger")
            return redirect(url_for("home"))


admin=Admin(index_view=CustomAdminIndexView())
admin.init_app(app)


class UserView(CustomModelView):
    #column_details_exclude_list=["password"]
    column_searchable_list = ["username", "email"]

class ProductView(CustomModelView):
    can_create=False
    can_edit=False
    column_searchable_list=["product_id","title"]

class CommentView(ProductView):
    column_searchable_list=["content","comment_id","user_id","product_id"]

class ReviewView(ProductView):
    column_searchable_list=["rating","review_id","user_id","product_id"]

admin.add_view(UserView(User, db.session))

admin.add_view(ProductView(Product, db.session))

admin.add_view(CommentView(Comment, db.session))

admin.add_view(ReviewView(Review, db.session))