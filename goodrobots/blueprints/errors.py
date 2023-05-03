from flask import Blueprint, render_template

errors = Blueprint("errors", __name__, template_folder="templates/pages")


@errors.errorhandler(400)
def error_400(e):
    return render_template("views/error.html", error=400), 400


@errors.errorhandler(404)
def error_404(e):
    return render_template("views/error.html", error=404), 404


@errors.errorhandler(500)
def error_500(e):
    return render_template("views/error.html", error=500), 500
