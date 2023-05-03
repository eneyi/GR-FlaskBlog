from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from goodrobots.engine.forms import *
from goodrobots.engine.db import *
from goodrobots.engine.helpers import Paginate
from .auth import is_logged_in
from datetime import datetime as dt
from pymongo import ASCENDING


views = Blueprint("views", __name__, template_folder="../templates/pages")


@views.route('/admin')
def admin():
    if 'logged_in' in session.keys():
        return redirect(url_for('views.view', subject='posts'))
    else:
        flash("Please Enter an Admin User Name and Password")
        return redirect(url_for('views.signin'))

@views.route('/')
def home():
    categories = category_connection.find({"cat_status": "listed"})
    posts = post_connection.find({"post_status": "p"}).sort("post_date", ASCENDING)
    featured = post_connection.find_one({"post_category": 'featured'})
    sform = SubscribeForm()
    return render_template("views/home.html", categories=categories, posts=posts, sform=sform, featured=featured)


@views.route('/donate')
def donate():
    sform = SubscribeForm()
    return render_template("views/donate.html", sform=sform)


@views.route('/about')
def about():
    sform = SubscribeForm()
    return render_template("views/about.html", sform=sform)


@views.route('/terms-of-service')
def tos():
    sform = SubscribeForm()
    return render_template("views/tos.html", sform=sform)


@views.route('/privacy-policy')
def privacy():
    sform = SubscribeForm()
    return render_template("views/privacy.html", sform=sform)


@views.route('/archive')
def archive():
    sform = SubscribeForm()
    posts = post_connection.find({"post_status": "p"})
    pg = Paginate(posts)
    return render_template("views/archives.html", category="archives", posts=pg._pg_posts(), page=pg._page(),
                           per_page=pg._perpage(), pagination=pg._pagination(), sform=sform)


@views.route('/projects')
def projects():
    sform = SubscribeForm()
    projects = project_connection.find({})
    pg = Paginate(projects)
    return render_template("views/projects.html", category="projects", projects=pg._pg_posts(), page=pg._page(),
                           per_page=pg._perpage(), pagination=pg._pagination(), sform=sform)


@views.route('/contact')
def contact():
    form = ContactForm()
    return render_template("views/contact.html", form=form)


@views.route('/blog_post/<post_id>')
def blog_post(post_id):
    sform = SubscribeForm()
    post = post_connection.find_one({"post_id": post_id, "post_status": 'p'})
    print(post['post_title'])
    return render_template("views/blog-post.html", post=post, sform=sform)


@views.route('/categories')
def categories():
    sform = SubscribeForm()
    categories = category_connection.find({"cat_status": "listed"})
    return render_template("views/categories.html", sform=sform, categories=categories)


@views.route('/category/<category>')
def category(category):
    cat = category_connection.find({"cat_slug": category})
    category_posts = post_connection.find({"post_status": 'p'})
    category_posts = [i for i in category_posts if category in [k.lower() for k in i['post_category']]]
    sform = SubscribeForm()
    pg = Paginate(category_posts)
    return render_template("views/category_posts.html", sform=sform, posts=pg._pg_posts(), page=pg._page(),
                           per_page=pg._perpage(), pagination=pg._pagination(), cat=cat)


@views.route('/project/<project>')
def project(project):
    proj = project_connection.find_one({"project_slug": project})
    project_posts = post_connection.find({"post_status": 'p', "project_slug": project})
    project_posts = [i for i in project_posts if project in [k.lower() for k in i['post_project']]]
    sform = SubscribeForm()
    pg = Paginate(project_posts)
    return render_template("views/project_posts.html", sform=sform, posts=pg._pg_posts(), page=pg._page(),
                           per_page=pg._perpage(), pagination=pg._pagination(), project=proj)


###############################BACKEND##################################
@views.route("/signup")
def signup():
    form = SignupForm()
    return render_template("admin/home.html", form=form, action='signup')


@views.route("/signin")
def signin():
    form = SigninForm()
    return render_template("admin/home.html", form=form, action='signin')


@views.route("/view_<subject>")
@is_logged_in
def view(subject):
    dform = DeleteForm()
    if subject == "posts":
        objs = post_connection.find({"post_author": session['fullname']})
    if subject == "categories":
        objs = category_connection.find({"cat_author": session['fullname']})
    if subject == "projects":
        objs = project_connection.find({"project_author": session['fullname']})
    if subject == "images":
        objs = image_connection.find({"image_author": session['fullname']})
    if subject == "datasets":
        objs = dataset_connection.find({"dataset_author": session['fullname']})

    pg = Paginate(objs, perpage = 25)
    return render_template("admin/view.html", subject=subject.capitalize(), objs=pg._pg_posts(), page=pg._page(),
                           per_page=pg._perpage(), pagination=pg._pagination(), form=dform)


###################################################################################################################################################
@views.route("/add_post")
@views.route("/edit_post/<post_id>")
@is_logged_in
def add_post(post_id=None,  methods=['GET']):
    form = PostForm()
    post = post_connection.find_one({"post_id": post_id})

    if "edit_post" in request.url:
        # Populate article form fields
        form.post_id = post['post_id']
        form.post_title.data = post['post_title']
        form.post_project.data = post['post_project']
        form.post_category.data = post['post_category']
        form.post_date.data = dt.strptime(post['post_date'], "%Y-%m-%d")
        form.post_status.data = post['post_status']
        form.post_image.data = f"goodrobots{post['post_image']}"
        form.post_content.datasets = "hello"
        form.post_content.data = post['post_content']
        return render_template("admin/edit.html", form=form, act="Edit", subject="Post", post=post)
    else:
        return render_template("admin/add.html", form=form, act="Add", subject="Post", post=post)


@views.route("/add_category")
@views.route("/edit_category/<category_id>")
@is_logged_in
def add_category(category_id=None, methods=['GET']):
    form = CategoryForm()
    category = category_connection.find_one({"cat_slug": category_id})

    if "edit_category" in request.url:
        # Populate category form fields
        form.cat_id.data = category['cat_id']
        form.cat_name.data = category['cat_name']
        form.cat_desc.data = category['cat_desc']
        form.cat_color.data = category['cat_color']
        form.cat_status.data = category['cat_status']
        form.cat_date.data = dt.strptime(category['cat_date'], "%Y-%m-%d")
        form.cat_image.data = category['cat_image']
        return render_template("admin/edit.html", form=form, act="Edit", subject="Category")
    else:
        return render_template("admin/add.html", form=form, act="Add", subject="Category")


@views.route("/add_project")
@views.route("/edit_project/<project_id>")
@is_logged_in
def add_project(project_id=None, methods=['GET']):
    form = ProjectForm()

    if "edit_project" in request.url:
        project = project_connection.find_one({"project_id": project_id})

        # Populate article form fields
        form.project_id = project['project_id']
        form.project_title.data = project['project_title']
        form.project_date.data = dt.strptime(project['project_date'], "%Y-%m-%d")
        form.project_desc.data = project['project_desc']
        form.project_author.data = project['project_author']
        return render_template("admin/edit.html", form=form, act="Edit", subject="Project")
    else:
        return render_template("admin/add.html", form=form, act="Edit", subject="Project")


@views.route("/add_image")
@views.route("/edit_image/<image_id>")
@is_logged_in
def add_image(image_id=None, methods=['GET']):
    form = ImageForm()

    if "edit_image" in request.url:
        image = image_connection.find_one({"image_id": image_id})

        # Populate article form fields
        form.image_title.data = image['image_title']
        form.image_date.data = dt.strptime(image['image_date'], "%Y-%m-%d")
        form.image_alt.data = image['image_alt']
        return render_template("admin/edit.html", form=form, act ="Edit", subject="Image")
    else:
        return render_template("admin/add.html", form=form, act ="Edit", subject="Image")
