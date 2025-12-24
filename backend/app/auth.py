from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)
@auth.route('/sign-up', methods=['GET', 'POST']) # Add 'GET' here
def sign_up():
    if request.method == 'POST':
        # ... your existing logic to get form data ...
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validation logic
        if password != confirm_password:
            return "Passwords do not match", 400

        # Check Database
        user_exists = db.session.execute(db.select(User).filter_by(username=username)).scalar()
        if user_exists:
            return "Username already taken", 400

        # Create User
        try:
            new_user = User(username=username, email=email, role='student')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login')) # Redirect to your login route
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}", 500

    # This part handles the 'GET' request to show the page
    return render_template("signup.html")