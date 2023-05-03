from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectMultipleField, SelectField, EmailField, PasswordField, IntegerField
from wtforms.validators import DataRequired
from wtforms import validators, widgets
from goodrobots.engine.db import *
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_mdeditor import MDEditorField

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PostForm(FlaskForm):
    post_id = ""
    post_title = StringField("Post Title", validators=[validators.Length(min=6, max=200)])
    post_date = DateField("Post Date", validators=[DataRequired()])

    choices = category_connection.find({}, {"cat_title":1, "_id":0})
    choices = [(c['cat_title'].replace(" ", "-"), c['cat_title']) for c in choices]
    post_category = SelectMultipleField("Post Category", validators=[DataRequired()], choices=choices)

    projects = project_connection.find({}, {"project_title": 1, "_id": 0})
    projects = [(c['project_title'].replace(" ", "-"), c['project_title']) for c in projects]
    post_project = SelectMultipleField("Post Project", choices=projects)

    post_status = SelectField("Post Status", validators=[DataRequired()], choices=[("p", "Published"), ("d", "Draft")])
    post_image = FileField("Post Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'svg'])])
    post_type = MultiCheckboxField("Post Type", choices=[("audio", "Audio"), ("text", "Text")])

    datasets = dataset_connection.find({})
    post_datasets = SelectMultipleField("Post Datasets", choices=datasets)
    post_content = MDEditorField("Post Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CategoryForm(FlaskForm):
    cat_id = StringField("Category Id", validators=[validators.Length(min=6, max=50)])
    cat_title = StringField("Category Title", validators=[validators.Length(min=6, max=50)])
    cat_desc = TextAreaField("Category Description", validators=[validators.Length(min=6, max=2000)])
    cat_color = StringField("Category Color", validators=[DataRequired()])
    cat_date = DateField("Categoory Date", validators=[DataRequired()])
    cat_image = StringField("Category Image Path", validators=[DataRequired()])
    cat_status = MultiCheckboxField("List Publically", choices=[("listed", "Listed"), ("unlisted", "Unlisted")])
    submit = SubmitField("Submit")


class ProjectForm(FlaskForm):
    project_id = ""
    project_title = StringField("Project Title", validators=[validators.Length(min=6, max=200)])
    project_desc = TextAreaField("Project Description", validators=[validators.Length(min=6, max=2000)])
    project_date = DateField("Project Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ImageForm(FlaskForm):
    upload = FileField("Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'svg'])])
    image_title = StringField("Image Name", validators=[validators.Length(min=6, max=50)])
    image_alt = StringField("Image Alt Text", validators=[validators.Length(min=6, max=60)])
    image_date = DateField("Image Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    firstname = StringField("First Name", validators=[validators.Length(min=6, max=50)])
    lastname = StringField("Last Name", validators=[validators.Length(min=6, max=60)])
    email = EmailField("Email Address", validators=[validators.Length(min=6, max=50)],
                       render_kw={"placeholder": "Email"})
    subject = StringField("Subject", validators=[validators.Length(min=6, max=60)])
    message = TextAreaField("Message", validators=[validators.Length(min=6, max=200)])
    submit = SubmitField("Submit")


class SubscribeForm(FlaskForm):
    fullname = StringField("First Name", validators=[validators.Length(min=4, max=100)], render_kw={"placeholder": "Full Name"})
    email = EmailField("Email Address", validators=[validators.Length(min=6, max=200)],
                       render_kw={"placeholder": "Email"})
    submit = SubmitField("Submit")


class SigninForm(FlaskForm):
    email = StringField("Email Address", validators=[validators.Length(min=6, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Submit")


class SignupForm(FlaskForm):
    fullname = StringField("First Name", validators=[validators.Length(min=4, max=100)],
                           render_kw={"placeholder": "Full Name"})
    username = StringField("Username", validators=[validators.Length(min=4, max=100)],
                           render_kw={"placeholder": "User Name"})
    email = EmailField("Email Address", validators=[validators.Length(min=6, max=50)],
                       render_kw={"placeholder": "Email"})
    bio = TextAreaField("Category DescriptionAdmin Biography", validators=[validators.Length(min=6, max=50)], render_kw={"placeholder": "Bio"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})
    avatar = FileField("Admin Avatar", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'svg'])])
    submit = SubmitField("Submit")


class DeleteForm(FlaskForm):
    submit = SubmitField("Submit")