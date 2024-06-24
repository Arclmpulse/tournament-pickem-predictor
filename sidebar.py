import json
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QMenu, QLineEdit, QApplication, QSizePolicy
from PySide6.QtCore import Qt, QEvent, QSize
from PySide6.QtGui import QPixmap, QIcon

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        
        # Scroll Area Configuration
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Adjust as needed
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # No horizontal scrollbar

        # Styling the Scroll Area and Scrollbar
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;  /* Match background color */
                margin: 0px;
                padding: 0px;
            }
            QScrollArea > QWidget:vertical {
                background-color: transparent;  /* Match background color */
                margin: 0px;
                padding: 0px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: transparent;  /* Match background color */
                width: 4px;  /* Thinner width */
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                min-height: 12px;  /* Adjust the height of the scrollbar handle */
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)

        self.scroll_content = QWidget(self)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.buttons = []

        # Load existing buttons from state, if available
        self.load_buttons()

        # Button to add new buttons
        self.add_new_button = QPushButton("New Event")
        self.layout.addWidget(self.add_new_button)
        self.add_new_button.clicked.connect(self.add_new_button_clicked)

        # Save Button
        self.save_button = QPushButton("Save")
        self.layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_buttons)

        # Variable to store currently active button
        self.current_button = None

        # Set up event filter to detect outside clicks
        self.installEventFilter(self)

        # Dictionary to map sport names to image file paths
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.sport_images = {
            "CS2": os.path.join(self.base_path, "images/cs2.png"),
            "LoL": os.path.join(self.base_path, "images/LoL.png"),
            "Futbol": os.path.join(self.base_path, "images/Futbol.png"),
            "NBA": os.path.join(self.base_path, "images/NBA.png"),
            "MLB": os.path.join(self.base_path, "images/MLB.png")
        }

    def add_button(self, text):
        button = QPushButton(text)
        button.setStyleSheet("text-align: left; padding: 10px; border: none; border-radius: 5px;")  # Rounded corners
        button.setFlat(True)
        self.scroll_layout.addWidget(button)
        self.buttons.append(button)

        # Context menu for right-click actions
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda pos, btn=button: self.open_menu(pos, btn))

        # Connect button clicked signal to handle active state
        button.clicked.connect(lambda checked, btn=button: self.set_active_button(btn))

        self.save_buttons()  # Save buttons after adding

    def open_menu(self, pos, button):
        menu = QMenu()

        try:
            rename_action = menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self.rename_button(button))

            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_button(button))

            select_sport_action = menu.addAction("Select Sport")
            select_sport_action.triggered.connect(lambda: self.open_sport_menu(button, pos))
        except Exception as e:
            print(f"Error creating menu: {e}")

        menu.exec_(button.mapToGlobal(pos))

    def open_sport_menu(self, button, pos):
        sport_menu = QMenu()

        for sport, image_path in self.sport_images.items():
            action = sport_menu.addAction(sport)
            action.triggered.connect(lambda checked, sport=sport: self.set_sport_image(button, sport))

        sport_menu.exec_(self.mapToGlobal(pos))

    def set_sport_image(self, button, sport):
        image_path = self.sport_images.get(sport)
        if not image_path:
            print(f"Image path for {sport} not found.")
            return
        
        pixmap = QPixmap(image_path)
        
        if pixmap.isNull():
            print(f"Failed to load image from {image_path}")
            return

        # Resize pixmap to fit button height while maintaining aspect ratio
        button_height = button.sizeHint().height() - 20  # adjust for padding
        scaled_pixmap = pixmap.scaledToHeight(button_height, Qt.SmoothTransformation)

        # Set the image to the right side of the button
        button.setIcon(QIcon(scaled_pixmap))
        button.setIconSize(QSize(scaled_pixmap.width(), scaled_pixmap.height()))

        # Adjust the button's text alignment and icon position
        button.setStyleSheet("""
            text-align: left; 
            padding: 10px; 
            border: none; 
            border-radius: 5px;
            padding-right: 30px;  /* Space for the icon */
            """)  

    def rename_button(self, button):
        # Clear active button's highlighting
        if self.current_button:
            self.current_button.setStyleSheet("text-align: left; padding: 10px; border: none; border-radius: 5px;")

        old_text = button.text()
        line_edit = QLineEdit(button.parent())
        line_edit.setText(old_text)
        line_edit.selectAll()

        # Set line edit height to match button height
        line_edit_height = button.sizeHint().height()
        line_edit.setFixedHeight(line_edit_height)

        # Function to finish renaming
        def finish_rename():
            new_text = line_edit.text()
            if new_text.strip():  # Check if the new text is not empty
                new_button = QPushButton(new_text)
                new_button.setStyleSheet("text-align: left; padding: 10px; border: none; border-radius: 5px;")  # Rounded corners
                new_button.setFlat(True)

                index = self.scroll_layout.indexOf(line_edit)
                self.scroll_layout.removeWidget(line_edit)
                line_edit.deleteLater()

                self.scroll_layout.insertWidget(index, new_button)
                self.buttons[self.buttons.index(button)] = new_button
                self.save_buttons()  # Save buttons state after renaming

                # Disconnect previous button's signals
                button.clicked.disconnect()
                button.customContextMenuRequested.disconnect()

                # Remove any lingering references
                button.setParent(None)

                # Connect new button's signals
                new_button.clicked.connect(lambda checked, btn=new_button: self.set_active_button(btn))
                new_button.setContextMenuPolicy(Qt.CustomContextMenu)
                new_button.customContextMenuRequested.connect(lambda pos, btn=new_button: self.open_menu(pos, btn))

                # Set the newly renamed button as active
                self.set_active_button(new_button)

                # Clean up the previous button
                button.deleteLater()

        # Function to cancel renaming
        def cancel_rename():
            self.scroll_layout.removeWidget(line_edit)
            line_edit.deleteLater()
            self.scroll_layout.insertWidget(self.scroll_layout.indexOf(button), button)

            # Set the original button as active again
            self.set_active_button(button)

        line_edit.editingFinished.connect(finish_rename)
        line_edit.installEventFilter(self)  # Install event filter to detect outside clicks

        index = self.scroll_layout.indexOf(button)
        self.scroll_layout.removeWidget(button)

        self.scroll_layout.insertWidget(index, line_edit)
        line_edit.setFocus()

    def set_active_button(self, button):
        # Clear active style from previous active button
        if self.current_button:
            try:
                self.current_button.setStyleSheet("text-align: left; padding: 10px; border: none; border-radius: 5px;")
            except RuntimeError:
                self.current_button = None  # Reset if the previous button is deleted

        # Set new active button
        self.current_button = button
        self.current_button.setStyleSheet("background-color: #c0c0c0; text-align: left; padding: 10px; border: none; border-radius: 5px;")

    def delete_button(self, button):
        # Check if the button to be deleted is the current active button
        if self.current_button == button:
            self.current_button = None

        self.scroll_layout.removeWidget(button)
        button.deleteLater()
        self.buttons.remove(button)
        self.save_buttons()

    def add_new_button_clicked(self):
        text = f"New Button {len(self.buttons) + 1}"
        self.add_button(text)
        self.save_buttons()

    def save_buttons(self):
        button_texts = [button.text() for button in self.buttons]
        with open('buttons.json', 'w') as f:
            json.dump(button_texts, f)

    def load_buttons(self):
        try:
            with open('buttons.json', 'r') as f:
                button_texts = json.load(f)
                for text in button_texts:
                    self.add_button(text)
        except FileNotFoundError:
            pass
    
    def clear_buttons(self):
        for button in self.buttons:
            button.deleteLater()
        self.buttons = []

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                if isinstance(self.focusWidget(), QLineEdit):
                    self.cancel_rename()
                    return True  # Event handled

        elif event.type() == QEvent.MouseButtonPress:
            if isinstance(self.focusWidget(), QLineEdit) and not self.focusWidget().underMouse():
                self.cancel_rename()
                return True  # Event handled

        return super().eventFilter(obj, event)

    def cancel_rename(self):
        if self.current_button and isinstance(self.scroll_layout.itemAt(self.scroll_layout.indexOf(self.current_button)), QLineEdit):
            old_text = self.current_button.text()
            line_edit = self.scroll_layout.itemAt(self.scroll_layout.indexOf(self.current_button)).widget()
            line_edit.setText(old_text)
            line_edit.clearFocus()
            self.scroll_layout.removeWidget(line_edit)
            self.scroll_layout.insertWidget(self.scroll_layout.indexOf(self.current_button), self.current_button)
            self.current_button.setStyleSheet("text-align: left; padding: 10px; border: none; border-radius: 5px;")
            self.current_button = None

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    sidebar = Sidebar()
    sidebar.show()
    sys.exit(app.exec())
