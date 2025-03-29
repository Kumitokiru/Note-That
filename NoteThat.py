from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
from flask_socketio import SocketIO, join_room
from datetime import datetime
import io
import csv
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.secret_key = "notethat_secret"  # Should be a strong, random key in production
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for development

# In-memory storage (consider replacing with a database like SQLite in production)
USERS = []
NOTES = []
GROUP_NOTES = []
TIME_LOGS = []
UPLOAD_FOLDER = "static/uploads"
GROUPS = []  # Global groups storage for all users

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

### Utility Functions ###

# User Management
def save_user(first_name, middle_name, last_name, username, email, password, profile_pic):
    """Save a new user with hashed password."""
    hashed_password = generate_password_hash(password)
    user = {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "username": username,
        "email": email,
        "password": hashed_password,  # Store hashed password
        "profile_pic": profile_pic
    }
    USERS.append(user)

def get_user_info(username):
    """Retrieve user info by username."""
    return next((user for user in USERS if user["username"] == username), None)

# Note Functions
def save_note(username, note_name, content):
    """Save or update a user's note with a timestamp."""
    timestamp = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
    for note in NOTES:
        if note["username"] == username and note["note_title"] == note_name:
            note["content"] = content
            note["timestamp"] = timestamp
            return timestamp  # Return the updated timestamp
    NOTES.append({
        "username": username,
        "note_title": note_name,
        "content": content,
        "timestamp": timestamp
    })
    return timestamp  # Return the new timestamp
    

def load_notes(username):
    """Load all notes for a user."""
    return [note for note in NOTES if note["username"] == username]

# Group Note Functions
def save_group_note(group_name, username, note_title, content):
    """Save or update a group note with a timestamp."""
    timestamp = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
    for note in GROUP_NOTES:
        if note["group_name"] == group_name and note["username"] == username and note["note_title"] == note_title:
            note["content"] = content
            note["timestamp"] = timestamp
            return
    GROUP_NOTES.append({
        "group_name": group_name,
        "username": username,
        "note_title": note_title,
        "content": content,
        "timestamp": timestamp
    })

def load_group_notes(group_name):
    """Load all notes for a group."""
    return [note for note in GROUP_NOTES if note["group_name"] == group_name]

# Time Log Functions
def save_time_log(username, group_name, status):
    """Save a time log entry with a timestamp."""
    timestamp = datetime.now().strftime("%I:%M:%S %p %Y-%m-%d")
    TIME_LOGS.append({"username": username, "group_name": group_name, "status": status, "timestamp": timestamp})
    return timestamp

def load_time_logs(group_name=None):
    """Load all time logs, optionally filtered by group."""
    if group_name:
        return [log for log in TIME_LOGS if log["group_name"] == group_name]
    return TIME_LOGS

# Search, Sort, and Filter Functions
def search_items(items, query, key):
    """Search items by a query string."""
    if not query:
        return items
    query = query.lower()
    return [item for item in items if query in item[key].lower()]

def sort_items(items, sort_by, key="timestamp"):
    if not sort_by:
        return items
    if sort_by == "newest":
        return sorted(items, key=lambda x: datetime.strptime(x[key], "%I:%M:%S %p %Y-%m-%d"), reverse=True)
    elif sort_by == "oldest":
        return sorted(items, key=lambda x: datetime.strptime(x[key], "%I:%M:%S %p %Y-%m-%d"))
    return items


def filter_by_date_range(items, start_date, end_date, key="timestamp"):
    """Filter items by a date range."""
    if not start_date or not end_date:
        return items
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return [item for item in items if start <= datetime.strptime(item[key], "%I:%M:%S %p %Y-%m-%d") <= end]
    except ValueError:
        return items  # Return unfiltered if date format is invalid

# CSV Generation
def generate_csv(data, headers, filename):
    """Generate a CSV file from data and send it as a download."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in data:
        writer.writerow([row.get(h.lower().replace(" ", "_"), "") for h in headers])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# Group Management
def load_user_groups(username):
    """Load all groups a user belongs to from the global GROUPS list."""
    return [g for g in GROUPS if username in g["members"]]

def update_username_in_groups(old_username, new_username):
    """Update a username in all group memberships stored in the global GROUPS list."""
    for group in GROUPS:
        if old_username in group["members"]:
            group["members"] = [new_username if m == old_username else m for m in group["members"]]

def update_username_in_group_notes(old_username, new_username):
    """Update a username in all group notes."""
    for note in GROUP_NOTES:
        if note["username"] == old_username:
            note["username"] = new_username



@app.after_request
def add_header(response):
    """Prevent caching of responses."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

### Routes ###

@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Handle user settings, including account updates and logout."""
    section = request.args.get("section", "account")
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    
    # Use the user info stored during login
    user_info = session.get("user_info", get_user_info(username))
    
    if request.method == "POST":
        if section == "account":
            try:
                new_first = request.form.get("firstName", "").strip()
                new_middle = request.form.get("middleName", "").strip()
                new_last = request.form.get("lastName", "").strip()
                new_username = request.form.get("username", "").strip()
                new_email = request.form.get("email", "").strip()
                new_password = request.form.get("password", "").strip()
                profile_file = request.files.get("profilePic")
                
                if profile_file and profile_file.filename:
                    profile_path = os.path.join(app.config["UPLOAD_FOLDER"], profile_file.filename)
                    profile_file.save(profile_path)
                    user_info["profile_pic"] = profile_file.filename
                    session["profile_pic"] = profile_file.filename
                
                user_info.update({
                    "first_name": new_first or user_info["first_name"],
                    "middle_name": new_middle or user_info["middle_name"],
                    "last_name": new_last or user_info["last_name"],
                    "username": new_username or user_info["username"],
                    "email": new_email or user_info["email"],
                    "password": generate_password_hash(new_password) if new_password else user_info["password"]
                })
                
                # Update session with new info
                session["user_info"] = user_info
                
                if new_username and new_username != username:
                    update_username_in_groups(username, new_username)
                    update_username_in_group_notes(username, new_username)
                    session["username"] = new_username
                
                return redirect(url_for("settings", section="account"))
            except Exception as e:
                return f"Error updating account: {str(e)}"
        
        elif section == "notifications":
            notif = request.form.get("notifToggle", "disabled")
            session["notifications"] = notif
            return redirect(url_for("settings", section="notifications"))
        
        elif section == "logout":
            session.clear()
            return redirect(url_for("login"))
    
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
    """Redirect to the user page."""
    return redirect(url_for("user_page"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    if request.method == "POST":
        try:
            first_name = request.form.get("txtf1", "").strip()
            middle_name = request.form.get("txtf2", "").strip()
            last_name = request.form.get("txtf3", "").strip()
            username = request.form.get("txtf4", "").strip()
            email = request.form.get("txtf5", "").strip()
            password = request.form.get("txtf6", "").strip()
            profile_pic = request.files.get("usrphtbtn")
            if not all([first_name, last_name, username, email, password]):
                return "Error: Please fill in all required fields."
            profile_path = "default.png"
            if profile_pic and profile_pic.filename:
                profile_path = profile_pic.filename
                profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER"], profile_path))
            save_user(first_name, middle_name, last_name, username, email, password, profile_path)
            return redirect(url_for("login"))
        except Exception as e:
            return f"Error during signup: {str(e)}"
    return render_template("Signup_Page.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login with password verification."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = next((u for u in USERS if u["email"] == email), None)
        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["profile_pic"] = user["profile_pic"]
            # Store complete user info in session for later use
            session["user_info"] = user
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
        if "save_note" in request.form:
            note_title = request.form.get("note_title", "").strip()
            note_content = request.form.get("note_content", "").strip()
            if note_title:
                timestamp = save_note(username, note_title, note_content)
                # Get the updated list of saved notes to update the left sidebar
                updated_notes = load_notes(username)
                # Emit an event with the entire saved_notes list along with the new note's title and timestamp
                socketio.emit('update_notes', {
                    'saved_notes': updated_notes,
                    'note_title': note_title,
                    'timestamp': timestamp
                }, room=username)
                return redirect(url_for("user_page", selected_note=note_title))
        elif "new_note" in request.form:
            return redirect(url_for("user_page"))
        elif "all_notes" in request.form:
            return redirect(url_for("all_notes"))
    
    selected_note = request.args.get("selected_note")
    if selected_note:
        for note in saved_notes:
            if note["note_title"] == selected_note:
                note_title = note["note_title"]
                note_content = note["content"]
                break
    highlight_note = request.args.get("highlight_note")
    groups = load_user_groups(username)
    return render_template("UserPage.html",
                           username=username,
                           profile_pic=profile_pic,
                           saved_notes=saved_notes,
                           note_title=note_title,
                           note_content=note_content,
                           highlight_note=highlight_note,
                           groups=groups,
                           )

@app.route("/all_notes", methods=["GET", "POST"])
def all_notes():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    notes = load_notes(username)
    
    # Check for sort parameter in GET request
    sort_by = request.args.get("sort")
    if sort_by:
        notes = sort_items(notes, sort_by)
    
    if request.method == "POST":
        if "search" in request.form:
            search_query = request.form.get("searchInput", "")
            notes = search_items(notes, search_query, "note_title")
        elif "show" in request.form:
            start_date = request.form.get("input1", "")
            end_date = request.form.get("input2", "")
            notes = filter_by_date_range(notes, start_date, end_date)
        elif "download" in request.form:
            return generate_csv(notes, ["Note Title", "Content", "Timestamp"], "user_notes.csv")
        elif "back" in request.form:
            return redirect(url_for("user_page"))
    
    return render_template("AllUserNotes.html", notes=notes)


@app.route("/create_group", methods=["GET", "POST"])
def create_group():
    """Handle group creation with user search and addition."""
    if "username" not in session:
        return redirect(url_for("login"))
    all_users = USERS
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
                # Append group data to the global GROUPS list
                GROUPS.append({"name": group_name, "members": selected_members})
                return redirect(url_for("group_page", group_name=group_name))
    user_dict = {u["username"]: u for u in all_users}
    return render_template("CreateGroup.html",
                           group_name=group_name,
                           selected_members=selected_members,
                           search_query=search_query,
                           search_results=search_results,
                           user_dict=user_dict,
                           )

@app.route("/search_user")
def search_user():
    """API endpoint to search users by username."""
    query = request.args.get("q", "").lower()
    users = USERS
    filtered_users = [u for u in users if query in u["username"].lower()]
    return jsonify(filtered_users)

@app.route("/time_page", methods=["GET", "POST"])
def time_page():
    """Handle clock in/out for a group."""
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
    return render_template("TimePage.html", username=username,)

@app.route("/group_page", methods=["GET", "POST"])
def group_page():
    """Main group page for note management and time logs."""
    if "username" not in session:
        return redirect(url_for("login"))
    group_name = request.args.get("group_name") or request.form.get("group_name")
    if not group_name:
        return redirect(url_for("user_page"))
    # Load the group from the global GROUPS list
    group = next((g for g in GROUPS if g["name"] == group_name), None)
    if not group:
        return redirect(url_for("user_page"))
    group_members = group["members"]
    all_users = USERS
    group_members_details = [u for u in all_users if u["username"] in group_members]
    group_notes = load_group_notes(group_name)
    time_logs = load_time_logs(group_name)
    time_logs.sort(key=lambda x: datetime.strptime(x["timestamp"], "%I:%M:%S %p %Y-%m-%d"))
    current_status = {}
    for member in group_members_details:
        member_logs = [log for log in time_logs if log["username"] == member["username"]]
        if member_logs:
            current_status[member["username"]] = member_logs[-1]["status"]
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
                return redirect(url_for("group_page", group_name=group_name, selected_note=note_title))
        elif "new_note" in request.form:
            return redirect(url_for("group_page", group_name=group_name))
        elif "member_notes" in request.form:
            return redirect(url_for("all_member_notes", group_name=group_name))
        elif "member_logs" in request.form:
            return redirect(url_for("time_logs", group_name=group_name))
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
                           logs=time_logs,
                           current_status=current_status,
                           editable=editable,
                           )

@app.route("/all_member_notes", methods=["GET", "POST"])
def all_member_notes():
    """Display all group notes with search, sort, and filter options."""
    if "username" not in session:
        return redirect(url_for("login"))
    group_name = request.args.get("group_name", "")
    if not group_name:
        return redirect(url_for("user_page"))
    
    notes = load_group_notes(group_name)
    
    # Check for sort parameter in GET request
    sort_by = request.args.get("sort")
    if sort_by:
        notes = sort_items(notes, sort_by)
    
    if request.method == "POST":
        if "search" in request.form:
            search_query = request.form.get("searchInput", "")
            notes = search_items(notes, search_query, "note_title")
        elif "sort" in request.form:
            sort_by = request.form.get("sort")
            notes = sort_items(notes, sort_by)
        elif "show" in request.form:
            start_date = request.form.get("input1", "")
            end_date = request.form.get("input2", "")
            notes = filter_by_date_range(notes, start_date, end_date)
        elif "download" in request.form:
            return generate_csv(notes, ["Member Name", "Note Title", "Content", "Timestamp"], "member_notes.csv")
        elif "back" in request.form:
            return redirect(url_for("group_page", group_name=group_name))
    
    return render_template("AllMemberNotes.html", notes=notes, group_name=group_name)


@app.route("/time_logs", methods=["GET", "POST"])
def time_logs():
    """Display group time logs with search, sort, and filter options."""
    if "username" not in session:
        return redirect(url_for("login"))
    group_name = request.args.get("group_name", "")
    if not group_name:
        return redirect(url_for("user_page"))
    logs = load_time_logs(group_name)
    
    # Check for sort parameter in GET request
    sort_by = request.args.get("sort")
    if sort_by:
        logs = sort_items(logs, sort_by)
    
    if request.method == "POST":
        if "search" in request.form:
            search_query = request.form.get("searchInput", "")
            logs = search_items(logs, search_query, "username")
        elif "sort" in request.form:
            sort_by = request.form.get("sort")
            logs = sort_items(logs, sort_by)
        elif "show" in request.form:
            start_date = request.form.get("input1", "")
            end_date = request.form.get("input2", "")
            logs = filter_by_date_range(logs, start_date, end_date)
        elif "download" in request.form:
            return generate_csv(logs, ["Member Name", "Status", "Timestamp"], "time_logs.csv")
        elif "back" in request.form:
            return redirect(url_for("group_page", group_name=group_name))
    
    return render_template("TimeLog_Page.html", logs=logs, group_name=group_name)



@socketio.on('join')
def on_join(data):
    username = data['username']
    join_room(username)
    print(f"{username} has joined their room")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
