import sys, re, json, pyperclip
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QSizePolicy
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

    def create_export(self) -> str:
        export = ''

        for file in self.network_files:
            export += f'const {file} = {json.dumps(self.network_files[file])};\n\n'
        export.removesuffix('\n')
        return export

    def create_import_page(self):
        def process_input():
            try:
                self.network_files = {}
                self.process_input(editbox.toPlainText())
                if 'network' in self.network_files:
                    self.st_mode = True
                    self.create_main_page()
                elif ('routes' and 'methodMetadata' and 'places') in self.network_files:
                    self.st_mode = False
                    self.create_main_page()
                else:
                    subtitle.setText('Failed to import either as ST or UVDOT file! Please check the file and try again!')
            except Exception as e:
                subtitle.setText('Exception occurred while trying to import: ' + e.__class__.__name__)

        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel('Welcome to UVDOT Editor!')
        title.setFont(QFont(title.font().family(), 14))
        subtitle = QLabel('Please import a ST network.js or a UVDOT data.js file.')
        editbox = QTextEdit()
        editbox.setPlaceholderText("Enter your file's content here")
        editbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        submit_button = QPushButton('&Import')

        submit_button.clicked.connect(process_input)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(editbox)
        layout.addWidget(submit_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_export_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        back_button = QPushButton('&Back')
        back_button.clicked.connect(self.create_main_page)
        back_button.setFixedWidth(50)
        title = QLabel('Export network')
        title.setFont(QFont(title.font().family(), 14))

        export = self.create_export()
        export_area = QTextEdit()
        export_area.setReadOnly(True)
        export_area.setPlainText(export)
        export_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        copy_button = QPushButton('&Copy to clipboard')
        copy_button.clicked.connect(lambda: pyperclip.copy(export))

        title_layout.addWidget(back_button)
        title_layout.addWidget(title)
        layout.addLayout(title_layout)
        layout.addWidget(export_area)
        layout.addWidget(copy_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_main_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title = QLabel()
        title.setFont(QFont(title.font().family(), 14))
        if self.st_mode:
            title.setText('Seacrestica Transport Network')
        else:
            title.setText('UltraVanilla Department of Transportation Network')

        export_button = QPushButton('&Export')
        export_button.setFixedWidth(50)
        import_button = QPushButton('&Import')
        import_button.setFixedWidth(50)
        # Do different options with tabs

        title_layout.addWidget(export_button)
        title_layout.addWidget(import_button)
        title_layout.addWidget(title)

        layout.addLayout(title_layout)
        layout.addStretch()

        import_button.clicked.connect(self.create_import_page)
        export_button.clicked.connect(self.create_export_page)

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
