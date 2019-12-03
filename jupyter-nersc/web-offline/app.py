import os

from sanic import Sanic
from sanic.response import html

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('app', 'templates'))

app = Sanic(__name__)
app.static("/static", "./static")

@app.route('/', methods=["GET", "PUT", "POST", "PATCH", "DELETE", "OPTION"])
@app.route('/<path:path>', methods=["GET", "PUT", "POST", "PATCH", "DELETE", "OPTION"])
async def catch_all(request, path=""):
    default_message = "NERSC's Jupyter service is offline. It will return when maintenance is over. Please try again later."
    message = os.environ.get("MESSAGE", default_message).strip()
    if not message:
        message = default_message
    template = env.get_template("index.html")
    content = template.render(message=message, app=app)
    return html(content, status=503)

if __name__ == '__main__':
    app.run()
