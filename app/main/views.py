"""Routers and views for blueprint 'main'
"""
from tests.log import logger, set_log
from flask_login import login_required, current_user
from app.alchemy_model import Post
from app.form import PostForm
from flask import (request, render_template, session, url_for, redirect, flash)
from .import main

@main.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    """depends on method
    GET  direct to where writing new post
    POST process new post submit
    """
    post_form = PostForm()
    if post_form.validate_on_submit():
        post = Post.insert(title=post_form.title.data,
                           content=post_form.content.data,
                           published=post_form.published.data,
                           author=current_user._get_current_object()
                          )
        flash('Post created successfully.', 'success')
        if post.published:
            return redirect(url_for('main.detail', id=post.id))
        else:
            return redirect(url_for('main.edit', id=post.id))
    return render_template('create.html', post_form=PostForm())

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    ''' Edit dedicated post '''
    post = Post.query.filter_by(id=id).first_or_404()
    post_form = PostForm()
    #check if method is 'POST' & data is validate
    if post_form.validate_on_submit():
        post.modify(post_form.title.data,
                    post_form.content.data,
                    post_form.published.data
                   )
        flash('Post saved successfully.', 'success')
        if post.published:
            return redirect(url_for('.detail', id=post.id))
        else:
            return redirect(url_for('.edit', id=post.id))
    #flash('Title and Content are required.', 'danger')

    #get data from DB to form
    post_form.title.data = post.title
    post_form.content.data = post.content
    post_form.published.data = post.published
    return render_template('edit.html', post_form=post_form)

@main.route("/posts/<int:id>/")
def detail(id):
    ''' Get dedicated post '''
    if current_user.is_authenticated:
        post = Post.query.filter_by(id=id).first_or_404()
    # If not logged yet, only published post allowed
    else:
        post = Post.query.filter_by(id=id, published=True).first_or_404()
    return render_template('detail.html', post=post, page_id=id)

@main.route('/')
def index(page=1):
    """Direct to homepage.
    check whether the browser has logged in
    If loggin in: editing posts is allowed
    If not: it can only read posts

    Support search in future
    """

    #posts is a class Pagination object
    page = request.args.get('page', 1, type=int)
    pagination = Post.query_posts(page)
    posts = pagination.items
    return render_template("index.html",
                           posts=posts,
                           pagination=pagination
                          )
