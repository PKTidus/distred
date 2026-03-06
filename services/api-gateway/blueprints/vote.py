from flask import Blueprint, g, redirect, request
from clients import vote_client
from middleware import require_auth

vote_bp = Blueprint("vote", __name__)


@vote_bp.post("/<int:post_id>")
@require_auth
def cast(post_id):
    direction = request.form.get("direction")
    next_url = request.form.get("next", "/")

    if direction not in ("up", "down"):
        return {"error": "Invalid vote direction"}, 400

    value = 1 if direction == "up" else -1
    vote_client.cast_vote(post_id=post_id, user_id=g.id, value=value)
    return redirect(next_url)


@vote_bp.post("/<int:post_id>/clear")
@require_auth
def clear(post_id):
    next_url = request.form.get("next", "/")
    vote_client.remove_vote(post_id=post_id, user_id=g.id)
    return redirect(next_url)
