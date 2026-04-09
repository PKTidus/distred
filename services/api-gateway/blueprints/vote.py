from flask import Blueprint, g, redirect, request, url_for, flash
from clients import vote_client
from middleware import require_auth

vote_bp = Blueprint("vote", __name__)


@vote_bp.route("/<post_id>", methods=["POST"])
@require_auth
def cast(post_id):
    direction = request.form.get("direction")
    next_url = request.form.get("next") or url_for("feed.home")

    if direction not in ("up", "down"):
        flash("Invalid vote direction")
        return redirect(next_url)

    value = 1 if direction == "up" else -1
    vote_client.cast_vote(post_id=post_id, user_id=str(g.user_id), value=value)
    return redirect(next_url)


@vote_bp.route("/<post_id>/clear", methods=["POST"])
@require_auth
def clear(post_id):
    next_url = request.form.get("next") or url_for("feed.home")
    vote_client.remove_vote(post_id=post_id, user_id=str(g.user_id))
    return redirect(next_url)
