import sys, re, json, pyperclip, os
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QSizePolicy, QTabWidget, QFileDialog, QTableWidget, QTableWidgetItem, QRadioButton
from chompjs import parse_js_object

network_files: dict = {}
st_mode: bool = False

class MethodTabs(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Name', 'BG-Color', 'FG-Color', 'Operator'])

        self.layout.addWidget(self.table)

        self.update_table()

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update_table(self):
        self.table.setRowCount(len(network_files['methodMetadata']))
        for row, name in enumerate(network_files['methodMetadata']):
            name_cell = QTableWidgetItem(name)
            bg_cell = QTableWidgetItem(network_files['methodMetadata'][name]['color'][0])
            fg_cell = QTableWidgetItem(network_files['methodMetadata'][name]['color'][1])
            operator_cell = QTableWidgetItem(network_files['methodMetadata'][name]['operator'])

            self.table.setItem(row, 0, name_cell)
            self.table.setItem(row, 1, bg_cell)
            self.table.setItem(row, 2, fg_cell)
            self.table.setItem(row, 3, operator_cell)
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()


def get_traveltimes(stations: list[str], st_string: dict) -> int:
    stations.sort()
    for time in st_string['traveltimes']:
        if time['start'] == stations[0] and time['end'] == stations[1]:
            return time['time']
    return 0


def get_nextstation(line: str, cstation: str, st_string: dict) -> str:
    for lines in st_string['lines']:
        if lines['name'] == line:
            if not lines['stations'].index(cstation) + 1 == len(lines['stations']):
                return lines['stations'][lines['stations'].index(cstation) + 1]


def convert_st_uvdot(st_string: dict) -> tuple:
    print('[D> Converting ST Network...')
    places = {}
    methodMetadata = {}
    routes = {}

    for station in st_string['stations']:
        places[station['name']] = 'CHANGE-ME'
        routes[station['name']] = [['CHANGE-ME', 'CHANGE-ME'], {'railways': {}}]
        for line in station['lines']:
            next_station = get_nextstation(line['name'], station['name'], st_string)
            if next_station:
                stations = [station['name'], next_station]
                routes[station['name']][1]['railways'][next_station] = [
                    [line['name'].replace('USTe', 'UltraStar express').replace('UST', 'UltraStar')],
                    get_traveltimes(stations, st_string) * 8,
                    {'currency': 'Emerald', 'price': 4, 'pass': 'SeaCard', 'passPrice': 2}]

    for line in st_string['lines']:
        if line['name'].startswith('USTe'):
            methodMetadata[line['name']] = {'color': ['#066b5f', 'white']}
        else:
            methodMetadata[line['name']] = {'color': ['#6b006b', 'white']}
        methodMetadata[line['name']]['operator'] = 'Seacrestica Transports Outpost'

    return places, methodMetadata, routes


class Application(QMainWindow):

    def process_input(self, inputstr: str) -> None:
        global network_files
        global st_mode
        network_files = {}
        pattern = re.compile(r'^(?:const|let|var) (network|places|methodMetadata|routes) = ({(?:[^;]|\n)*});$', re.MULTILINE)

        matches = re.finditer(pattern, inputstr)
        for match in matches:
            if match.groups()[0] == 'network':
                print('[D> ST Network detected')
                network_files['places'], network_files['methodMetadata'], network_files['routes'] = convert_st_uvdot(parse_js_object(match.groups()[1]))
                st_mode = True
            else:
                print(f'[D> UVDOT Network variable detected ({match.groups()[0]})')
                st_mode = False
                network_files[match.groups()[0]] = parse_js_object(match.groups()[1])


    def __init__(self):
        super().__init__()

        self.setWindowTitle('UVDOT Editor')
        self.create_import_page()
        self.showMaximized()

    def create_export(self) -> str:
        export = ''

        for file in network_files:
            export += f'const {file} = {json.dumps(network_files[file])};\n\n'
        export.removesuffix('\n')
        return export

    def create_st_export(self) -> str:
        export = ''

        # We need the platform. The platform is not being converted. So please store it somewhere else if st_mode is enabled.
        return export

    def create_import_page(self):
        def input_js(text: str):
            global network_files
            self.process_input(text)
            if ('routes' and 'methodMetadata' and 'places') in network_files:
                self.create_main_page()
            else:
                subtitle.setText('Failed to import either as ST or UVDOT file! Please check the file and try again!')

        def process_input():
            input_js(editbox.toPlainText())
        def open_file():
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open network.js or data.js', os.path.expanduser('~'), 'network.js or data.js (*.js)')
            if file_name:
                with open(file_name, 'r') as f:
                    input_js(f.read())

        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel('Welcome to UVDOT Editor!')
        title.setFont(QFont(title.font().family(), 14))
        subtitle = QLabel('Please import a ST network.js or a UVDOT data.js file.')
        editbox = QTextEdit()
        editbox.setPlaceholderText("Enter your file's content here")
        editbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        editbox.setFont(QFont('monospace', 10))
        submit_button = QPushButton('&Import')
        open_file_button = QPushButton('&Open file')

        submit_button.clicked.connect(process_input)
        open_file_button.clicked.connect(open_file)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(editbox)
        layout.addWidget(submit_button)
        layout.addWidget(open_file_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_export_page(self):
        def prepare_export():
            copy_button.clicked.disconnect()
            if st_export.isChecked():
                export = self.create_st_export()
            else:
                export = self.create_export()
            export_area.setPlainText(export)
            copy_button.clicked.connect(lambda: pyperclip.copy(export))

        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        back_button = QPushButton('&Back')
        back_button.clicked.connect(self.create_main_page)
        back_button.setFixedWidth(50)
        title = QLabel('Export network')
        title.setFont(QFont(title.font().family(), 14))

        export_area = QTextEdit()
        export_area.setFont(QFont('monospace', 10))
        export_area.setReadOnly(True)
        export_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        export_layout = QHBoxLayout()
        st_export = QRadioButton('&ST-Mode')
        uvdot_export = QRadioButton('&UVDOT-Mode')

        copy_button = QPushButton('&Copy to clipboard')

        uvdot_export.setDisabled(st_mode)
        uvdot_export.setChecked(not st_mode)
        st_export.setChecked(st_mode)

        uvdot_export.toggled.connect(prepare_export)
        prepare_export()

        title_layout.addWidget(back_button)
        title_layout.addWidget(title)
        export_layout.addWidget(st_export)
        export_layout.addWidget(uvdot_export)
        export_layout.addStretch()
        layout.addLayout(title_layout)
        layout.addWidget(export_area)
        layout.addLayout(export_layout)
        layout.addWidget(copy_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_main_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title = QLabel()
        title.setFont(QFont(title.font().family(), 14))
        if st_mode:
            title.setText('Seacrestica Transport Network')
        else:
            title.setText('UltraVanilla Department of Transportation Network')

        export_button = QPushButton('&Export')
        export_button.setFixedWidth(50)
        import_button = QPushButton('&Import')
        import_button.setFixedWidth(50)
        # Do different options with tabs
        tab_bar = QTabWidget()
        tab_bar.addTab(MethodTabs(), "Methods")

        title_layout.addWidget(export_button)
        title_layout.addWidget(import_button)
        title_layout.addWidget(title)

        layout.addLayout(title_layout)
        layout.addWidget(tab_bar)

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
