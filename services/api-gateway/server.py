#!/usr/bin/python
import os
from flask import Flask
from blueprints.auth import auth_bp
from blueprints.feed import feed_bp
from blueprints.post import post_bp
from blueprints.subreddit import subreddit_bp
from blueprints.vote import vote_bp


from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


@app.template_filter("humanize")
def humanize_time(timestamp):
    """Convert a timestamp to a human-readable string like '2 hours ago'."""
    if not timestamp:
        return ""

    now = int(time.time())
    diff = now - timestamp

    if diff < 60:
        return "just now"
    elif diff < 3600:
        return f"{diff // 60}m ago"
    elif diff < 86400:
        return f"{diff // 3600}h ago"
    elif diff < 604800:
        return f"{diff // 86400}d ago"
    else:
        return datetime.fromtimestamp(timestamp).strftime("%b %d, %Y")


app.register_blueprint(feed_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(post_bp, url_prefix="/post")
app.register_blueprint(subreddit_bp, url_prefix="/subreddit")
app.register_blueprint(vote_bp, url_prefix="/vote")

if __name__ == "__main__":
    print("API Gateway listening on port 8000...")
    app.run(host="0.0.0.0", port=8000, debug=True)
