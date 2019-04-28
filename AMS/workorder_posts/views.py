from flask import render_template,url_for,flash, redirect,request,Blueprint
from flask_login import current_user,login_required
from AMS import db
from AMS.models import workorderPost
from AMS.workorder_posts.forms import workorderPostForm

workorder_posts = Blueprint('workorder_posts',__name__)

@workorder_posts.route('/create',methods=['GET','POST'])
@login_required
def create_post():
    form = workorderPostForm()

    if form.validate_on_submit():

        workorder_post = workorderPost(title=form.title.data,
                             text=form.text.data,
                             user_id=current_user.id
                             )
        db.session.add(workorder_post)
        db.session.commit()
        flash("workorder Post Created")
        return redirect(url_for('core.index'))

    return render_template('create_post.html',form=form)


# int: makes sure that the workorder_post_id gets passed as in integer
# instead of a string so we can look it up later.
@workorder_posts.route('/<int:workorder_post_id>')
def workorder_post(workorder_post_id):
    # grab the requested workorder post by id number or return 404
    workorder_post = workorderPost.query.get_or_404(workorder_post_id)
    return render_template('workorder_post.html',title=workorder_post.title,
                            date=workorder_post.date,post=workorder_post
    )

@workorder_posts.route("/<int:workorder_post_id>/update", methods=['GET', 'POST'])
@login_required
def update(workorder_post_id):
    workorder_post = workorderPost.query.get_or_404(workorder_post_id)
    if workorder_post.author != current_user:
        # Forbidden, No Access
        abort(403)

    form = workorderPostForm()
    if form.validate_on_submit():
        workorder_post.title = form.title.data
        workorder_post.text = form.text.data
        db.session.commit()
        flash('Post Updated')
        return redirect(url_for('workorder_posts.workorder_post', workorder_post_id=workorder_post.id))
    # Pass back the old workorder post information so they can start again with
    # the old text and title.
    elif request.method == 'GET':
        form.title.data = workorder_post.title
        form.text.data = workorder_post.text
    return render_template('create_post.html', title='Update',
                           form=form)


@workorder_posts.route("/<int:workorder_post_id>/delete", methods=['POST'])
@login_required
def delete_post(workorder_post_id):
    workorder_post = workorderPost.query.get_or_404(workorder_post_id)
    if workorder_post.author != current_user:
        abort(403)
    db.session.delete(workorder_post)
    db.session.commit()
    flash('Post has been deleted')
    return redirect(url_for('core.index'))
