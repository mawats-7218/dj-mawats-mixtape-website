# DJ Mawats Mixtape Website

A beginner-friendly Flask website for publishing mixtapes with:
- public home and mixtape pages
- audio streaming
- downloads
- admin login
- audio + cover uploads
- SQLite database
- responsive mobile layout

## Run on Windows / VS Code

1. Open this folder in VS Code.
2. Open the VS Code terminal.
3. Create a virtual environment:
   `py -m venv .venv`
4. Activate it:
   `.venv\Scripts\Activate.ps1`
5. Install packages:
   `pip install -r requirements.txt`
6. Optional: set admin credentials before running:
   PowerShell:
   `$env:ADMIN_USER="admin"`
   `$env:ADMIN_PASSWORD="your-strong-password"`
   `$env:SECRET_KEY="replace-with-a-long-random-secret"`
7. Start:
   `py app.py`
8. Open:
   http://127.0.0.1:5000

Default demo login if you do not set environment variables:
username: admin
password: change-me

IMPORTANT FOR A REAL PUBLIC SITE:
- Change the admin password and SECRET_KEY.
- Do not use Flask debug mode in production.
- Put the site behind HTTPS.
- Set upload size limits and storage limits.
- Use a production WSGI server and persistent storage.
- Only upload music/artwork you have rights to distribute.
