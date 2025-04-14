from flask import Flask, request
from markupsafe import escape  # Import the escape function

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    # Sanitize user input with HTML escaping before including in the response
    safe_input = escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)