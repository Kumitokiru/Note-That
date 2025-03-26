import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_socketio import SocketIO
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
app.secret_key = "notethat_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

#######################################
# Google API Setup for Sheets & Drive
#######################################

# Define API scopes for Google Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load service account credentials from file
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

# Initialize Google Sheets client (gspread)
gs_client = gspread.authorize(creds)

# Open spreadsheets by URL (use your provided links)
USERS_SHEET = gs_client.open_by_url("https://docs.google.com/spreadsheets/d/1CawuBeZm_EHKj2wOcULfluuTLMJP1KzGLQv_azBOZmE/edit?usp=sharing").sheet1
GROUPS_SHEET = gs_client.open_by_url("https://docs.google.com/spreadsheets/d/1Mn-X01ot9bv1rk2uRLqIpO5pW-ka1o9RNUts9V0nn6c/edit?usp=sharing").sheet1
NOTES_SHEET = gs_client.open_by_url("https://docs.google.com/spreadsheets/d/1ByERqCAUyC0Bw42XDbJkKl4Zhk1SMdUiAxTrxdrHABk/edit?usp=sharing").sheet1
TIME_LOG_SHEET = gs_client.open_by_url("https://docs.google.com/spreadsheets/d/18RQhzRNSLJhKeFVrhQVT6WnsflYdHnbo5tNNjKKT29Q/edit?usp=sharing").sheet1
GROUP_NOTES_SHEET = gs_client.open_by_url("https://docs.google.com/spreadsheets/d/1bfKr_-2cwDk0_HT2fLyoG96My07N4ehNVs8esaXpWk0/edit?usp=sharing").sheet1

# Initialize Google Drive API client
drive_service = build("drive", "v3", credentials=creds)
# Extract the folder ID from your Uploads link:
# Example link: https://drive.google.com/drive/folders/1qagsZ601ppNzY5xdwah1Nd4elo_gi_QE?usp=sharing
UPLOADS_FOLDER_ID = "1qagsZ601ppNzY5xdwah1Nd4elo_gi_QE"

#######################################
# Utility Functions
#######################################

def current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#######################################
# Google Sheets Functions (Replace CSV)
#######################################

# --- Users ---
def save_user_to_sheet(first_name, last_name, username, email, password, profile_pic):
    # Append a new row; assume header row is already set in the sheet
    USERS_SHEET.append_row([first_name, "", last_name, username, email, password, profile_pic, ""])

def get_user_from_sheet(email, password):
    records = USERS_SHEET.get_all_records()
    for row in records:
        if row["email"] == email and row["password"] == password:
            return row  # returns a dict with keys: first_name, last_name, username, etc.
    return None

def update_user_in_sheet(username, new_data):
    # This is a simple approach: read all records, update in memory, then clear and rewrite the sheet.
    records = USERS_SHEET.get_all_records()
    USERS_SHEET.clear()
    # Write header back (assuming header order as below)
    header = ["first_name", "middle_name", "last_name", "username", "email", "password", "profile_pic", "age"]
    USERS_SHEET.append_row(header)
    for row in records:
        if row["username"] == username:
            row.update(new_data)
        USERS_SHEET.append_row([row["first_name"], row.get("middle_name", ""), row["last_name"],
                                 row["username"], row["email"], row["password"], row["profile_pic"], row.get("age", "")])

# --- Notes ---
def save_note(username, note_name, content):
    timestamp = current_timestamp()
    NOTES_SHEET.append_row([username, note_name, content, timestamp])

def load_notes(username):
    records = NOTES_SHEET.get_all_records()
    return [row for row in records if row["username"] == username]

def delete_note(username, note_name):
    records = NOTES_SHEET.get_all_records()
    NOTES_SHEET.clear()
    header = ["username", "note_name", "content", "timestamp"]
    NOTES_SHEET.append_row(header)
    for row in records:
        if not (row["username"] == username and row["note_name"] == note_name):
            NOTES_SHEET.append_row([row["username"], row["note_name"], row["content"], row["timestamp"]])

def delete_all_notes(username):
    records = NOTES_SHEET.get_all_records()
    NOTES_SHEET.clear()
    header = ["username", "note_name", "content", "timestamp"]
    NOTES_SHEET.append_row(header)
    for row in records:
        if row["username"] != username:
            NOTES_SHEET.append_row([row["username"], row["note_name"], row["content"], row["timestamp"]])

# --- Groups ---
def save_group(group_name, members):
    # Save group row: first cell group name, rest are member usernames.
    GROUPS_SHEET.append_row([group_name] + members)

def load_groups_for_user(username):
    records = GROUPS_SHEET.get_all_records()
    groups = []
    for row in records:
        # Assume first column is group name and subsequent columns are member usernames.
        members = [row[key] for key in row if key != "" and row[key] != ""]
        if username in members:
            groups.append({"name": row["group_name"], "members": members[1:]})
    return groups

# --- Time Log ---
def save_time_log(username, group_name, status):
    timestamp = current_timestamp()
    TIME_LOG_SHEET.append_row([username, group_name, status, timestamp])
    return timestamp

def load_time_logs():
    records = TIME_LOG_SHEET.get_all_records()
    logs = {}
    for row in records:
        gname = row["group_name"]
        if gname not in logs:
            logs[gname] = []
        logs[gname].append({"username": row["username"], "status": row["status"], "timestamp": row["timestamp"]})
    return logs

# --- Group Notes ---
def save_group_note(group_name, username, note_title, content):
    timestamp = current_timestamp()
    GROUP_NOTES_SHEET.append_row([group_name, username, note_title, content, timestamp])

def load_group_notes(group_name):
    records = GROUP_NOTES_SHEET.get_all_records()
    return [row for row in records if row["group_name"] == group_name]

#######################################
# Google Drive Function for Uploads
#######################################

def upload_to_drive(file_path, file_name):
    file_metadata = {
        "name": file_name,
        "parents": [UPLOADS_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype="image/png")  # Change mimetype as needed
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/uc?id={file['id']}"

#######################################
# Routes (Example for Signup, Login, Notes, etc.)
#######################################

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("txtf1", "").strip()
        last_name = request.form.get("txtf3", "").strip()
        username = request.form.get("txtf4", "").strip()
        email = request.form.get("txtf5", "").strip()
        password = request.form.get("txtf6", "").strip()
        profile_file = request.files.get("usrphtbtn")
        if not first_name or not last_name or not username or not email or not password:
            return "Error: Please fill in all required fields."
        profile_pic = "default.png"
        if profile_file and profile_file.filename:
            # Save temporarily then upload to Drive
            temp_path = os.path.join("/tmp", profile_file.filename)
            profile_file.save(temp_path)
            profile_pic = upload_to_drive(temp_path, profile_file.filename)
            os.remove(temp_path)
        # Save user data in Google Sheet
        save_user_to_sheet(first_name, last_name, username, email, password, profile_pic)
        return redirect(url_for("login"))
    return render_template("Signup_Page.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = get_user_from_sheet(email, password)
        if user:
            session["username"] = user["username"]
            session["profile_pic"] = user["profile_pic"]
            return redirect(url_for("user_page"))
        return "Error: Invalid email or password"
    return render_template("Login_Page.html")

@app.route("/user", methods=["GET", "POST"])
def user_page():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    # For profile picture, assume stored drive link
    profile_pic = session.get("profile_pic", url_for("static", filename="uploads/default.png"))
    saved_notes = load_notes(username)
    note_title, note_content = "", ""
    if request.method == "POST":
        if "save_note" in request.form:
            note_title = request.form.get("note_title", "").strip()
            note_content = request.form.get("note_content", "").strip()
            if note_title:
                save_note(username, note_title, note_content)
                return redirect(url_for("user_page", selected_note=note_title))
        # Handle deletion similarly...
    selected_note = request.args.get("selected_note")
    if selected_note:
        for note in saved_notes:
            if note["note_name"] == selected_note:
                note_title = note["note_name"]
                note_content = note["content"]
                break
    # For groups, you could load from GROUPS_SHEET similarly.
    groups = []  # (Implement as needed)
    return render_template("UserPage.html",
                           username=username,
                           profile_pic=profile_pic,
                           saved_notes=saved_notes,
                           note_title=note_title,
                           note_content=note_content,
                           groups=groups)

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
            save_time_log(username, group_name, "Clock In")
        elif request.form.get("clock_out"):
            save_time_log(username, group_name, "Clock Out")
        return redirect(url_for("group_page", group_name=group_name))
    return render_template("TimePage.html", username=username)

@app.route("/group_page", methods=["GET", "POST"])
def group_page():
    if "username" not in session:
        return redirect(url_for("login"))
    group_name = request.args.get("group_name") or request.form.get("group_name")
    if not group_name:
        return redirect(url_for("user_page"))
    # Load group members and group notes from GROUPS_SHEET and GROUP_NOTES_SHEET respectively
    # (Implementation will depend on how you structure your sheets.)
    group_members = []  # (Implement as needed)
    group_notes = load_group_notes(group_name)
    logs = load_time_logs().get(group_name, [])
    note_title, note_content = "", ""
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
                break
    return render_template("GroupPage.html",
                           group_name=group_name,
                           group_members=group_members,
                           group_notes=group_notes,
                           note_title=note_title,
                           note_content=note_content,
                           logs=logs)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Get the port from Render environment or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
