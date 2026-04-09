from flask import Blueprint, redirect, render_template, request, url_for, flash, make_response, g
from clients import user_client
from middleware import require_auth, extract_bearer_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not all([username, password]):
        flash("Username and password are required", "error")
        return redirect(url_for("auth.register_form"))

    result = user_client.register(username=username, password=password)
    if "error" in result:
        flash(result["error"], "error")
        return redirect(url_for("auth.register_form"))

    flash("User registered successfully. Please login.", "success")
    return redirect(url_for("auth.login_form"))


@auth_bp.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password are required", "error")
        return redirect(url_for("auth.login_form"))

    result = user_client.login(username=username, password=password)
    if "error" in result:
        flash(result["error"], "error")
        return redirect(url_for("auth.login_form"))

    # Login successful
    token = result["access_token"]
    next_url = request.args.get("next") or url_for("feed.home")
    response = make_response(redirect(next_url))
    response.set_cookie("access_token", token, httponly=True)
    return response


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Invalidate the current token by adding it to the blacklist."""
    token = extract_bearer_token()
    if token:
        user_client.logout(token=token)

    response = make_response(redirect(url_for("feed.home")))
    response.delete_cookie("access_token")
    flash("Logged out successfully", "success")
    return response


@auth_bp.get("/me")
@require_auth
def get_me():
    """Return the currently authenticated user's profile."""
    token = extract_bearer_token()
    result = user_client.get_current_user(token=token)
    return {"id": result.id, "username": result.username, "error": result.error}
