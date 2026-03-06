from flask import Blueprint, render_template, request
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
    data = request.get_json()
    name = data.get("name")
    description = data.get("description", "")

    response = subreddit_client.create_subreddit(name=name, description=description)
    return render_template(
        "subreddit.html",
        subreddit=response,
    )
