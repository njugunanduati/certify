from flask import render_template, Blueprint
from app import app, db


blueprint = Blueprint('errors', __name__)

@blueprint.app_errorhandler(404)
def handle_404(err):
    return render_template('404.html'), 404


@blueprint.app_errorhandler(500)
def handle_500(err):
    return render_template('500.html'), 500