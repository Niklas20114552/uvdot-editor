import sys, re
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from chompjs import parse_js_object

class Application(QMainWindow):
    def process_input(self, input: str) -> None:
        filter = re.compile(r'^(?:const|let|var) (network|places|methodMetadata|routes) = ({(?:[^;]|\n)*});$', re.MULTILINE)

        matches = re.finditer(filter, input)
        for match in matches:
            self.network_files[match.groups()[0]] = parse_js_object(match.groups()[1])

    def __init__(self):
        super().__init__()
        self.setWindowTitle('UVDOT Editor')
        self.create_import_page()
        self.showMaximized()
        self.network_files: dict = {}
        self.st_mode: bool = False

    def create_import_page(self):
        def process_input():
            self.network_files = {}
            self.process_input(editbox.toPlainText())
            if 'network' in self.network_files:
                self.st_mode = True
            elif ('routes' and 'methodMetadata' and 'places') in self.network_files:
                self.st_mode = False
            else:
                subtitle.setText('Failed to import either as ST or UVDOT file! Please check the file and try again!')

        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel('Welcome to UVDOT Editor!')
        title.setFont(QFont(title.font().family(), 14))
        subtitle = QLabel('Please import a ST network.js or a UVDOT data.js file.')
        editbox = QTextEdit()
        editbox.setPlaceholderText("Enter your file's content here")
        submit_button = QPushButton('Import')

        submit_button.clicked.connect(process_input)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(editbox)
        layout.addWidget(submit_button)
        layout.addStretch()

        widget.setLayout(layout)
        self.setCentralWidget(widget)


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName('uvdot-edit')

    browser = Application()
    browser.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
