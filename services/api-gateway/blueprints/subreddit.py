from flask import Blueprint, render_template, request, redirect, url_for, flash
from clients import subreddit_client
from middleware import require_auth

subreddit_bp = Blueprint("subreddit", __name__)


# create subreddit
@subreddit_bp.route("/create", methods=["GET"])
@require_auth
def create_subreddit_form():
    return render_template("create_subreddit.html")


@subreddit_bp.route("/create", methods=["POST"])
@require_auth
def create_subreddit():
    name = request.form.get("name")
    description = request.form.get("description", "")

    if not name:
        flash("Subreddit name is required", "error")
        return redirect(url_for("subreddit.create_subreddit_form"))

    response = subreddit_client.create_subreddit(name=name, description=description)
    
    # Use the error field from the gRPC response
    if response.error:
        flash(f"Error creating subreddit: {response.error}", "error")
        return redirect(url_for("subreddit.create_subreddit_form"))

    flash("Subreddit created successfully", "success")
    # Redirect to the subreddit feed
    return redirect(url_for("feed.subreddit", slug=response.name))
