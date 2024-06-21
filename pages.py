from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit

class Page(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit(text)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

    def get_content(self):
        return self.text_edit.toPlainText()

    def set_content(self, content):
        self.text_edit.setText(content)

class Page1(Page):
    def __init__(self, parent=None):
        super().__init__("This is Page 1", parent)

class Page2(Page):
    def __init__(self, parent=None):
        super().__init__("This is Page 2", parent)
