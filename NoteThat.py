from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime
import os
import csv
import io

app = Flask(__name__)
app.secret_key = "notethat_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# Use PostgreSQL database from Railway, or fallback to SQLite for local testing
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///notethat.db")

# Ensure compatibility with SQLAlchemy (Railway uses "postgres://", but SQLAlchemy expects "postgresql://")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#############################
# Database Models
#############################

# Association table for many-to-many relationship between Groups and Users
group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(200), default="default.png")
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    notes = db.relationship("Note", backref="user", lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    members = db.relationship('User', secondary=group_members, backref=db.backref('groups', lazy='dynamic'))

class GroupNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    note_title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.String(100))

class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50))
    timestamp = db.Column(db.String(100))

#############################
# File Storage Configuration
#############################

# Set the base folder to a folder named "NoteThat" on the user's Desktop.
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "NoteThat")
BASE_FOLDER = DESKTOP_PATH
UPLOAD_FOLDER = os.path.join(BASE_FOLDER, "uploads")

# Ensure necessary folders exist
os.makedirs(BASE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#############################
# Utility Functions
#############################

def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# NOTE FUNCTIONS
def save_note(username, note_title, content):
    user = User.query.filter_by(username=username).first()
    if not user:
        return
    note = Note.query.filter_by(user_id=user.id, note_name=note_title).first()
    timestamp = current_timestamp()
    if note:
        note.content = content
        note.timestamp = timestamp
    else:
        note = Note(note_name=note_title, content=content, timestamp=timestamp, user_id=user.id)
        db.session.add(note)
    db.session.commit()

def load_notes(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return []
    notes = Note.query.filter_by(user_id=user.id).all()
    return [{"name": n.note_name, "content": n.content, "timestamp": n.timestamp} for n in notes]

def delete_note(username, note_title):
    user = User.query.filter_by(username=username).first()
    if not user:
        return
    note = Note.query.filter_by(user_id=user.id, note_name=note_title).first()
    if note:
        db.session.delete(note)
        db.session.commit()

def delete_all_notes(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return
    notes = Note.query.filter_by(user_id=user.id).all()
    for note in notes:
        db.session.delete(note)
    db.session.commit()

# GROUP NOTE FUNCTIONS
def save_group_note(group_name, username, note_title, content):
    timestamp = current_timestamp()
    note = GroupNote.query.filter_by(group_name=group_name, username=username, note_title=note_title).first()
    if note:
        note.content = content
        note.timestamp = timestamp
    else:
        note = GroupNote(group_name=group_name, username=username, note_title=note_title,
                         content=content, timestamp=timestamp)
        db.session.add(note)
    db.session.commit()

def load_group_notes(group_name):
    notes = GroupNote.query.filter_by(group_name=group_name).all()
    return [{
        "group_name": n.group_name,
        "username": n.username,
        "note_title": n.note_title,
        "content": n.content,
        "timestamp": n.timestamp
    } for n in notes]

# TIME LOG FUNCTIONS
def save_time_log(username, group_name, status):
    timestamp = current_timestamp()
    log = TimeLog(username=username, group_name=group_name, status=status, timestamp=timestamp)
    db.session.add(log)
    db.session.commit()
    return timestamp

def load_time_logs():
    logs = TimeLog.query.all()
    result = {}
    for log in logs:
        if log.group_name not in result:
            result[log.group_name] = []
        result[log.group_name].append({
            "username": log.username,
            "status": log.status,
            "timestamp": log.timestamp
        })
    return result

# USER & GROUP MANAGEMENT
def load_users():
    users = User.query.all()
    return [{
        "username": u.username,
        "email": u.email,
        "profile_pic": u.profile_pic
    } for u in users]

def get_user_info(username):
    return User.query.filter_by(username=username).first()

def load_user_groups(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return []
    groups = user.groups.all()
    return [{"name": g.name, "members": [member.username for member in g.members]} for g in groups]

def delete_group_entirely(group_name):
    group = Group.query.filter_by(name=group_name).first()
    if group:
        db.session.delete(group)
        db.session.commit()

def safe_parse_timestamp(ts):
    formats = [
        "%I:%M:%S %p %Y-%m-%d",
        "%Y-%m-%d %I:%M:%S %p",
        "%Y-%m-%d %H:%M:%S",
        "%I:%M:%S %p %d-%m-%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return datetime.min

def update_username_in_group_notes(old_username, new_username):
    notes = GroupNote.query.filter_by(username=old_username).all()
    for note in notes:
        note.username = new_username
    db.session.commit()

# LANGUAGE & THEME HELPERS
def load_options(filepath):
    options = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            options = [opt.strip() for opt in content.split("\n\n") if opt.strip()]
    return options

def get_theme_colors(theme):
    mapping = {
        "Midnight Slate (Default)": {"bg": "#333", "text": "white"},
        "Urban Noir": {"bg": "#111", "text": "#ccc"},
        "Twilight Ember": {"bg": "#4a0e0e", "text": "#f0d9b5"},
        "Arctic Ice": {"bg": "#e0f7fa", "text": "#006064"},
        "Forest Canopy": {"bg": "#2e4600", "text": "#a3c586"},
        "Electric Violet": {"bg": "#2e004f", "text": "#e0b0ff"},
        "Solar Flare": {"bg": "#b33000", "text": "#ffe0b3"},
        "Ocean Depths": {"bg": "#012a4a", "text": "#ffffff"},
        "Desert Mirage": {"bg": "#c19a6b", "text": "#5b4636"},
    }
    return mapping.get(theme, {"bg": "#333", "text": "white"})

@app.context_processor
def inject_translations():
    return {"translations": {"app_name": "Note That"}}

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

#############################
#         ROUTES            #
#############################

@app.route("/settings", methods=["GET", "POST"])
def settings():
    section = request.args.get("section", "account")
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        if section == "account":
            new_first = request.form.get("firstName", "").strip()
            new_middle = request.form.get("middleName", "").strip()
            new_last = request.form.get("lastName", "").strip()
            new_username = request.form.get("username", "").strip()
            new_email = request.form.get("email", "").strip()
            new_password = request.form.get("password", "").strip()
            new_age = request.form.get("age", "").strip()
            profile_file = request.files.get("profilePic")
            new_profile = None
            if profile_file and profile_file.filename:
                new_profile = profile_file.filename
                profile_file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_profile))
            user = get_user_info(username)
            if user:
                user.first_name = new_first or user.first_name
                if hasattr(user, "middle_name"):
                    user.middle_name = new_middle or user.middle_name
                user.last_name = new_last or user.last_name
                user.username = new_username or user.username
                user.email = new_email or user.email
                user.password = new_password or user.password
                if new_profile:
                    user.profile_pic = new_profile
                db.session.commit()
                if new_username and new_username != username:
                    update_username_in_group_notes(username, new_username)
                    session["username"] = new_username
                if new_profile:
                    session["profile_pic"] = new_profile
            return redirect(url_for("settings", section="account"))
        
        elif section == "manageNotes":
            return redirect(url_for("settings", section="manageNotes"))
        
        elif section == "manageGroups":
            return redirect(url_for("settings", section="manageGroups"))
        
        elif section == "notifications":
            notif = request.form.get("notifToggle", "disabled")
            session["notifications"] = notif
            return redirect(url_for("settings", section="notifications"))
        
        elif section == "logout":
            session.clear()
            return redirect(url_for("login"))
    
    user_info = get_user_info(username)
    user_notes = load_notes(username)
    user_groups = load_user_groups(username)
    settings_nav = ["Account", "Manage Notes", "Manage Groups", "About", "Log Out"]
    
    return render_template("Settings.html",
                           section=section,
                           user=user_info,
                           user_notes=user_notes,
                           user_groups=user_groups,
                           settings_nav=settings_nav)

@app.route("/")
def home():
    return redirect(url_for("user_page"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("txtf1", "").strip()
        last_name = request.form.get("txtf3", "").strip()
        username = request.form.get("txtf4", "").strip()
        email = request.form.get("txtf5", "").strip()
        password = request.form.get("txtf6", "").strip()
        profile_pic = request.files.get("usrphtbtn")
        if not first_name or not last_name or not username or not email or not password:
            return "Error: Please fill in all required fields."
        profile_path = "default.png"
        if profile_pic and profile_pic.filename:
            profile_path = profile_pic.filename
            profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER"], profile_path))
        new_user = User(
            username=username,
            email=email,
            password=password,
            profile_pic=profile_path,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("Signup_Page.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["username"] = user.username
            session["profile_pic"] = user.profile_pic if user.profile_pic else "default.png"
            return redirect(url_for("user_page"))
        return "Error: Invalid email or password"
    return render_template("Login_Page.html")

@app.route("/user", methods=["GET", "POST"])
def user_page():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    profile_pic = url_for("static", filename=f"uploads/{session['profile_pic']}") if "profile_pic" in session else url_for("static", filename="uploads/default.png")
    saved_notes = load_notes(username)
    note_title, note_content = "", ""
    if request.method == "POST":
        if "delete_note" in request.form:
            to_delete = request.form.getlist("delete_notes")
            for note in to_delete:
                delete_note(username, note)
            return redirect(url_for("user_page"))
        elif "delete_all" in request.form:
            delete_all_notes(username)
            return redirect(url_for("user_page"))
        elif "save_note" in request.form:
            note_title = request.form.get("note_title", "").strip()
            note_content = request.form.get("note_content", "").strip()
            if note_title:
                save_note(username, note_title, note_content)
                return redirect(url_for("user_page", selected_note=note_title))
        elif "new_note" in request.form:
            return redirect(url_for("user_page"))
    selected_note = request.args.get("selected_note")
    if selected_note:
        for note in saved_notes:
            if note["name"] == selected_note:
                note_title = note["name"]
                note_content = note["content"]
                break
    highlight_note = request.args.get("highlight_note")
    groups = []
    if os.path.exists("groups.csv"):
        with open("groups.csv", "r") as file:
            reader = csv.reader(file)
            groups = [{"name": row[0], "members": row[1:]} for row in reader]
    return render_template("UserPage.html",
                           username=username,
                           profile_pic=profile_pic,
                           saved_notes=saved_notes,
                           note_title=note_title,
                           note_content=note_content,
                           highlight_note=highlight_note,
                           groups=groups,
                           theme=session.get("theme", "Midnight Slate (Default)"),
                           language=session.get("language", "en"))

@app.route("/create_group", methods=["GET", "POST"])
def create_group():
    if "username" not in session:
        return redirect(url_for("login"))
    all_users = load_users()
    current_user = session["username"]
    selected_members = request.form.getlist("members")
    if current_user not in selected_members:
        selected_members.insert(0, current_user)
    group_name = request.form.get("group_name", "")
    search_query = request.form.get("search_query", "")
    search_results = []
    if request.method == "POST":
        if "search" in request.form:
            if search_query:
                search_results = [u for u in all_users if search_query.lower() in u["username"].lower()]
        elif "add_user" in request.form:
            user_to_add = request.form.get("add_user")
            if user_to_add and user_to_add not in selected_members:
                selected_members.append(user_to_add)
        elif "create_group" in request.form:
            if selected_members:
                with open("groups.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([group_name] + selected_members)
                return redirect(url_for("group_page", group_name=group_name))
    user_dict = {u["username"]: u for u in all_users}
    return render_template("CreateGroup.html",
                           group_name=group_name,
                           selected_members=selected_members,
                           search_query=search_query,
                           search_results=search_results,
                           user_dict=user_dict,
                           theme=session.get("theme", "Midnight Slate (Default)"),
                           language=session.get("language", "en"))

@app.route("/search_user")
def search_user():
    query = request.args.get("q", "").lower()
    users = load_users()
    filtered_users = [u for u in users if query in u["username"].lower()]
    return jsonify(filtered_users)

@app.route("/time_page", methods=["GET", "POST"])
def time_page():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    group_name = request.args.get("group_name", "")
    if not group_name:
        return redirect(url_for("user_page"))
    if request.method == "POST":
        if request.form.get("clock_in"):
            status = "Clock In"
            save_time_log(username, group_name, status)
        elif request.form.get("clock_out"):
            status = "Clock Out"
            save_time_log(username, group_name, status)
        return redirect(url_for("group_page", group_name=group_name))
    return render_template("TimePage.html", username=username,
                           theme=session.get("theme", "Midnight Slate (Default)"),
                           language=session.get("language", "en"))

@app.route("/group_page", methods=["GET", "POST"])
def group_page():
    if "username" not in session:
        return redirect(url_for("login"))
    group_name = request.args.get("group_name") or request.form.get("group_name")
    if not group_name:
        return redirect(url_for("user_page"))
    groups = []
    if os.path.exists("groups.csv"):
        with open("groups.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == group_name:
                    groups = list(dict.fromkeys(row[1:]))
                    break
    if not groups:
        return redirect(url_for("user_page"))
    all_users = load_users()
    group_members_details = []
    for member_username in groups:
        for u in all_users:
            if u["username"] == member_username:
                group_members_details.append(u)
                break
    group_notes = load_group_notes(group_name)
    all_time_logs = load_time_logs()
    combined_logs = all_time_logs.get(group_name, [])
    combined_logs.sort(key=lambda x: safe_parse_timestamp(x["timestamp"]))
    current_status = {}
    for member in group_members_details:
        member_logs = [log for log in combined_logs if log["username"] == member["username"]]
        if member_logs:
            sorted_logs = sorted(member_logs, key=lambda x: safe_parse_timestamp(x["timestamp"]))
            current_status[member["username"]] = sorted_logs[-1]["status"]
        else:
            current_status[member["username"]] = "Clock In"
    note_title = ""
    note_content = ""
    editable = True
    if request.method == "POST":
        if "save_note" in request.form:
            note_title = request.form.get("note_title", "").strip()
            note_content = request.form.get("note_content", "").strip()
            if note_title:
                save_group_note(group_name, session["username"], note_title, note_content)
                socketio.emit('update_group_notes', {
                    'group_name': group_name,
                    'note': {
                        'username': session["username"],
                        'note_title': note_title,
                        'timestamp': current_timestamp()
                    }
                })
                return redirect(url_for("group_page", group_name=group_name, selected_note=note_title))
        elif "new_note" in request.form:
            return redirect(url_for("group_page", group_name=group_name))
    selected_note = request.args.get("selected_note")
    if selected_note:
        for note in group_notes:
            if note["note_title"] == selected_note:
                note_title = note["note_title"]
                note_content = note["content"]
                editable = (note["username"] == session["username"])
                break
    return render_template("GroupPage.html",
                           group_name=group_name,
                           group_members=group_members_details,
                           group_notes=group_notes,
                           note_title=note_title,
                           note_content=note_content,
                           selected_note=selected_note,
                           logs=combined_logs,
                           current_status=current_status,
                           editable=editable,
                           theme=session.get("theme", "Midnight Slate (Default)"),
                           language=session.get("language", "en"))

@app.route("/set_theme", methods=["POST"])
def set_theme():
    selected_theme = request.form.get("theme", "")
    session["theme"] = selected_theme
    return redirect(request.referrer or url_for("user_page"))

@app.route("/set_language", methods=["POST"])
def set_language():
    selected_language = request.form.get("language", "")
    session["language"] = selected_language
    return redirect(request.referrer or url_for("user_page"))

# NEW: Route to provide CSV content of user's notes for client-side download/update.
@app.route("/download_notes")
def download_notes():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    notes = load_notes(username)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["username", "note_name", "content", "timestamp"])
    for note in notes:
        writer.writerow([username, note["name"], note["content"], note["timestamp"]])
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={username}_notes.csv"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT environment variable or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)

