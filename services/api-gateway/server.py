#!/usr/bin/python
from flask import Flask, request

app = Flask(__name__)


if __name__ == "__main__":
    print("API Gateway listening on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
