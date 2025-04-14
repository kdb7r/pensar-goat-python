import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
from urllib.parse import urlparse
import re
from markupsafe import escape  # Import for XSS protection

app = flask.Flask(__name__)

# ======== 1. SQL Injection Vulnerability ========
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
conn.commit()


@app.route("/login")
def login():
    """Vulnerable to SQL Injection"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    # Using parameterized query instead of string interpolation
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS - fixed"""
    user_input = flask.request.args.get("name", "")
    return f"<h1>Welcome, {escape(user_input)}!</h1>"  # Sanitized to prevent script injection


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF attacks"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF
    if not url or not isinstance(url, str):
        return "Invalid URL", 400
    
    # Parse the URL to validate components
    try:
        parsed_url = urlparse(url)
        
        # Check for valid scheme
        if parsed_url.scheme not in ["http", "https"]:
            return "Only HTTP and HTTPS protocols are allowed", 400
        
        hostname = parsed_url.netloc.lower()
        if ":" in hostname:
            hostname = hostname.split(":")[0]
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private IP ranges
            if ip.is_private or ip.is_loopback or ip.is_multicast or ip.is_link_local:
                return "Access to internal addresses is restricted", 403
        except ValueError:
            # If not an IP address, check hostname against dangerous patterns
            dangerous_patterns = [
                r"^localhost$",
                r"^127\.",
                r"^0\.0\.0\.0",
                r"^10\.",
                r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
                r"^192\.168\.",
                r"^169\.254\."
            ]
            
            for pattern in dangerous_patterns:
                if re.match(pattern, hostname):
                    return "Access to internal addresses is restricted", 403
        
        # Set timeout and disable redirects for security
        response = requests.get(url, allow_redirects=False, timeout=5)
        return response.text
        
    except requests.exceptions.Timeout:
        return "Request timed out", 408
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to SSH server with host key verification"""
    ssh = paramiko.SSHClient()
    # Load system host keys
    ssh.load_system_host_keys()
    # Use RejectPolicy to reject connections to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH Error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)