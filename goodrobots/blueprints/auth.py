from flask import Blueprint, request, redirect, url_for, flash, session
from goodrobots.engine.forms import *
from goodrobots.engine.db import *
from goodrobots.engine.helpers import *
from flask_mail import Message
from goodrobots import mail
from passlib.hash import sha256_crypt
import os


auth = Blueprint("auth", __name__, template_folder="templates")


#################Simple Authentication##########################
@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    admin_email_exist = admin_connection.find_one({"admin_email": form.email.data})
    admin_username_exist = admin_connection.find_one({"admin_username": form.username.data})

    if not admin_email_exist and not admin_username_exist:
        pass1, pass2 = form.password.data, form.confirm_password.data
        if pass1 == pass2:
            username = form.username.data

            # create user directory
            if not os.path.exists(f"goodrobots/static/assets/users/{username}"):
                os.mkdir(f"goodrobots/static/assets/users/{username}")

            # save avatar
            file = request.files['user-image']
            filename = save_image(file, base=f"goodrobots/static/assets/users/{username}", slug="avatar")

            # add user to database
            newadmin = {"admin_title": form.fullname.data,
                        "admin_email": form.email.data,
                        "admin_pass": sha256_crypt.encrypt(form.password.data),
                        "admin_username": username,
                        "admin_image": filename.replace("goodrobots", ""),
                        "admin_status": "inactive"}

            admin_connection.insert_one(newadmin)
            flash("We will Contact You in for further details")
            return redirect(url_for("views.home"))
        else:
            flash("Passwords Must Match")
            return redirect(url_for("views.signup"))
    else:
        flash("Username or Email is taken, please choose a different Username or Email")
        return redirect(url_for("views.signup"))


@auth.route("/signin", methods=['GET', 'POST'])
def signin():
    form = SigninForm(request.form)

    email = form.email.data
    p1 = form.password.data

    check1 = admin_connection.find_one({"admin_email": email})
    check2 = admin_connection.find_one({"admin_username": email})
    user = check1 if check1 else check2

    if user:
        active_user = user['admin_status'] == "active"
        pass_check = sha256_crypt.verify(p1, user['admin_pass'])
        if 'logged_in' in session.keys():
            flash("Already Logged In")
            return redirect(url_for('views.view', subject="posts", session=session))
        else:
            if active_user and pass_check:
                session['logged_in'] = True
                session['fullname'] = user['admin_title']
                session['username'] = user['admin_username']
                session['email'] = user['admin_email']
                session['dir'] = f"/static/users/{user['admin_username']}"
                flash("Successfully Logged In")
                return redirect(url_for('views.view', subject="posts", session=session))
            else:
                flash("Wrong User Name or Password")
                return redirect(url_for('views.signin'))
    else:
        flash("No such admin exist, please sign up")
        return redirect(url_for('views.signup'))


@auth.route('/signout')
@is_logged_in
def signout():
    session['logged_in'] = False
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('views.signin'))

#################ADD ENDPOINTS###########################


@auth.route("/add_post", methods=['GET', 'POST'])
@is_logged_in
def add_post():
    form = PostForm(request.form)
    slug = form.post_title.data.lower().replace(" ", "-")
    post_exist = post_connection.find_one({"post_slug": slug, "post_author": session['fullname']})


    if not post_exist and request.method == 'POST':
        gr_posts_count = post_connection.count_documents({})
        post_id = f"gr_post{gr_posts_count}"
        gpt4 = NLTKGPT(form.post_content.data).run()

        # edit file attachments
        file = request.files['post-image']
        filename = save_image(file)

        post_buzz = gpt4.get("bullets").split("•")[1::]
        post_buzz = [i[1::].strip() for i in post_buzz if i != ""]

        # create post
        post = {"post_id": post_id,
                "post_title": form.post_title.data,
                "post_project": form.post_project.data,
                "post_summary": gpt4.get("summary"),
                "post_slug": slug,
                "post_author": session['fullname'],
                "post_date": str(form.post_date.data),
                "post_category": form.post_category.data,
                "post_tags": gpt4.get("tags"),
                "post_keywords": gpt4.get("keywords"),
                "post_status": form.post_status.data,
                "post_image": filename.replace("goodrobots", ""),
                "post_content": form.post_content.data,
                "post_buzz": post_buzz,
                "post_read_time": f"{round(len(form.post_content.data)/1000)} Mins"
                }

        post_connection.insert_one(post)
        flash(message="Post Successfully Inserted")

    else:
        flash(message="Post Exist")
        return redirect(url_for('views.add_post'))
    return redirect(url_for('views.view', subject="posts"))


@is_logged_in
@auth.route("/add_category", methods=['GET', 'POST'])
def add_category():
    form = CategoryForm(request.form)

    slug = form.cat_title.data.lower().replace(" ", "-")
    category_exist = category_connection.find_one({"cat_slug": slug, "cat_author": session['fullname']})
    gr_category_count = category_connection.count_documents({})
    category_id = f"gr_category{gr_category_count}"

    if not category_exist:
        category = {
                    "cat_id": category_id,
                    "cat_title": form.cat_title.data.lower(),
                    "cat_slug": slug,
                    "cat_author": session['fullname'],
                    "cat_desc": form.cat_desc.data,
                    "cat_color": request.form.get("cat_color"),
                    "cat_date": str(form.cat_date.data),
                    "cat_status": form.cat_status.data,
                    "cat_image": form.cat_image.data}

        category_connection.insert_one(category)
        flash(message="Category Successfully Inserted")

        return redirect(url_for('views.view', subject="categories"))
    return redirect(url_for('views.view', subject="categories"))


@auth.route("/add_project", methods=['GET', 'POST'])
@is_logged_in
def add_project():
    form = ProjectForm(request.form)

    slug = form.project_title.data.lower().replace(" ", "-")
    project_exist = project_connection.find_one({"project_slug": slug, "project_author": session['fullname']})
    gr_project_count = project_connection.count_documents({})
    project_id = f"gr_project{gr_project_count}"

    if not project_exist:
        project = {
                    "project_id": project_id,
                    "project_title": form.project_title.data,
                    "project_slug": slug,
                    "project_desc": form.project_desc.data,
                    "project_author": session['fullname'],
                    "project_date": str(form.project_date.data)}

        project_connection.insert_one(project)
        flash(message="Project Successfully Inserted")

        return redirect(url_for('views.view', subject="projects"))
    return redirect(url_for('views.view', subject="projects"))


@auth.route("/add_image", methods=['GET', 'POST'])
@is_logged_in
def add_image():
    form = ImageForm(request.form)
    slug = form.image_title.data.lower().replace(" ", "-")
    image_exist = image_connection.find_one({"image_slug": slug, "image_author": session['fullname']})

    if not image_exist and request.method == 'POST':
        gr_image_count = image_connection.count_documents({})
        image_id = f"gr_image{gr_image_count}"

        # edit file attachments
        file = request.files['image-file']
        filename = save_image(file)

        image = {
            "image_id": image_id,
            "image_title": form.image_title.data,
            "image_uahtor": session['fullname'],
            "image_slug": slug,
            "image_alt": form.image_alt.data,
            "image_path": filename,
            "image_date": str(form.image_date.data)}

        image_connection.insert_one(image)
        flash(message="IMage Successfully Inserted")

        return redirect(url_for('views.view', subject="images"))
    return redirect(url_for('views.view', subject="images"))


###########################EDIT ENDPOINTS#####################################


@auth.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_post(post_id):
    form = PostForm(request.form)


    slug = form.post_title.data.lower().replace(" ", "-")
    post_exist = post_connection.find_one({"post_id": post_id})

    if post_exist and request.method == 'POST':
        post_id = post_id
        gpt4 = NLTKGPT(form.post_content.data).run()

        # edit file attachments
        file = request.files['post-image']
        if file:
            filename = save_image(file)
        else:
            filename = post_exist['post_image']

        post_buzz = gpt4.get("bullets").split("•")[1::]
        post_buzz
        post_buzz = [i[1::].strip() for i in post_buzz if i != ""]

        # create post
        post = {"post_id": post_id,
                "post_title": form.post_title.data,
                "post_project": form.post_project.data,
                "post_summary": gpt4.get("summary"),
                "post_slug": slug,
                "post_author": session['fullname'],
                "post_date": str(form.post_date.data),
                "post_category": form.post_category.data,
                "post_tags": gpt4.get("tags"),
                "post_keywords": gpt4.get("keywords"),
                "post_status": form.post_status.data,
                "post_buzz": post_buzz,
                "post_image": filename.replace("goodrobots", ""),
                "post_content": form.post_content.data,

                "post_read_time": f"{round(len(form.post_content.data) / 1000)} Mins"
                }

        post_connection.update_one(
            {'post_id': post_id}, {"$set": post}, upsert=True)
        flash('Post Updated', 'success')

    else:
        flash(message="No Such Post Exist")
        return redirect(url_for('views.view', subject="posts"))

    return redirect(url_for('views.view', subject="posts"))


@auth.route('/edit_category/<category_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_category(category_id):
    form = CategoryForm(request.form)
    category_exist = category_connection.find_one({"cat_slug": category_id, "cat_author": session['fullname']})


    if category_exist and request.method == 'POST':
        category = {
                    "cat_id": category_id,
                    "cat_title": form.cat_title.data.lower(),
                    "cat_author": session['fullname'],
                    "cat_slug": form.cat_title.data.lower().replace(" ", "-"),
                    "cat_desc": form.cat_desc.data,
                    "cat_color": request.form.get("cat_color"),
                    "cat_date": str(form.cat_date.data),
                    "cat_status": form.cat_status.data,
                    "cat_image": form.cat_image.data}
        category_connection.update_one(
            {'cat_slug': category_id}, {"$set": category}, upsert=True)
        flash('Category Updated', 'success')
    else:
        flash(message="No Such Category Exist")
        return redirect(url_for('views.view', subject="categories"))
    return redirect(url_for('views.view', subject="categories"))


@auth.route("/edit_project/<project_id>", methods=['GET', 'POST'])
@is_logged_in
def edit_project(project_id):
    form = ProjectForm(request.form)
    slug = form.project_title.data.lower().replace(" ", "-")
    project_exist = project_connection.find_one({"project_id": project_id, "project_author": session['fullname']})

    if project_exist and request.method == "POST":
        project = {
                    "project_id": project_id,
                    "project_title": form.project_title.data,
                    "project_slug": slug,
                    "project_desc": form.project_desc.data,
                    "project_author": session['fullname'],
                    "project_date": str(form.project_date.data)}

        project_connection.update_one(
            {'project_id': project_id}, {"$set": project}, upsert=True)
        flash('Project Updated', 'success')
    else:
        flash(message="No Such Project Exist")
        return redirect(url_for('views.view', subject="projects"))
    return redirect(url_for('views.view', subject="projects"))


@auth.route("/edit_image/<image_id>", methods=['GET', 'POST'])
@is_logged_in
def edit_image(image_id):
    form = ImageForm(request.form)
    slug = form.image_title.data.lower().replace(" ", "-")
    image_exist = image_connection.find_one({"image_slug": slug, "image_author": session['fullname']})

    if image_exist and request.method == 'POST':
        # edit file attachments
        file = request.files['image-file']
        filename = save_image(file)

        image = {
            "image_id": image_id,
            "image_title": form.image_title.data,
            "image_slug": slug,
            "image_alt": form.image_alt.data,
            "image_path": filename,
            "image_author": session['fullname'],
            "image_date": str(form.image_date.data)}

        image_connection.update_one(
            {'image_id': image_id}, {"$set": image}, upsert=True)
        flash('IMage Updated', 'success')
    else:
        flash(message="No Such Image Exist")
        return redirect(url_for('views.view', subject="images"))
    return redirect(url_for('views.view', subject="images"))


######################DELETE ENDPOINTS#######################

@auth.route('/delete_post/<post_id>', methods=['GET', 'POST'])
@is_logged_in
def delete_post(post_id):
    post_connection.delete_one({"post_id": post_id})
    flash("Post Successfully Deleted")
    return redirect(url_for("views.view", subject="posts"))


@auth.route("/delete_project/<project_id>",  methods=['GET', 'POST'])
@is_logged_in
def delete_project(project_id):
    project_connection.delete_one({"project_id":project_id})
    flash("Project Successfully Deleted")
    return redirect(url_for("views.view", subject="projects"))


@auth.route("/delete_category/<category_id>",  methods=['GET', 'POST'])
@is_logged_in
def delete_category(category_id):
    category_connection.delete_one({"cat_slug": category_id})
    flash("Category Successfully Deleted")
    return redirect(url_for("views.view", subject="categories"))


@auth.route("/delete_image/<image_id>",  methods=['GET', 'POST'])
@is_logged_in
def delete_image(image_id):
    image_connection.delete_one({"image_id": image_id})
    flash("Image Successfully Deleted")
    return redirect(url_for("views.view", subject="images"))

#############################CONTACT & SUBSCRIBE#########################

@auth.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if form.validate_on_submit():
        fn = form.firstname.data
        ln = form.lastname.data
        email = form.email.data
        sub = form.subject.data
        msg = form.message.data

        msg = f"From: {fn} {ln}<br>{email}<br>{sub}<br>{msg}"
        msg = Message(sub, sender="fair@goodrobots.ai",
                      recipients=['fair@goodrobots.ai'],
                      body=msg)
        mail.send(msg)
        flash("We have recieved your message!!!")
        return redirect(url_for('views.contact'))


@auth.route("/subscribe", methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm(request.form)
    email = form.email.data
    fullname = form.fullname.data

    user_exist = subcribers_connection.find_one({"email": email})

    if not user_exist:
        new_user = {"user": str(fullname), "email":str(email)}
        subcribers_connection.insert_one(new_user)
        message = f"Hello {fullname.capitalize()}: <br> <h2 style='color:#034447;font-weight:bolder;'>Thank you for joining Good Robots</h2>" \
                  f"<br>We investigate the use of " \
                  f"AI algorithms in politics, society and culture. Our goal is to ensure that Tech companies deploying AI" \
                  f"powered products are fair and ethical. We evaluate AI products, investigate the use of AI in Big Tech products" \
                  f"and draw public awareness to the basics of ethical Algorithms. " \
                  f"<br><br> On this platorm, you will find thought - provoking articles, investigations, datasets, interviews " \
                  f"with industry leaders and academics, and analysis of the latest trends and developments.We'll explore topics such as:" \
                  f" The implications of AI in decision making in society, the role of Big Tech in normalising ethical AI standards," \
                  f"The impact of AI on marginalised and vulnerable groups and the need for AI standards and regulations. " \
                  f"Thank you for subscribing to Good Robots. We're excited to have you on board and look forward to sharing our insights with you!\n\n" \
                  f"<br>Best Regards, <br> Ruth"

        msg = Message('Welcome to Good Robots', sender='fair@goodrobots.ai', recipients=[email])
        msg.html = message
        mail.send(message=msg)
        flash("Thank you for subscribing to Good Robots. Happy to have in the good fight")
    else:
        flash("User Exists")
        return redirect(url_for('views.home'))

    return redirect(url_for('views.home'))
