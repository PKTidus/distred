from flask import Blueprint, redirect, render_template, request, url_for
from clients import post_client, subreddit_client
from middleware import require_auth

post_bp = Blueprint("post", __name__)


@post_bp.route("/", methods=["GET"])
@require_auth
def create_post_form():
    return render_template(
        "create_post.html",
        subreddits=subreddit_client.get_subreddits(),
    )


@post_bp.route("/", methods=["POST"])
@require_auth
def create_post():
    data = request.get_json()
    title = data.get("title")
    subreddit = data.get("subreddit")
    response = post_client.create_post(title=title, subreddit=subreddit)
    return render_template(
        "post.html",
        post=response,
    )


@post_bp.route("/<post_id>", methods=["DELETE"])
@require_auth
def delete_post(post_id):
    post_client.delete_post(post_id=post_id)
    # redirect to home feed after deletion
    return redirect(url_for("feed.home"))


@post_bp.route("/<post_id>", methods=["GET"])
def view_post(post_id):
    response = post_client.get_post(post_id=post_id)
    if not response:
        return "Post not found", 404
    return render_template(
        "post.html",
        post=response,
    )
