from flask import Blueprint, redirect, render_template, request, url_for, flash
from clients import post_client, subreddit_client
from middleware import require_auth

post_bp = Blueprint("post", __name__)


@post_bp.route("/", methods=["GET"])
@require_auth
def create_post_form():
    return render_template(
        "create_post.html",
        subreddits=subreddit_client.get_subreddits().subreddits,
    )


@post_bp.route("/", methods=["POST"])
@require_auth
def create_post():
    title = request.form.get("title")
    subreddit = request.form.get("subreddit")

    if not title or not subreddit:
        flash("Title and subreddit are required", "error")
        return redirect(url_for("post.create_post_form"))

    response = post_client.create_post(title=title, subreddit=subreddit)
    
    if response.error:
        flash(f"Error creating post: {response.error}", "error")
        return redirect(url_for("post.create_post_form"))

    return redirect(url_for("post.view_post", post_id=response.post_id))


@post_bp.route("/<post_id>", methods=["POST"])
@require_auth
def delete_post(post_id):
    response = post_client.delete_post(post_id=post_id)
    if response.error:
        flash(f"Error deleting post: {response.error}", "error")
    else:
        flash("Post deleted successfully", "success")
    return redirect(url_for("feed.home"))


@post_bp.route("/<post_id>", methods=["GET"])
def view_post(post_id):
    response = post_client.get_post(post_id=post_id)
    if not response or response.error:
        return f"Post not found: {response.error if response else ''}", 404
    return render_template(
        "post.html",
        post=response,
    )
