#!/usr/bin/python
from flask import Flask
from blueprints.auth import auth_bp
from blueprints.feed import feed_bp
from blueprints.post import post_bp
from blueprints.subreddit import subreddit_bp
from blueprints.vote import vote_bp


app = Flask(__name__)

app.register_blueprint(feed_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(post_bp, url_prefix="/post")
app.register_blueprint(subreddit_bp, url_prefix="/subreddit")
app.register_blueprint(vote_bp, url_prefix="/vote")

if __name__ == "__main__":
    print("API Gateway listening on port 8000...")
    app.run(host="0.0.0.0", port=8000, debug=True)
