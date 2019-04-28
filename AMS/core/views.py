from flask import render_template,request,Blueprint
from AMS.models import workorderPost
from flask_login import current_user,login_required
core = Blueprint('core',__name__)

@core.route('/')
def index():
    '''
    This is the home page view. Notice how it uses pagination to show a limited
    number of posts by limiting its query size and then calling paginate.
    '''
    workorder_posts = []
    if current_user.is_authenticated :
        page = request.args.get('page', 1, type=int)
        page = request.args.get('page', 1, type=int)
        workorder_posts = workorderPost.query.filter_by(author=current_user).order_by(workorderPost.date.desc()).paginate(page=page, per_page=5)


    return render_template('index.html',workorder_posts=workorder_posts)

@core.route('/info')
def info():
    '''
    Example view of any other "core" page. Such as a info page, about page,
    contact page. Any page that doesn't really sync with one of the models.
    '''
    return render_template('info.html')
