import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
import csv
import json
from flask_socketio import SocketIO
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "notethat_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# Base folder for all files
BASE_FOLDER = "files"

# File paths
USERS_FILE = os.path.join(BASE_FOLDER, "users.csv")
GROUPS_FILE = os.path.join(BASE_FOLDER, "groups.csv")
NOTES_FILE = os.path.join(BASE_FOLDER, "notes.csv")
GROUP_NOTES_FILE = os.path.join(BASE_FOLDER, "group_notes.csv")  # Separate CSV for group notes
TIME_LOG_FILE = os.path.join(BASE_FOLDER, "time_log.csv")         # CSV for time logs
UPLOAD_FOLDER = os.path.join(BASE_FOLDER, "uploads")
               
# Ensure necessary folders exist
os.makedirs(BASE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

### UTILITY FUNCTIONS ###

# NOTE FUNCTIONS
def save_note(username, note_name, content):
    timestamp = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
    user_notes = load_notes(username)
    for note in user_notes:
        if note["name"] == note_name:
            note["content"] = content
            note["timestamp"] = timestamp
            break
    else:
        user_notes.append({"name": note_name, "content": content, "timestamp": timestamp})
    all_rows = []
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", newline="") as f:
            reader = list(csv.reader(f))
            if reader:
                for row in reader[1:]:
                    if row[0] != username:
                        all_rows.append(row)
    for note in user_notes:
        all_rows.append([username, note["name"], note["content"], note["timestamp"]])
    with open(NOTES_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "note_name", "content", "timestamp"])
        writer.writerows(all_rows)

def load_notes(username):
    notes = []
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 4 and row[0] == username:
                    notes.append({"name": row[1], "content": row[2], "timestamp": row[3]})
    return notes

def delete_note(username, note_name):
    all_rows = []
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", newline="") as file:
            reader = list(csv.reader(file))
            for row in reader[1:]:
                if not (row[0] == username and row[1] == note_name):
                    all_rows.append(row)
    with open(NOTES_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "note_name", "content", "timestamp"])
        writer.writerows(all_rows)

def delete_all_notes(username):
    all_rows = []
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", newline="") as file:
            reader = list(csv.reader(file))
            for row in reader[1:]:
                if row[0] != username:
                    all_rows.append(row)
    with open(NOTES_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "note_name", "content", "timestamp"])
        writer.writerows(all_rows)

# GROUP NOTE FUNCTIONS
def save_group_note(group_name, username, note_title, content):
    timestamp = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
    notes = load_group_notes(group_name)
    updated = False
    for note in notes:
        if note["note_title"] == note_title and note["username"] == username:
            note["content"] = content
            note["timestamp"] = timestamp
            updated = True
            break
    if not updated:
        notes.append({
            "group_name": group_name,
            "username": username,
            "note_title": note_title,
            "content": content,
            "timestamp": timestamp
        })
    with open(GROUP_NOTES_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["group_name", "username", "note_title", "content", "timestamp"])
        for note in notes:
            writer.writerow([note["group_name"], note["username"], note["note_title"], note["content"], note["timestamp"]])

def load_group_notes(group_name):
    notes = []
    if os.path.exists(GROUP_NOTES_FILE):
        with open(GROUP_NOTES_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 5 and row[0] == group_name:
                    notes.append({
                        "group_name": row[0],
                        "username": row[1],
                        "note_title": row[2],
                        "content": row[3],
                        "timestamp": row[4]
                    })
    return notes

# TIME LOG FUNCTIONS
TIME_LOG_HEADER = ["username", "group_name", "status", "timestamp"]

def save_time_log(username, group_name, status):
    timestamp = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
    if os.path.exists(TIME_LOG_FILE) and not os.access(TIME_LOG_FILE, os.W_OK):
        print(f"Permission issue: {TIME_LOG_FILE} is not writable")
    with open(TIME_LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        if os.stat(TIME_LOG_FILE).st_size == 0:
            writer.writerow(TIME_LOG_HEADER)
        writer.writerow([username, group_name, status, timestamp])
    return timestamp

def load_time_logs():
    logs = {}
    if os.path.exists(TIME_LOG_FILE):
        with open(TIME_LOG_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 4:
                    uname, gname, status, timestamp = row[0], row[1], row[2], row[3]
                    if gname not in logs:
                        logs[gname] = []
                    logs[gname].append({
                        "username": uname,
                        "status": status,
                        "timestamp": timestamp
                    })
    return logs

# USER & GROUP MANAGEMENT
def load_users():
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 7:
                    user = {
                        "first_name": row[0],
                        "middle_name": row[1],
                        "last_name": row[2],
                        "username": row[3],
                        "email": row[4],
                        "password": row[5],
                        "profile_pic": row[6] if row[6] else "default.png"
                    }
                    if len(row) >= 8:
                        user["age"] = row[7]
                    else:
                        user["age"] = ""
                    users.append(user)
    return users

def get_user_info(username):
    return next((user for user in load_users() if user["username"] == username), None)

def load_user_groups(username):
    groups = []
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and username in row[1:]:
                    groups.append({
                        "name": row[0],
                        "members": row[1:]
                    })
    return groups

def delete_group_entirely(group_name):
    all_rows = []
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r", newline="") as file:
            reader = list(csv.reader(file))
            for row in reader:
                if row and row[0] != group_name:
                    all_rows.append(row)
        with open(GROUPS_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            for row in all_rows:
                writer.writerow(row)

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

def update_username_in_groups(old_username, new_username):
    if os.path.exists(GROUPS_FILE):
        updated_rows = []
        with open(GROUPS_FILE, "r", newline="") as file:
            reader = list(csv.reader(file))
            for row in reader:
                new_row = [row[0]] + [new_username if elem == old_username else elem for elem in row[1:]]
                updated_rows.append(new_row)
        with open(GROUPS_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

def update_username_in_group_notes(old_username, new_username):
    if os.path.exists(GROUP_NOTES_FILE):
        updated_rows = []
        with open(GROUP_NOTES_FILE, "r", newline="") as file:
            reader = list(csv.reader(file))
            if reader:
                header = reader[0]
                updated_rows.append(header)
                for row in reader[1:]:
                    if len(row) >= 2 and row[1] == old_username:
                        row[1] = new_username
                    updated_rows.append(row)
        with open(GROUP_NOTES_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

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

### NEW ENDPOINTS FOR AUTOMATIC DOWNLOADS

@app.route("/download_signup_csv")
def download_signup_csv():
    if "signup_username" not in session:
        return redirect(url_for("login"))
    username = session["signup_username"]
    user_info = get_user_info(username)
    if not user_info:
        return "User not found", 404
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["username", "email", "password"])
    writer.writerow([user_info["username"], user_info["email"], user_info["password"]])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                 download_name=f"{username}_credentials.csv",
                 as_attachment=True,
                 mimetype="text/csv")

@app.route("/download_notes")
def download_notes():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["note_name", "content", "timestamp"])
    for note in load_notes(username):
        writer.writerow([note["name"], note["content"], note["timestamp"]])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                 download_name=f"{username}_notes.csv",
                 as_attachment=True,
                 mimetype="text/csv")


@app.route("/download_group_notes")
@app.route("/download_group_notes")
def download_group_notes():
    group_name = request.args.get("group_name")
    if not group_name:
        return "Group name not provided", 400

    # Load group notes
    notes = load_group_notes(group_name)
    
    # Load time logs for this group
    all_logs = load_time_logs().get(group_name, [])
    current_status = {}
    # Compute latest status per member
    for log in all_logs:
        uname = log["username"]
        ts = safe_parse_timestamp(log["timestamp"])
        if uname not in current_status or ts > safe_parse_timestamp(current_status[uname]["timestamp"]):
            current_status[uname] = {"status": log["status"], "timestamp": log["timestamp"]}

    # Create CSV with header including member status and its timestamp
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["username", "note_title", "content", "note_timestamp", "member_status", "status_timestamp"])
    for note in notes:
        uname = note["username"]
        if uname in current_status:
            m_status = current_status[uname]["status"]
            status_ts = current_status[uname]["timestamp"]
        else:
            m_status = "Clock In"
            status_ts = ""
        writer.writerow([uname, note["note_title"], note["content"], note["timestamp"], m_status, status_ts])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                    download_name=f"{group_name}_notes.csv",
                    as_attachment=True,
                    mimetype="text/csv")


### ROUTES ###

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
            updated_rows = []
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, "r", newline="") as file:
                    reader = list(csv.reader(file))
                    header = reader[0] if reader else ["first_name", "middle_name", "last_name", "username", "email", "password", "profile_pic", "age"]
                    updated_rows.append(header)
                    for row in reader[1:]:
                        if row[3] == username:
                            row[0] = new_first or row[0]
                            row[1] = new_middle or row[1]
                            row[2] = new_last or row[2]
                            row[3] = new_username or row[3]
                            row[4] = new_email or row[4]
                            row[5] = new_password or row[5]
                            if len(row) >= 8:
                                row[7] = new_age or row[7]
                            else:
                                row.append(new_age)
                            if new_profile:
                                row[6] = new_profile
                        updated_rows.append(row)
                with open(USERS_FILE, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(updated_rows)
                if new_username and new_username != username:
                    update_username_in_groups(username, new_username)
                    update_username_in_group_notes(username, new_username)
                    session["username"] = new_username
                if new_profile:
                    session["profile_pic"] = new_profile
            return redirect(url_for("settings", section="account"))
        
        elif section == "manageNotes":
            if "delete_selected" in request.form:
                selected = request.form.getlist("selected_notes")
                for note in selected:
                    delete_note(username, note)
            elif "delete_all" in request.form:
                delete_all_notes(username)
            return redirect(url_for("settings", section="manageNotes"))
        
        elif section == "manageGroups":
            if "delete_selected" in request.form:
                selected = request.form.getlist("selected_groups")
                for group in selected:
                    delete_group_entirely(group)
            elif "delete_all" in request.form:
                user_groups = load_user_groups(username)
                for group in user_groups:
                    delete_group_entirely(group["name"])
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
        with open(USERS_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            if os.stat(USERS_FILE).st_size == 0:
                writer.writerow(["first_name", "middle_name", "last_name", "username", "email", "password", "profile_pic", "age"])
            writer.writerow([first_name, "", last_name, username, email, password, profile_path, ""])
        session["signup_username"] = username
        return render_template("download_signup.html")
    return render_template("Signup_Page.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        with open(USERS_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 6 and row[4] == email and row[5] == password:
                    session["username"] = row[3]
                    session["profile_pic"] = row[6] if row[6] else "default.png"
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
                # Redirect with download_csv flag so that JS triggers auto-download once
                return redirect(url_for("user_page", selected_note=note_title, download_csv=1))
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
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r") as file:
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
                with open(GROUPS_FILE, "a", newline="") as file:
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
    group_members = []
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == group_name:
                    group_members = list(dict.fromkeys(row[1:]))
                    break
    if not group_members:
        return redirect(url_for("user_page"))
    all_users = load_users()
    group_members_details = []
    for member_username in group_members:
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
                        'timestamp': datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
                    }
                })
                # Redirect with download_csv flag for group notes
                return redirect(url_for("group_page", group_name=group_name, selected_note=note_title, download_csv=1))
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

if __name__ == "__main__":
    # Optional but recommended for full compatibility
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
