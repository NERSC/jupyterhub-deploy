import os

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    default_message = "NERSC's Jupyter service is offline. It will return when maintenance is over. Please try again later."
    message = os.environ.get("MESSAGE", default_message).strip()
    if not message:
        message = default_message
    return render_template("index.html", message=message), 503

if __name__ == '__main__':
    app.run(host="0.0.0.0")
