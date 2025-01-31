from PyQt5.QtWidgets import QApplication, QListWidget, QWidget, QLabel, QMessageBox, QPushButton, QLineEdit, QTextEdit, QListWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtCore import QPropertyAnimation, QRect, QSequentialAnimationGroup, QEasingCurve, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QInputDialog

from PyQt5 import QtCore
import csv
import sys
import os


class ClearableTextEdit(QTextEdit):
    def __init__(self, placeholder, parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.setPlainText(placeholder)
        self.setStyleSheet("color: gray; background-color: lightgray;")

    def focusInEvent(self, event):
        if self.toPlainText() == self.placeholder:
            self.clear()
            self.setStyleSheet("color: black; background-color: white;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        if not self.toPlainText().strip():
            self.setPlainText(self.placeholder)
            self.setStyleSheet("color: gray; background-color: lightgray;")
        else:
            self.setStyleSheet("color: black; background-color: white;")
        super().focusOutEvent(event)


from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QLabel, QMessageBox
import re

class Create_Account_Page(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Note That')
        
        self.setStyleSheet("background-color: #333;")
        self.setGeometry(1920, 1080, 1920, 1080)

        
        # Text Field for Username
        self.txtf1 = QTextEdit(self)
        self.txtf1.setPlaceholderText('Enter Username')
        self.txtf1.move(850, 450)
        self.txtf1.resize(250, 60)
        self.txtf1.setStyleSheet("background-color: lightgray;")
        font = QFont()
        font.setPointSize(12)
        self.txtf1.setFont(font)

        # Text Field for Email
        self.txtf2 = QTextEdit(self)
        self.txtf2.setPlaceholderText('Enter Email')
        self.txtf2.resize(250, 60)
        self.txtf2.move(850, 550)
        self.txtf2.setStyleSheet("background-color: lightgray;")
        self.txtf2.setFont(font)

        # Text Field for Password
        self.txtf3 = QTextEdit(self)
        self.txtf3.setPlaceholderText('Enter Password')
        self.txtf3.resize(250, 60)
        self.txtf3.move(850, 650)
        self.txtf3.setStyleSheet("background-color: lightgray;")
        self.txtf3.setFont(font)

        # Labels
        
        
        
        self.sdbrlft9 = QWidget(self)
        self.sdbrlft9.move(812, 248)
        self.sdbrlft9.resize(301, 90)
        self.sdbrlft9.setStyleSheet("background-color: khaki;")
        
        self.sdbrlft10 = QWidget(self)
        self.sdbrlft10.move(812, 248)
        self.sdbrlft10.resize(301, 5)
        self.sdbrlft10.setStyleSheet("background-color: white;")
        
        self.sdbrlft11 = QWidget(self)
        self.sdbrlft11.move(812, 260)
        self.sdbrlft11.resize(301, 5)
        self.sdbrlft11.setStyleSheet("background-color: white;")
        
        self.sdbrlft12 = QWidget(self)
        self.sdbrlft12.move(812, 272)
        self.sdbrlft12.resize(301, 5)
        self.sdbrlft12.setStyleSheet("background-color: white;")
        
        self.sdbrlft13 = QWidget(self)
        self.sdbrlft13.move(812, 283)
        self.sdbrlft13.resize(301, 5)
        self.sdbrlft13.setStyleSheet("background-color: white;")
        
        self.sdbrlft14 = QWidget(self)
        self.sdbrlft14.move(812, 294)
        self.sdbrlft14.resize(301, 5)
        self.sdbrlft14.setStyleSheet("background-color: white;")
        
        self.sdbrlft15 = QWidget(self)
        self.sdbrlft15.move(812, 305)
        self.sdbrlft15.resize(301, 5)
        self.sdbrlft15.setStyleSheet("background-color: white;")
        
        self.sdbrlft16 = QWidget(self)
        self.sdbrlft16.move(812, 318)
        self.sdbrlft16.resize(301, 5)
        self.sdbrlft16.setStyleSheet("background-color: white;")
        
        self.sdbrlft16 = QWidget(self)
        self.sdbrlft16.move(812, 331)
        self.sdbrlft16.resize(301, 5)
        self.sdbrlft16.setStyleSheet("background-color: white;")
        
        self.lbl1 = QLabel('/////////', self)
        self.lbl1.move(812, 230)
        self.lbl1.resize(810, 130)
        self.lbl1.setFont(QFont("Arial", 70))
        self.lbl1.setStyleSheet("background-color: transparent; color: khaki; bold;" )
        
        self.crtacnt = QLabel('Create Account', self)
        self.crtacnt.resize(700, 160)
        self.crtacnt.move(700, 315)
        self.crtacnt.setFont(QFont("Calibri", 50))
        self.crtacnt.setStyleSheet("background-color: transparent; color: white; bold;" )
        
        self.ntthtlbl = QLabel('Note That', self)
        self.ntthtlbl.move(820, 250)
        self.ntthtlbl.setFont(QFont("Edwardian Script ITC", 50))
        self.ntthtlbl.setStyleSheet("background-color: transparent; color: blue; bold;" )

        
        
        
        
        
        
        self.usrnmlbl = QLabel('Username', self)
        self.usrnmlbl.move(700, 460)
        self.usrnmlbl.setStyleSheet("color: white;")
        self.usrnmlbl.setFont(QFont("Arial", 14))

        self.emllbl = QLabel('Email', self)
        self.emllbl.move(700, 560)
        self.emllbl.setStyleSheet("color: white;")
        self.emllbl.setFont(QFont("Arial", 14))

        self.passwrdlbl = QLabel('Password', self)
        self.passwrdlbl.move(700, 660)
        self.passwrdlbl.setStyleSheet("color: white;")
        self.passwrdlbl.setFont(QFont("Arial", 14))

        # Create Account Button
        self.crtbtn = QPushButton('Sign Up', self)
        self.crtbtn.resize(200, 50)
        self.crtbtn.move(870, 750)
        self.crtbtn.setStyleSheet("background-color: white;")
        self.crtbtn.clicked.connect(self.create_account)

    def create_account(self):
        username = self.txtf1.toPlainText()  # Capturing the username
        email = self.txtf2.toPlainText()
        password = self.txtf3.toPlainText()

        # Simple email validation using regular expression
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not username:
            self.show_error_message("Username is required.")
        elif not email:
            self.show_error_message("Email is required.")
        elif not re.match(email_pattern, email):
            self.show_error_message("Please enter a valid email address.")
        elif not password:
            self.show_error_message("Password is required.")
        else:
            # Pass the username, email, and password to the login page
            self.login_page = Login_Page(username, email, password)
            self.login_page.show()
            self.close()  # Close the create account page

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Input Error")
        msg.exec_()


class Login_Page(QWidget):
    def __init__(self, username, email, password, parent=None):
        super().__init__(parent)
        self.username = username  # Store the username passed from Create_Account_Page
        self.email = email  # Store the email passed from Create_Account_Page
        self.password = password  # Store the password passed from Create_Account_Page
        self.init_ui()  # Now you can initialize the UI

    def init_ui(self):
        self.setWindowTitle('Login Page')
        self.setStyleSheet("background-color: #333;")
        self.setGeometry(1920, 1080, 1920, 1080)

        # Email Field
        self.txtf4 = ClearableTextEdit('Enter Email', self)
        self.txtf4.move(850, 400)
        self.txtf4.resize(250, 60)
        self.txtf4.setStyleSheet("background-color: lightgray;")
        font = QFont()
        font.setPointSize(12)
        self.txtf4.setFont(font)

        # Password Field
        self.txtf5 = ClearableTextEdit('Enter Password', self)
        self.txtf5.resize(250, 60)
        self.txtf5.move(850, 500)
        self.txtf5.setStyleSheet("background-color: lightgray;")
        self.txtf5.setFont(font)

        # Labels
        self.usrnmlbl = QLabel('Email', self)
        self.usrnmlbl.move(700, 410)
        self.usrnmlbl.setStyleSheet("color: white;")
        self.usrnmlbl.setFont(QFont("Arial", 14))

        self.passlbl = QLabel('Password', self)
        self.passlbl.move(700, 510)
        self.passlbl.setStyleSheet("color: white;")
        self.passlbl.setFont(QFont("Arial", 14))

        # Login Button
        self.lginbtn = QPushButton('Login', self)
        self.lginbtn.move(869, 610)
        self.lginbtn.resize(200, 50)
        self.lginbtn.setStyleSheet("background-color: white;")
        self.lginbtn.clicked.connect(self.log_in)

    def log_in(self):
        email_input = self.txtf4.toPlainText()
        password_input = self.txtf5.toPlainText()

        if not email_input or not password_input:
            print("Please fill in all fields.")
        elif email_input == self.email and password_input == self.password:
            # Pass the username to User_Page
            self.user_page = User_Page(self.username)  # Pass the username
            self.user_page.show()
            self.close()  # Close login page
        else:
            print("Incorrect email or password.")





                
            
class User_Page(QWidget):
    def __init__(self, username, image_path=None):
        super().__init__()
        self.username = username
        self.image_path = image_path  # Store the image path
        self.notes = {}
        self.timestamps = {}
        self.groups = {}
        self.csv_file_path = "notes_data.csv"
        self.init_ui()
        self.update_sidebar()
        self.load_profile_picture() 

    def init_ui(self):
        # Set the window title
        self.setWindowTitle('Note That')
        # Set the background color of the window
        self.setStyleSheet("background-color: #333;")
        self.setGeometry(1920, 1080, 1920, 1080)

        # Sidebar Left Serves as a Border
        

        # Sidebar Left
        self.sdbrlft = QListWidget(self)
        self.sdbrlft.move(0, 2)
        self.sdbrlft.resize(300, 1009)
        self.sdbrlft.setStyleSheet("""
        QListWidget {
            background-color: #333; 
            color: white;
            border: 4px solid black;  /* Ensure no border by default */
            
        
        }
        QListWidget::item {
            background-color: #333;
            color: white;
            border: 2px solid transparent;  /* Ensure no border by default */
            padding: 5px;  /* Add padding for better spacing */
        }
        QListWidget::item:hover {
            background-color: #555;  /* Darker gray on hover */
            color: lightblue;  /* Highlight text color on hover */
            border: 2px solid lightblue;  /* Optional: Add border on hover */
        }
        QListWidget::item:selected {
            background-color: blue;
            color: white;
        }
    """)
        self.sdbrlft.setFont(QFont("Arial", 12))
        self.sdbrlft.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sdbrlft.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Sidebar Right Serves as a Border
        

        self.sdbrcntr = QListWidget(self)
        self.sdbrcntr.move(296, 645)
        self.sdbrcntr.resize(1360, 366)
        self.sdbrcntr.setStyleSheet("""
        QListWidget {
            background-color: #333; 
            color: white;
            border: 4px solid black;  /* Ensure no border by default */
            
            
        
        }
        QListWidget::item {
            background-color: #333;
            color: white;
            border: 2px solid transparent;  /* Ensure no border by default */
            padding: 5px;  /* Add padding for better spacing */
        }
        QListWidget::item:hover {
            background-color: #555;  /* Darker gray on hover */
            color: lightblue;  /* Highlight text color on hover */
            border: 2px solid lightblue;  /* Optional: Add border on hover */
        }
        QListWidget::item:selected {
            background-color: blue;
            color: white;
        }
        QListWidget::verticalScrollBar, QListWidget::horizontalScrollBar {
        width: 0px;
        height: 0px;
    }
        
    """)
        
        self.sdbrcntr.setFont(QFont("Arial", 12))
        self.sdbrcntr.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sdbrcntr.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Sidebar Right
        self.sdbrrgt = QListWidget(self)
        self.sdbrrgt.move(1650, 2)
        self.sdbrrgt.resize(300, 1009)
        self.sdbrrgt.setStyleSheet("""
            QListWidget {
                background-color: #333;
                color: white;
                border: 4px solid black;
            }
            QListWidget::item {
                background-color: #333;
                color: white;
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #555;
                color: lightblue;
            }
            QListWidget::item:selected {
                background-color: blue;
                color: white;
            }
        """)
        self.sdbrrgt.setFont(QFont("Arial", 12))
        self.sdbrrgt.itemClicked.connect(self.open_group_page) 
        self.sdbrrgt.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sdbrrgt.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        
        # Set widget positions manually
        self.crtgp_button = QPushButton('Create Group', self)
        self.crtgp_button.resize(200, 50)
        self.crtgp_button.move(1690, 20)
        self.crtgp_button.setStyleSheet("""
        QPushButton {
                background-khaki: ;
                color: khaki;
                border: 2px solid black;
                border-radius: 10px; /* Rounded corners */
            }
            QPushButton:hover {
                background-color: #d3d3d3; /* Slightly darker gray on hover */
                color: blue; /* Change text color on hover */
                border: 2px solid blue; /* Optional: Highlight border on hover */
            }
            QPushButton:pressed {
                background-color: gray; /* Darker color when pressed */
                color: white;
                border: 2px solid yellow;
            }
            QScrollArea {
                background-color: #333;
            }
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }
            
    """)
        self.crtgp_button.setFont(QFont("Arial", 14))
        self.crtgp_button.setFont(QFont("Arial", 14))
        self.crtgp_button.clicked.connect(self.go_to_create_group_page)  # Connect to go_to_group_page function

    

        

        # Add the username label
        self.username_label = QLabel(self.username, self)
        self.username_label.move(400, 39)
        self.username_label.setStyleSheet("color: white; font-size: 18px;")
        self.username_label.setFont(QFont("Arial", 20))
        
        
        
        # Text Field for Note Name
        self.txtf5 = QLineEdit(self)
        self.txtf5.setPlaceholderText("Note Name")
        self.txtf5.move(350, 126)
        self.txtf5.setStyleSheet("background-color: lightgray;")
        self.txtf5.setFont(QFont("Arial", 12))

        # Text Field for Note Content
        self.txtf6 = QTextEdit(self)
        self.txtf6.setPlaceholderText("Type Here")
        self.txtf6.resize(1200, 390)
        self.txtf6.move(350, 170)
        self.txtf6.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.txtf6.setStyleSheet("background-color: lightgray;")
        self.txtf6.setFont(QFont("Arial", 14))

        
        
        # Save Note Button
        self.svntbtn = QPushButton('Save Note', self)
        self.svntbtn.resize(200, 50)
        self.svntbtn.move(700, 570)
        self.svntbtn.setStyleSheet("""
            QPushButton {
                background-khaki: ;
                color: khaki;
                border: 2px solid black;
                border-radius: 10px; /* Rounded corners */
            }
            QPushButton:hover {
                background-color: #d3d3d3; /* Slightly darker gray on hover */
                color: blue; /* Change text color on hover */
                border: 2px solid blue; /* Optional: Highlight border on hover */
            }
            QPushButton:pressed {
                background-color: gray; /* Darker color when pressed */
                color: white;
                border: 2px solid yellow;
            }
            QListWidget::horizontalScrollBar {
                height: 0px;
                background: transparent;
            }
        """)
        self.svntbtn.setFont(QFont("Arial", 14))

        # New Note Button
        self.nwntbtn = QPushButton('New Note', self)
        self.nwntbtn.resize(200, 50)
        self.nwntbtn.move(1000, 570)
        self.nwntbtn.setStyleSheet("""
            QPushButton {
                background-khaki: ;
                color: khaki;
                border: 2px solid black;
                border-radius: 10px; /* Rounded corners */
            }
            QPushButton:hover {
                background-color: #d3d3d3; /* Slightly darker gray on hover */
                color: blue; /* Change text color on hover */
                border: 2px solid blue; /* Optional: Highlight border on hover */
            }
            QPushButton:pressed {
                background-color: gray; /* Darker color when pressed */
                color: white;
                border: 2px solid yellow;
            }
        """)
        self.nwntbtn.setFont(QFont("Arial", 14))

        self.img = QLabel("+", self)
        self.img.move(300, 1)
        self.img.setFixedSize(100, 100)  # Set a fixed size for the image display area
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet("color: white; font-size: 18px; background-color: transparent; border-radius: 50px;")
        self.img.mousePressEvent = self.change_profile_picture  # Set mouse click event handler
        
        if self.image_path:
            # If an image was previously uploaded, load it
            pixmap = QPixmap(self.image_path)
            self.img.setPixmap(pixmap)    
        
        # Set up the Save Note button
        self.svntbtn.clicked.connect(self.save_note)
        self.nwntbtn.clicked.connect(self.new_note)
        
        # Connect note item clicks to loading
        self.sdbrlft.itemClicked.connect(self.handle_sidebar_click)

    def save_note(self):
        """Save a note and ensure it persists when reopening User_Page."""
        note_name = self.txtf5.text().strip()
        note_content = self.txtf6.toPlainText().strip()

        if note_name and note_content:
            # Save the note to the dictionary
            self.notes[note_name] = note_content
            current_time = QDateTime.currentDateTime().toString("MM/dd/yyyy hh:mm:ss AP")
            self.timestamps[note_name] = current_time

            # Save the new note and timestamp to CSV for persistence
            self.sync_note_to_csv(note_name, current_time)

            # Update the sidebar to reflect the saved note
            self.update_sidebar()

            QMessageBox.information(self, "Success", "Note saved successfully!")  # Notify user of save
        else:
            QMessageBox.warning(self, "Error", "Please enter both note name and content.")

    def sync_note_to_csv(self, note_name, timestamp):
        """Save notes to a CSV file so they persist even after restarting."""
        try:
            with open(self.csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([note_name, self.notes[note_name], timestamp])  # Save name, content, and timestamp
        except Exception as e:
            print(f"Error saving to CSV: {e}")

      # Add the timestamp

    def update_sidebar(self):
        """Ensure saved notes are reloaded when returning to User_Page."""
        self.sdbrlft.clear()  # Clear sidebar before adding items
        self.sdbrcntr.clear()

        # Add spacing to keep UI organized
        spacer = QListWidgetItem("")
        spacer.setSizeHint(QSize(10, 50))
        self.sdbrlft.addItem(spacer)
        self.sdbrcntr.addItem(spacer)

        # Reload saved notes
        for note_name in self.notes:
            note_item = QListWidgetItem(note_name)
            note_item.setFont(QFont("Arial", 12))
            note_item.setForeground(Qt.white)
            note_item.setBackground(Qt.blue)
            self.sdbrlft.addItem(note_item)

            # Add timestamp to sidebar
            timestamp_item = QListWidgetItem(f"{note_name}: {self.timestamps[note_name]}")
            timestamp_item.setFont(QFont("Arial", 12))
            timestamp_item.setForeground(Qt.white)
            timestamp_item.setBackground(Qt.blue)

            # Add space between items
            spacer_item = QListWidgetItem("")
            spacer_item.setSizeHint(QSize(15, 60))
            self.sdbrcntr.addItem(spacer_item)
            self.sdbrcntr.addItem(timestamp_item)

        # Ensure clicking a note loads its content
        self.sdbrcntr.itemClicked.connect(self.highlight_note_in_sidebar)

    def update_sidebar2(self):
        """Ensure saved notes are reloaded when returning to User_Page."""
        self.sdbrlft.clear()  # Clear sidebar before adding items
        self.sdbrcntr.clear()

        # Add spacing to keep UI organized
        spacer = QListWidgetItem("")
        spacer.setSizeHint(QSize(10, 50))
        self.sdbrlft.addItem(spacer)
        self.sdbrcntr.addItem(spacer)

        # Reload saved notes
        for note_name in self.notes:
            note_item = QListWidgetItem(note_name)
            note_item.setFont(QFont("Arial", 12))
            note_item.setForeground(Qt.white)
            note_item.setBackground(Qt.blue)
            self.sdbrlft.addItem(note_item)

            # Add timestamp to sidebar
            timestamp_item = QListWidgetItem(f"{note_name}: {self.timestamps[note_name]}")
            timestamp_item.setFont(QFont("Arial", 12))
            timestamp_item.setForeground(Qt.white)
            timestamp_item.setBackground(Qt.blue)

            # Add space between items
            spacer_item = QListWidgetItem("")
            spacer_item.setSizeHint(QSize(15, 60))
            self.sdbrcntr.addItem(spacer_item)
            self.sdbrcntr.addItem(timestamp_item)

        # Ensure clicking a note loads its content
        self.sdbrcntr.itemClicked.connect(self.highlight_note_in_sidebar)

    def highlight_note_in_sidebar(self, item):
    # Extract note name from the timestamp item
        note_name = item.text().split(":")[0]  # Get the note name before the timestamp
        for i in range(self.sdbrlft.count()):
            list_item = self.sdbrlft.item(i)
            if list_item and list_item.text() == note_name:
                self.sdbrlft.setCurrentItem(list_item)  # Highlight the note in the left sidebar
                break

    def handle_sidebar_click(self, item):
        """Load a note when it is clicked in the sidebar."""
        note_name = item.text()

        if note_name in self.notes:
            self.txtf5.setText(note_name)
            self.txtf6.setPlainText(self.notes[note_name])
        else:
            QMessageBox.warning(self, "Error", "Note not found.")

    def load_note(self, note_name):
        if note_name in self.notes:
            self.txtf5.setText(note_name)
            self.txtf6.setPlainText(self.notes[note_name])
        else:
            QMessageBox.warning(self, "Error", "Note not found.")

    def new_note(self):
        self.txtf5.clear()
        self.txtf6.clear()
        
    def go_to_create_group_page(self):
        """Navigate to Create_Group_Page and pass stored groups, notes, and timestamps."""
        self.create_group_page = Create_Group_Page(
            self.username, 
            self.image_path, 
            groups=self.groups, 
            notes=self.notes,  # Pass saved notes
            timestamps=self.timestamps  # Pass timestamps
        )
        self.create_group_page.show()
        self.close()


    def change_profile_picture(self, event):
        """Slide down the '+' symbol, then replace it with the user's image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile Picture",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.image_path = file_path  # Store the selected image path
            self.load_profile_picture() # If a file was selected
            pixmap = QPixmap(file_path)  # Load the image as a QPixmap
            pixmap = pixmap.scaled(100, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Resize image

            # Step 1: Animate the '+' sliding down
            original_geometry = self.img.geometry()
            slide_down_geometry = original_geometry.adjusted(0, 50, 0, 0)  # Move label down by 50px

            slide_down_animation = QPropertyAnimation(self.img, b"geometry")
            slide_down_animation.setDuration(300)  # Duration for sliding
            slide_down_animation.setStartValue(original_geometry)
            slide_down_animation.setEndValue(slide_down_geometry)
            slide_down_animation.setEasingCurve(QEasingCurve.OutCubic)

            # Step 2: Replace '+' with the image and slide the image back up
            def replace_and_slide_up():
                self.img.setPixmap(pixmap)  # Replace '+' with the image
                self.img.setText("")  # Remove the + text
                slide_up_geometry = original_geometry.adjusted(0, 0, 0, 0) 
                slide_up_animation = QPropertyAnimation(self.img, b"geometry")
                slide_down_animation.setDuration(1000)  # Slower animation (1 second)
                slide_down_animation.setDuration(100)   # Faster animation (0.1 second)
                slide_up_animation.setStartValue(slide_up_geometry)
                slide_up_animation.setEndValue(original_geometry)
                slide_up_animation.setEasingCurve(QEasingCurve.OutCubic)
                slide_up_animation.start()

            # Connect the end of the slide down animation to the start of the replacement
            slide_down_animation.finished.connect(replace_and_slide_up)

            # Start the slide down animation
            slide_down_animation.start()

    def add_group(self, group_name, members):
        """Add a group to the sidebar and store it below the Create Button."""
        
        self.groups[group_name] = members  # Store the group name and members

        # Create a spacer item to push groups below the Create Group button
        if self.sdbrrgt.count() == 0:  # Add spacer only once
            spacer = QListWidgetItem("")
            spacer.setSizeHint(QSize(70, 80))  # Adjust height to push items down
            self.sdbrrgt.addItem(spacer)

        # Create a QListWidgetItem for the group name
        group_item = QListWidgetItem(group_name)
        group_item.setFont(QFont("Arial", 12))

        # Add the group name to the right sidebar
        self.sdbrrgt.addItem(group_item)

        # Ensure clicking on a group opens the respective group page
        self.sdbrrgt.itemClicked.connect(self.open_group_page)

    def open_group_page(self, item):
        """Open Group_Page and pass stored groups."""
        group_name = item.text()

        if group_name in self.groups:
            members = self.groups[group_name]
        else:
            members = []

        # Pass `self.groups` to Group_Page
        self.group_page = Group_Page(self.username, self.image_path, group_name, members, self.groups, self.notes, self.timestamps)
        self.group_page.show()
        self.close()  # Close User_Page


    def load_profile_picture(self):
        """Load the profile picture if the image path is set."""
        if self.image_path:  # If an image path exists
            pixmap = QPixmap(self.image_path)
            pixmap = pixmap.scaled(100, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img.setPixmap(pixmap)
            self.img.setText("")  

class Create_Group_Page(QWidget):
    def __init__(self, username, image_path=None, group_name=None, members=None, groups=None, notes=None, timestamps=None):
        super().__init__()
        self.username = username
        self.image_path = image_path
        self.group_name = group_name if group_name else "Unnamed Group"
        self.members = members if members else []
        self.groups = groups if groups else {}  # Store all groups
        self.notes = notes if notes else {}  # Store notes data
        self.timestamps = timestamps if timestamps else {}  # Store timestamps

        self.users_data = {  # Predefined list of users for searching
            self.username: {'image': self.image_path, 'username': self.username}
        }
        self.init_ui()
        

    def init_ui(self):
        self.setWindowTitle('Note That')
        self.setStyleSheet("background-color: #333;")
        self.setGeometry(1920, 1080, 1920, 1080)

        # List to store references to the QPushButton widgets
        self.img_buttons = []

        # Number of buttons in each row
        num_buttons_per_row = 5
        # Total number of buttons (for three rows)
        num_buttons_total = 11  # Adjusted for three rows
        # Width of each button (based on the font or icon size)
        button_width = 30  # Adjust according to your button size
        button_spacing = 80  # Space between the buttons
        row_spacing = 150  # Space between rows (vertical space)

        # Total width required for buttons per row
        total_width = num_buttons_per_row * button_width + (num_buttons_per_row - 1) * button_spacing

        # Calculate the starting x position to center the buttons horizontally
        start_x = (self.width() - total_width) // 2

        # First row's y position
        row_1_y = 300

        # Second row's y position (add the vertical row spacing)
        row_2_y = row_1_y + row_spacing

        # Third row's y position (add vertical row spacing again)
        row_3_y = row_2_y + row_spacing

        # Position each button
        for i in range(num_buttons_total):
            # Determine row and column positions
            row = i // num_buttons_per_row  # 0 for first row, 1 for second row, 2 for third row
            col = i % num_buttons_per_row   # Column position within the row

            button = QPushButton(self)  # Create a new QPushButton
            button.setStyleSheet("background-color: transparent; border-radius: 50px;")

            # Calculate the x and y position for each button
            x_pos = start_x + (button_width + button_spacing) * col

            # Determine y position based on row
            if row == 0:
                y_pos = row_1_y
            elif row == 1:
                y_pos = row_2_y
            else:
                y_pos = row_3_y

            button.move(x_pos, y_pos)  # Position each button
            button.resize(100, 100)  # Adjust the size of the button

            # Add the profile image and username to the first button (for the current user)
            if i == 0:
                if self.image_path:
                    icon = QIcon(self.image_path)
                    button.setIcon(icon)  # Set the user's image as the button icon
                    button.setIconSize(QSize(100, 100))  # Resize icon to fit button
                else:
                    button.setText("+")  # Show '+' if no image is provided
                    button.setStyleSheet("color: white; font-size: 18px; background-color: transparent; border-radius: 50px;")

                # Add the username below the image
                username_label = QLabel(self.username, self)
                username_label.setStyleSheet("color: white; font-size: 14px;")
                username_label.move(x_pos + 25, y_pos + 110)  # Position the username label below the image
                username_label.show()

            else:
                button.setText("+")  # Default '+' for other buttons
                button.setStyleSheet("color: white; font-size: 18px; background-color: transparent; border-radius: 50px;")

            button.clicked.connect(lambda checked, i=i: self.handle_button_click(i))  # Connect each button to a handler
            button.show()  # Make sure to show the button
            self.img_buttons.append(button)  # Store the button in the list

        # Searchable text field
        self.txtf8 = QLineEdit('Search', self)
        self.txtf8.move(1040, 230)
        self.txtf8.setStyleSheet("background-color: lightgray;")
        self.txtf8.setFont(QFont("Arial", 12))
        self.txtf8.textChanged.connect(self.perform_search)
        
        self.txtf9 = QLineEdit('Enter Group Name', self)
        self.txtf9.move(759, 230)
        self.txtf9.setStyleSheet("background-color: lightgray;")
        self.txtf9.setFont(QFont("Arial", 12))
        self.txtf9.textChanged.connect(self.perform_search)

        # Add button to allow users to add their own profile
        
        self.svntbtn2 = QPushButton('Create Group', self)
        self.svntbtn2.resize(200, 50)
        self.svntbtn2.move(890, 770)
        self.svntbtn2.setStyleSheet("""
            QPushButton {
                background-khaki: ;
                color: khaki;
                border: 2px solid black;
                border-radius: 10px; /* Rounded corners */
            }
            QPushButton:hover {
                background-color: #d3d3d3; /* Slightly darker gray on hover */
                color: blue; /* Change text color on hover */
                border: 2px solid blue; /* Optional: Highlight border on hover */
            }
            QPushButton:pressed {
                background-color: gray; /* Darker color when pressed */
                color: white;
                border: 2px solid yellow;
            }
            QListWidget::horizontalScrollBar {
                height: 0px;
                background: transparent;
            }
        """)
        self.svntbtn2.setFont(QFont("Arial", 14))
        self.svntbtn2.clicked.connect(self.create_group) 

        # Back button
        self.bckbtn = QPushButton('<', self)
        self.bckbtn.resize(50, 50)
        self.bckbtn.move(5, 6)
        self.bckbtn.clicked.connect(self.back_User_Page2)
        self.bckbtn.setStyleSheet("background-color: lightgray;")
        self.bckbtn.setFont(QFont("Arial", 14))

    def back_User_Page2(self):
        """Return to User_Page while keeping saved notes and groups intact."""
        self.user_page = User_Page(self.username, self.image_path)

        # Restore saved groups
        for group_name, members in self.groups.items():
            self.user_page.add_group(group_name, members)

        # Restore saved notes and timestamps
        for note_name, note_content in self.notes.items():
            self.user_page.notes[note_name] = note_content  
            self.user_page.timestamps[note_name] = self.timestamps[note_name]

        self.user_page.update_sidebar2()  # Ensure timestamps are displayed
        
        self.user_page.show()
        self.close()



    def handle_button_click(self, button_index):
        """
        Handle the logic when a '+' button is clicked.
        Search for the user based on the text input, update the button with user profile or image.
        If the username already exists, allow re-addition (update).
        Also, animate the username label to slide down.
        """
        if button_index < len(self.img_buttons):
            button = self.img_buttons[button_index]  # Get the clicked button

            # Perform the search based on the input
            search_text = self.txtf8.text().lower()  # Get the search query and convert to lowercase

            if search_text in self.users_data:
                # If the user is found, update the button with the user's profile
                user_data = self.users_data[search_text]  # Fetch user data

                if user_data['image']:
                    # If the user has an image, display it on the button
                    icon = QIcon(user_data['image'])
                    button.setIcon(icon)
                    button.setIconSize(QSize(100, 100))  # Set icon size to match the button size
                    button.setText("")  # Clear the "+" text since the image is now displayed
                else:
                    # If no image, display just the username on the button
                    button.setText(user_data['username'])
                    button.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")

                # Add the username label below the button
                username_label = QLabel(user_data['username'], self)
                username_label.setStyleSheet("color: white; font-size: 14px;")
                username_label.setAlignment(Qt.AlignCenter)

                # Position the username label below the button
                x_pos, y_pos = button.x(), button.y() + button.height() + 10
                username_label.move(x_pos, y_pos)
                username_label.resize(button.width(), 20)
                username_label.show()  # Ensure the label is shown

                # Slide down animation
                animation = QPropertyAnimation(username_label, b"pos")
                animation.setDuration(500)  # Set the duration for the slide-down animation
                animation.setStartValue(QPoint(x_pos, y_pos - 30))  # Start just above the button
                animation.setEndValue(QPoint(x_pos, y_pos))  # End at the desired position
                animation.setEasingCurve(QEasingCurve.OutBounce)  # Apply easing curve for a smooth effect
                animation.start()

                print(f"Button {button_index + 1} updated with user {search_text}")
            else:
                # If no user is found, show a warning
                QMessageBox.warning(self, "User Not Found", f"No user found for '{search_text}'.")
        else:
            print(f"Button {button_index + 1} not available")


    def perform_search(self):
        search_text = self.txtf8.text().lower()
        if search_text in self.users_data:
            self.search_result = search_text  # Store the result if found
            print(f"Search matches the user: {self.search_result}")
        else:
            self.search_result = None  # Clear the search result if not found
            print(f"No matching user for: {search_text}")

    def create_group(self):
        """Create a new group and return to User_Page with updated groups."""
        group_name = self.txtf9.text().strip()  # Get the group name from the input

        if not group_name:
            QMessageBox.warning(self, "Error", "Please enter a group name.")
            return

        # Get selected members (modify logic based on actual UI selection)
        members = list(self.users_data.keys())

        if not members:
            QMessageBox.warning(self, "Error", "Please add at least one member to the group.")
            return

        # Store the new group
        self.groups[group_name] = members  

        print(f"Group '{group_name}' created with members: {', '.join(members)}")
        self.user_page = User_Page(self.username, self.image_path)

        # Restore saved groups
        for group_name, members in self.groups.items():
            self.user_page.add_group(group_name, members)

        # Restore saved notes
        for note_name, note_content in self.notes.items():
            self.user_page.notes[note_name] = note_content  # Reload notes
            self.user_page.timestamps[note_name] = self.timestamps[note_name]  # Reload timestamps

        self.user_page.update_sidebar2()  # Refresh UI with stored notes
        
        self.user_page.show()
        self.close()


    



class Group_Page(QWidget):
    def __init__(self, username, image_path=None, group_name=None, members=None, groups=None, notes=None, timestamps=None):
        super().__init__()
        self.username = username
        self.image_path = image_path
        self.group_name = group_name if group_name else "Unnamed Group"
        self.members = members if members else []
        self.groups = groups if groups else {}  # Store all groups
        self.notes = notes if notes else {}  # Store notes data
        self.timestamps = timestamps if timestamps else {}  # Store timestamps
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Note That')
        self.setStyleSheet("background-color: #333;")
        self.setGeometry(1920, 1080, 1920, 1080)

        # Sidebar Left Serves as a Border
        self.sdbrlft3 = QWidget(self)
        self.sdbrlft3.move(5, 0)
        self.sdbrlft3.resize(300, 1080)
        self.sdbrlft3.setStyleSheet("background-color: black;")

        # Sidebar Left
        self.sdbrlft4 = QWidget(self)
        self.sdbrlft4.move(0, 6)
        self.sdbrlft4.resize(300, 1003)
        self.sdbrlft4.setStyleSheet("background-color: #333;")

        # Sidebar Right Serves as a Border
        self.sdbrrgt5 = QWidget(self)
        self.sdbrrgt5.move(1645, 0)
        self.sdbrrgt5.resize(300, 1080)
        self.sdbrrgt5.setStyleSheet("background-color: black;")

        # Sidebar Right
        self.sdbrrgt6 = QWidget(self)
        self.sdbrrgt6.move(1650, 6)
        self.sdbrrgt6.resize(300, 1003)
        self.sdbrrgt6.setStyleSheet("background-color: #333;")

        
        

        # Text Field for Group Name
        self.txtf6 = QLineEdit(self.group_name, self)  # Use group_name if provided
        self.txtf6.move(350, 100)
        self.txtf6.setStyleSheet("background-color: lightgray;")
        self.txtf6.setFont(QFont("Arial", 12))

        # Text Field for Group Content
        self.txtf7 = QTextEdit('Group Details', self)
        self.txtf7.resize(1200, 390)
        self.txtf7.move(350, 140)
        self.txtf7.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.txtf7.setStyleSheet("background-color: lightgray;")
        self.txtf7.setFont(QFont("Arial", 14))

        # Save Group Button
        self.svntbtn = QPushButton('Save Group', self)
        self.svntbtn.resize(200, 50)
        self.svntbtn.move(700, 540)
        self.svntbtn.setStyleSheet("background-color: lightgray;")
        self.svntbtn.setFont(QFont("Arial", 14))

        # New Group Button
        self.nwntbtn = QPushButton('New Group', self)
        self.nwntbtn.resize(200, 50)
        self.nwntbtn.move(1000, 540)
        self.nwntbtn.setStyleSheet("background-color: lightgray;")
        self.nwntbtn.setFont(QFont("Arial", 14))

        # Back Button to User Page
        self.bckbtn2 = QPushButton('<', self)
        self.bckbtn2.resize(50, 50)
        self.bckbtn2.move(5, 6)
        self.bckbtn2.clicked.connect(self.back_User_Page)
        self.bckbtn2.setStyleSheet("background-color: lightgray;")
        self.bckbtn2.setFont(QFont("Arial", 14))

        # Display group name and members
        group_label = QLabel(f"Group Name: {self.group_name}", self)
        group_label.move(400, 50)
        group_label.setStyleSheet("color: white; font-size: 20px;")
        members_label = QLabel(f"Members: {', '.join(self.members)}", self)  # Safe to join since members is a list
        members_label.move(700, 50)
        members_label.setStyleSheet("color: white; font-size: 20px;")

    def save_group_content(self):
        """Save whatever content is added in the group."""
        group_text = self.txtf7.toPlainText()
        self.messages[self.group_name] = group_text  # Store messages for this group
        QMessageBox.information(self, "Saved", "Group content saved successfully!")

    def load_group_content(self):
        """Load existing content for the group if available."""
        if self.group_name in self.messages:
            self.txtf7.setPlainText(self.messages[self.group_name])  # Load messages

    def back_User_Page(self):
        """Return to User_Page while keeping saved notes and groups intact."""
        self.user_page = User_Page(self.username, self.image_path)

        # Restore saved groups
        for group_name, members in self.groups.items():
            self.user_page.add_group(group_name, members)

        # Restore saved notes
        for note_name, note_content in self.notes.items():
            self.user_page.notes[note_name] = note_content  # Reload notes
            self.user_page.timestamps[note_name] = self.timestamps[note_name]  # Reload timestamps

        self.user_page.update_sidebar()  # Refresh UI with stored notes
        self.user_page.show()
        self.close()  # Close Group_Page









#if __name__ == "__main__":
 #   app = QApplication(sys.argv)
    
    # Replace 'test_user' with the actual username you want to test
  #  grppg = Group_Page('test_user')  # Pass the username here
   # grppg.show()

    #app.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    create_account = Create_Account_Page()
    create_account.show()
    app.exec()