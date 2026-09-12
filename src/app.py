import os

from flask import Flask, render_template
from views import index, course, contact

app = Flask(__name__)

app.add_url_rule('/', endpoint='index', view_func=index)
app.add_url_rule('/course/<course_id>', endpoint='course', view_func=course)
app.add_url_rule('/contact', endpoint='contact', view_func=contact, methods=['GET', 'POST'])

HOST = '127.0.0.1'
PORT = 5000

def startup_banner(host=HOST, port=PORT):
    """Greeting printed once when the development server starts."""
    rule = '=' * 40
    return (
        f"{rule}\n"
        f"  Course Explainer\n"
        f"  Running at http://{host}:{port}\n"
        f"{rule}"
    )

if __name__ == '__main__':
    # The debug reloader re-executes this module in a child process, so greet
    # only from the parent or the banner prints twice.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print(startup_banner())
    app.run(host=HOST, port=PORT, debug=True)