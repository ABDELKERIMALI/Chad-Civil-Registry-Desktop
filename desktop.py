
import os
import sys
import time
import threading
import secrets
import webview

from pathlib import Path
from flask import redirect, url_for
from app import create_app, db


APP_NAME = "Chad Civil Registry"
HOST = "127.0.0.1"
PORT = 5000


def get_data_dir():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    data_dir = base / "ChadCivilRegistry"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DATA_DIR = get_data_dir()
os.environ["DATABASE_URL"] = f"sqlite:///{(DATA_DIR / 'civil_registry.db').as_posix()}"

secret_file = DATA_DIR / "secret_key"
if secret_file.exists():
    secret_key = secret_file.read_text(encoding="utf-8").strip()
else:
    secret_key = secrets.token_urlsafe(48)
    secret_file.write_text(secret_key, encoding="utf-8")

os.environ["SECRET_KEY"] = secret_key

app = create_app("production")


@app.route("/")
def index():
    return redirect(url_for("auth.login"))


def run_server():
    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    import urllib.request

    url = f"http://{HOST}:{PORT}/"
    for _ in range(50):
        try:
            with urllib.request.urlopen(url, timeout=1):
                break
        except Exception:
            time.sleep(0.2)
    else:
        raise RuntimeError("Flask server failed to start on port 5000.")

    webview.create_window(
        APP_NAME,
        url,
        width=1280,
        height=800,
        min_size=(900, 600),
    )
    webview.start()
