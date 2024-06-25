import json
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QStackedWidget, QSplitter, QSizePolicy, QApplication
from PySide6.QtCore import Qt, QSize

from sidebar import Sidebar
from pages import Page1, Page2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tournament Pickems")
        self.setMinimumSize(QSize(640, 480))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Create a QSplitter to manage the sidebar and main content
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # Sidebar setup
        self.sidebar = Sidebar()
        self.sidebar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)  # Set policy for expanding and shrinking

        # Initial widths based on percentage of window width
        self.update_sidebar_widths()

        self.splitter.addWidget(self.sidebar)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        self.splitter.addWidget(self.stack)

        # Pages setup
        self.page1 = Page1()
        self.page2 = Page2()
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        # Ensure default buttons are added if no state is loaded
        if not self.sidebar.buttons:
            self.sidebar.add_button("Page 1")
            self.sidebar.add_button("Page 2")

        # Connect the signals after buttons are guaranteed to be present
        self.connect_buttons()

        # Load the saved state
        self.load_state()

        # Connect sidebar's save button to save state
        self.sidebar.save_button.clicked.connect(self.save_state)

    def update_sidebar_widths(self):
        # Calculate min and max widths based on current window size
        window_width = self.width()
        min_width = window_width * 0.2  # Minimum width set to 20% of window width
        max_width = window_width * 0.25  # Maximum width set to 25% of window width

        # Set sidebar widths
        self.sidebar.setMinimumWidth(min_width)
        self.sidebar.setMaximumWidth(max_width)

    def connect_buttons(self):
        if len(self.sidebar.buttons) >= 2:
            self.sidebar.buttons[0].clicked.connect(lambda: self.stack.setCurrentWidget(self.page1))
            self.sidebar.buttons[1].clicked.connect(lambda: self.stack.setCurrentWidget(self.page2))

    def save_state(self):
        state = {
            'buttons': [button.text() for button in self.sidebar.buttons],
            'page1': self.page1.get_content(),
            'page2': self.page2.get_content(),
        }
        with open('state.json', 'w') as f:
            json.dump(state, f)

    def load_state(self):
        try:
            with open('state.json', 'r') as f:
                state = json.load(f)
                # Clear existing buttons first
                self.sidebar.clear_buttons()
                # Add buttons from the loaded state
                for text in state['buttons']:
                    self.sidebar.add_button(text)
                self.page1.set_content(state['page1'])
                self.page2.set_content(state['page2'])
                self.connect_buttons()
        except FileNotFoundError:
            pass

    def resizeEvent(self, event):
        self.update_sidebar_widths()
        event.accept()

    def closeEvent(self, event):
        self.save_state()  # Save state when window is closing
        event.accept()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
