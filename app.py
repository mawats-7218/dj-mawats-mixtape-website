from flask import Flask, render_template, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import sqlite3, os, uuid

BASE = Path(__file__).resolve().parent
DB = BASE / "mixtapes.db"
AUDIO_DIR = BASE / "static" / "uploads" / "audio"
COVER_DIR = BASE / "static" / "uploads" / "covers"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
COVER_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")

ALLOWED_AUDIO = {"mp3", "wav", "m4a", "ogg"}
ALLOWED_IMAGES = {"jpg", "jpeg", "png", "webp"}

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mixtapes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            description TEXT,
            audio TEXT NOT NULL,
            cover TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def allowed(filename, extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions

@app.route("/googlec3007d139a378b35.html")
def google_verification():
    return send_from_directory(".", "googlec3007d139a378b35.html")

@app.route("/")
def home():
    conn = db()
    mixes = conn.execute("SELECT * FROM mixtapes ORDER BY id DESC LIMIT 6").fetchall()
    conn.close()
    return render_template("index.html", mixtapes=mixes)

@app.route("/mixtapes")
def mixtapes():
    conn = db()
    mixes = conn.execute("SELECT * FROM mixtapes ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("mixtapes.html", mixtapes=mixes)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("upload"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        description = request.form.get("description", "").strip()
        audio = request.files.get("audio")
        cover = request.files.get("cover")

        if not title or not audio or not audio.filename:
            flash("Title and audio file are required.", "error")
            return redirect(url_for("upload"))

        if not allowed(audio.filename, ALLOWED_AUDIO):
            flash("Audio must be MP3, WAV, M4A or OGG.", "error")
            return redirect(url_for("upload"))

        audio_name = f"{uuid.uuid4().hex}_{secure_filename(audio.filename)}"
        audio.save(AUDIO_DIR / audio_name)

        cover_name = None
        if cover and cover.filename:
            if not allowed(cover.filename, ALLOWED_IMAGES):
                flash("Cover must be JPG, PNG or WEBP.", "error")
                (AUDIO_DIR / audio_name).unlink(missing_ok=True)
                return redirect(url_for("upload"))
            cover_name = f"{uuid.uuid4().hex}_{secure_filename(cover.filename)}"
            cover.save(COVER_DIR / cover_name)

        conn = db()
        conn.execute(
            "INSERT INTO mixtapes (title, genre, description, audio, cover) VALUES (?, ?, ?, ?, ?)",
            (title, genre, description, audio_name, cover_name)
        )
        conn.commit()
        conn.close()
        flash("Mixtape uploaded successfully!", "success")
        return redirect(url_for("mixtapes"))

    return render_template("upload.html")

@app.post("/delete/<int:mix_id>")
def delete_mix(mix_id):
    if not session.get("admin"):
        abort(403)
    conn = db()
    mix = conn.execute("SELECT * FROM mixtapes WHERE id=?", (mix_id,)).fetchone()
    if mix:
        conn.execute("DELETE FROM mixtapes WHERE id=?", (mix_id,))
        conn.commit()
        if mix["audio"]:
            (AUDIO_DIR / mix["audio"]).unlink(missing_ok=True)
        if mix["cover"]:
            (COVER_DIR / mix["cover"]).unlink(missing_ok=True)
    conn.close()
    return redirect(url_for("mixtapes"))

init_db()

if __name__ == "__main__":
    app.run(debug=True)
