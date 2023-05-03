from flask import Blueprint, send_from_directory, request, url_for, flash,redirect
import os

editor = Blueprint("editor", __name__, template_folder="templates")



@editor.route('/upload', methods=['GET','POST'])
def upload():
    f = request.files.get('upload')
    # Add more validations here
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg', 'svg']:
        flash("Imagefile not allowed.")
        return redirect(url_for("{{'views.add_post'}}"))
    f.save(os.path.join('goodrobots/static/assets/img/posts/pimgs', f.filename))
    url = f"/static/assets/img/posts/pimgs/{f.filename}"
    flash(f"The path to this file is {url}")
    return redirect(url_for('views.add_post'))
