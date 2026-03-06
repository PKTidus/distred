from flask import Blueprint, render_template, request
from clients import feed_client, user_client
from middleware import require_auth, extract_bearer_token

feed_bp = Blueprint("feed", __name__)


@feed_bp.route("/", methods=["GET"])
@require_auth
def home():
    page = int(request.args.get("page", 1))
    sort = request.args.get("sort", "hot")
    per_page = 20

    token: str = extract_bearer_token() or ""
    user = user_client.get_current_user(token)
    posts_result = feed_client.get_home_feed(
        sort=sort, page=page, per_page=per_page, user_id=user.id
    )

    return render_template(
        "feed.html",
        posts=posts_result.items,
        total_pages=posts_result.total,
        page=page,
    )


@feed_bp.route("/r/<slug>", methods=["GET"])
@require_auth
def subreddit(slug):
    page = int(request.args.get("page", 1))
    sort = request.args.get("sort", "hot")
    per_page = 20

    token: str = extract_bearer_token() or ""
    user = user_client.get_current_user(token)
    posts_result = feed_client.get_subreddit_feed(
        subreddit=slug, sort=sort, page=page, per_page=per_page, user_id=user.id
    )

    return render_template(
        "feed.html",
        posts=posts_result.items,
        title=f"r/{slug}",
        total_pages=posts_result.total,
        page=page,
    )
