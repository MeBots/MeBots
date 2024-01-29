from flask import render_template
from app import app, db


@app.errorhandler(401)
def not_found_error(error):
    return render_template('error.html', message='You don\'t have access to this page.'), 401


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', message='Not found.'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', message='An unexpected error has occurred.'), 500
