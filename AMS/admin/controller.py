from flask_admin.contrib.sqla import ModelView
from .admin_blueprint import AdminBlueprint
from AMS.models import User
from AMS import db
from flask_admin import Admin
# Flask and Flask-SQLAlchemy initialization here
print("Admin was called")
adc = AdminBlueprint(__name__, name='Test', template_mode='bootstrap3')
adc.add_view(ModelView(User, db.session))

