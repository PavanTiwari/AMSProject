import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user as muser
from flask_admin.contrib import sqla
from flask_security import SQLAlchemyUserDatastore, Security, current_user as cuser
from werkzeug.security import generate_password_hash

app = Flask(__name__)

#############################################################################
############ CONFIGURATIONS (CAN BE SEPARATE CONFIG.PY FILE) ###############
###########################################################################

# Remember you need to set your environment variables at the command line
# when you deploy this to a real website.
# export SECRET_KEY=mysecret
# set SECRET_KEY=mysecret
app.config['SECRET_KEY'] = 'mysecret'

#################################
### DATABASE SETUPS ############
###############################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Migrate(app,db)

from flask_admin import Admin
from wtforms.fields import PasswordField


# Customized User model for SQL-Admin
class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        # if not muser.is_authenticated():
        #     return False
        for role in cuser.roles:
            if role == 'admin':
                return True
            else:
                return False


    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = generate_password_hash(model.password2)

# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        for role in cuser.roles:
            if role == 'admin':
                return True
            else:
                return False


admin = Admin(app)

###########################
#### LOGIN CONFIGS #######
#########################

login_manager = LoginManager()

# We can now pass in our app to the login manager
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "users.login"


###########################
#### BLUEPRINT CONFIGS #######
#########################

# Import these at the top if you want
# We've imported them here for easy reference
from AMS.core.views import core
from AMS.users.views import users
from AMS.workorder_posts.views import workorder_posts
from AMS.error_pages.handlers import error_pages


# Register the apps
app.register_blueprint(users)
app.register_blueprint(workorder_posts)
app.register_blueprint(core)
app.register_blueprint(error_pages)



# Executes before the first request is processed.
# Initialize the SQLAlchemy data store and Flask-Security.
from AMS.models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='end-user', description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = generate_password_hash('password')
    if not user_datastore.get_user('someone@example.com'):
        user_datastore.create_user(email='someone@example.com', username='someone', password = encrypted_password)
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', username='admin', password =encrypted_password)

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
   # user_datastore.add_role_to_user('someone@example.com', 'end-user')
    user_datastore.add_role_to_user('test@test.com', 'admin')
    db.session.commit()

