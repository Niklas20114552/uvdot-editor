import json
import os
import re
import sys

import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from chompjs import parse_js_object

network_files: dict = {}
st_mode: bool = False


def replace_dict_entry_at_index(d: dict, index: int, new_key: str, new_value: str) -> dict:
    items = list(d.items())
    items[index] = (new_key, new_value)
    return dict(items)

class PlacesTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

class NodesTab(QWidget):
    def __init__(self) -> None:
        super().__init__()      
        
class MethodsTab(QWidget):
    def __init__(self):
        def update_bg():
            if self.add_name.text().startswith('USTe '):
                self.add_button.setDisabled(False)
                self.add_bg.setText('#066b5f')
            elif self.add_name.text().startswith('UST '):
                self.add_button.setDisabled(False)
                self.add_bg.setText('#6b006b')
            else:
                self.add_button.setDisabled(True)
                self.add_bg.setText('')

        def check_button():
            self.add_button.setDisabled(
                not (self.add_name.text() and self.add_bg.text() and self.add_fg.text() and self.add_op.text()))

        super().__init__()
        self.dont_update = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Name', 'BG-Color', 'FG-Color', 'Operator', 'Transfer?'])
        self.table.itemChanged.connect(self.process_update)

        self.layout.addWidget(self.table)

        self.update_table()

        self.add_box = QGroupBox('Add method')
        self.add_layout = QHBoxLayout()
        self.add_box.setLayout(self.add_layout)

        self.add_name = QLineEdit()
        self.add_bg = QLineEdit()
        self.add_fg = QLineEdit()
        self.add_op = QLineEdit()
        self.add_button = QPushButton('Add method')
        self.add_button.setFixedWidth(100)

        self.add_name.setPlaceholderText('Method name')
        self.add_bg.setPlaceholderText('Background color')
        self.add_fg.setPlaceholderText('Foreground color')
        self.add_op.setPlaceholderText('Operator')
        if st_mode:
            self.add_name.textChanged.connect(update_bg)
            self.add_bg.setDisabled(True)
            self.add_fg.setDisabled(True)
            self.add_op.setDisabled(True)
            self.add_button.setDisabled(True)
            self.add_fg.setText('white')
            self.add_op.setText('Seacrestica Transports Outpost')
        else:
            self.add_name.textChanged.connect(check_button)
            self.add_bg.textChanged.connect(check_button)
            self.add_fg.textChanged.connect(check_button)
            self.add_op.textChanged.connect(check_button)

        self.add_button.clicked.connect(self.add_method)

        self.add_layout.addWidget(self.add_name)
        self.add_layout.addWidget(self.add_bg)
        self.add_layout.addWidget(self.add_fg)
        self.add_layout.addWidget(self.add_op)
        self.add_layout.addWidget(self.add_button)

        self.layout.addWidget(self.add_box)
        check_button()

    def add_method(self):
        network_files['methodMetadata'][self.add_name.text()] = {'color': [self.add_bg.text(), self.add_fg.text()],
                                                                 'operator': self.add_op.text()}
        self.update_table()

    def process_update(self, item: QTableWidgetItem):
        if self.dont_update:
            return
        index = self.table.item(item.row(), 0).text()
        if item.column() == 0:
            dict_index = item.row()
            old_name = tuple(network_files['methodMetadata'].keys())[dict_index]
            if st_mode:
                if item.text().startswith('USTe '):
                    network_files['methodMetadata'][old_name]['color'][0] = '#066b5f'
                    network_files['methodMetadata'] = replace_dict_entry_at_index(network_files['methodMetadata'],
                                                                                  dict_index,
                                                                                  item.text(),
                                                                                  network_files['methodMetadata'][
                                                                                      old_name])
                elif item.text().startswith('UST '):
                    network_files['methodMetadata'][old_name]['color'][0] = '#6b006b'
                    network_files['methodMetadata'] = replace_dict_entry_at_index(network_files['methodMetadata'],
                                                                                  dict_index,
                                                                                  item.text(),
                                                                                  network_files['methodMetadata'][
                                                                                      old_name])
                elif item.text().strip() == '':
                    network_files['methodMetadata'].pop(tuple(network_files['methodMetadata'].keys())[dict_index])
                else:
                    item.setText(old_name)
            else:
                if item.text().strip() == '':
                    network_files['methodMetadata'].pop(tuple(network_files['methodMetadata'].keys())[dict_index])
                else:
                    network_files['methodMetadata'] = replace_dict_entry_at_index(network_files['methodMetadata'],
                                                                                  dict_index,
                                                                                  item.text(),
                                                                                  network_files['methodMetadata'][
                                                                                      old_name])
        elif item.column() == 1:
            if item.text().strip() == '':
                item.setText(network_files['methodMetadata'][index]['color'][0])
            else:
                network_files['methodMetadata'][index]['color'][0] = item.text()

        elif item.column() == 2:
            if item.text().strip() == '':
                item.setText(network_files['methodMetadata'][index]['color'][1])
            else:
                network_files['methodMetadata'][index]['color'][1] = item.text()
        elif item.column() == 3:
            if item.text().strip() == '':
                item.setText(network_files['methodMetadata'][index]['operator'])
            else:
                network_files['methodMetadata'][index]['operator'] = item.text()
        self.update_table()

    def update_table(self):
        try:
            self.dont_update = True

            self.table.setRowCount(len(network_files['methodMetadata']))
            for row, name in enumerate(network_files['methodMetadata']):
                name_cell = QTableWidgetItem(name)
                bg_cell = QTableWidgetItem(network_files['methodMetadata'][name]['color'][0])
                fg_cell = QTableWidgetItem(network_files['methodMetadata'][name]['color'][1])
                operator_cell = QTableWidgetItem(network_files['methodMetadata'][name]['operator'])
                #transfer_checkbox = QCheckBox()
                #transfer_checkbox.setChecked(name in network_files['transfers'])
                #transfer_cell = QTableWidgetItem(transfer_checkbox)
                if st_mode:
                    bg_cell.setFlags(bg_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    fg_cell.setFlags(fg_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    operator_cell.setFlags(operator_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)

                self.table.setItem(row, 0, name_cell)
                self.table.setItem(row, 1, bg_cell)
                self.table.setItem(row, 2, fg_cell)
                self.table.setItem(row, 3, operator_cell)
                #self.table.setItem(row, 4, transfer_cell)
                self.table.resizeColumnsToContents()
                self.table.resizeRowsToContents()
        except Exception as e:
            network_files['places'] = {}
            network_files['transfers'] = {}
            network_files['methodMetadata'] = {}
            network_files['routes'] = {}
            
            print(f"[D> An error occurred during table update: {e}")
        finally:
            self.dont_update = False


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


class CloseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.cancelled = False
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Quit?")

        self.layout.addWidget(QLabel('Do you want to export the network before closing?'))
        self.yes = QPushButton('&Yes')
        self.no = QPushButton('&No')
        self.cancel = QPushButton('&Cancel')

        self.yes.clicked.connect(self.accept)
        self.no.clicked.connect(self.reject)
        self.cancel.clicked.connect(self.do_cancel)

        self.button_layout.addWidget(self.yes)
        self.button_layout.addWidget(self.no)
        self.button_layout.addWidget(self.cancel)
        self.layout.addLayout(self.button_layout)

    def do_cancel(self):
        self.cancelled = True
        self.reject()


def create_export() -> str:
    export = ''

    for file in network_files:
        export += f'const {file} = {json.dumps(network_files[file])};\n\n'
    export.removesuffix('\n')
    return export


def create_st_export() -> str:
    export = ''

    # We need the platform. The platform is not being converted. So please store it somewhere else if st_mode is enabled.
    return export


class Application(QMainWindow):

    def process_input(self, inputstr: str) -> None:
        global network_files
        global st_mode
        network_files = {}
        # UVDOT uses exports, dont look at the start of the string, look anywhere
        pattern = re.compile(r'(?:const|let|var) (network|places|methodMetadata|routes|transfers) = ((?:{|\[)(?:[^;]|\n)*(?:}|\]));$',
                             re.MULTILINE)

        matches = re.finditer(pattern, inputstr)
        for match in matches:
            if match.groups()[0] == 'network':
                print('[D> ST Network detected')
                network_files['places'], network_files['methodMetadata'], network_files['routes'] = convert_st_uvdot(
                    parse_js_object(match.groups()[1]))
                st_mode = True
            else:
                print(f'[D> UVDOT Network detected ({match.groups()[0]})')
                st_mode = False
                network_files[match.groups()[0]] = parse_js_object(match.groups()[1])

    def __init__(self):
        super().__init__()
        self.only_export_mode = False

        self.setWindowTitle('UVDOT Editor')
        self.create_import_page()
        self.setMinimumSize(800, 600)

    def create_import_page(self):
        self.only_export_mode = True

        def input_js(text: str):
            global network_files
            self.process_input(text)
            if ('routes' and 'methodMetadata' and 'places') in network_files:
                self.only_export_mode = False
                self.create_main_page()
            else:
                subtitle.setText('Failed to import either as ST or UVDOT file! Please check the file and try again!')

        def process_input():
            input_js(editbox.toPlainText())

        def open_file_picker():
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open network.js or data.ts', os.path.expanduser('~'),
                                                       'Network file (*.js)')
            if file_name:
                with open(file_name, 'r') as f:
                    input_js(f.read())
                    
        def open_local_file():
            try:
                with open("./data.ts", 'r') as f:
                    input_js(f.read())
            except:
                try:
                    with open("./network.js", 'r') as f:
                        input_js(f.read())
                except:
                    subtitle.setText('Failed to import a local file! Please check if netowkr.js or data.ts exists in the current directory and try again!')
                
        def skip_import():
            self.create_main_page()

        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel('Welcome to UVDOT Editor!')
        title.setFont(QFont(title.font().family(), 14))
        subtitle = QLabel('Please import a ST network.js or a UVDOT data.ts file.')
        editbox = QTextEdit()
        editbox.setPlaceholderText("Enter your file's content here")
        editbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        editbox.setFont(QFont('monospace', 10))
        submit_button = QPushButton('&Import')
        open_file_button = QPushButton('&Open file')
        auto_file_button = QPushButton('&Auto-detect file')
        skip_import_button = QPushButton('&Skip Importing')

        submit_button.clicked.connect(process_input)
        open_file_button.clicked.connect(open_file_picker)
        auto_file_button.clicked.connect(open_local_file)
        skip_import_button.clicked.connect(skip_import)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(editbox)
        layout.addWidget(submit_button)
        layout.addWidget(open_file_button)
        layout.addWidget(auto_file_button)
        layout.addWidget(skip_import_button)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_export_page(self):
        def prepare_export():
            if st_export.isChecked():
                export_area.setPlainText(create_st_export())
            else:
                export_area.setPlainText(create_export())

        def copy_export():
            if st_export.isChecked():
                pyperclip.copy(create_st_export())
            else:
                pyperclip.copy(create_export())
            if self.only_export_mode:
                self.close()

        def saveas():
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save script as...', os.path.expanduser('~'),
                                                       'JavaScript network file (*.js')
            with open(file_path, 'w') as f:
                if st_export.isChecked():
                    f.write(create_st_export())
                else:
                    f.write(create_export())
            if self.only_export_mode:
                self.close()

        def goback():
            if self.only_export_mode:
                self.close()
            else:
                self.create_main_page()

        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        back_button = QPushButton('&Back')
        back_button.clicked.connect(goback)
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
        copy_button.clicked.connect(copy_export)

        save_button = QPushButton('&Save as...')
        save_button.clicked.connect(saveas)

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
            title.setText('Seacrestica Transports Network')
        else:
            title.setText('UltraVanilla Department of Transportation Network')

        export_button = QPushButton('&Export')
        export_button.setFixedWidth(50)
        import_button = QPushButton('&Import')
        import_button.setFixedWidth(50)
        # Do different options with tabs
        tab_bar = QTabWidget()
        tab_bar.addTab(MethodsTab(), "Methods")
        tab_bar.addTab(NodesTab(), "Nodes")
        tab_bar.addTab(PlacesTab(), "Places")

        title_layout.addWidget(export_button)
        title_layout.addWidget(import_button)
        title_layout.addWidget(title)

        layout.addLayout(title_layout)
        layout.addWidget(tab_bar)

        import_button.clicked.connect(self.create_import_page)
        export_button.clicked.connect(self.create_export_page)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def closeEvent(self, a0):
        if self.only_export_mode:
            return super().closeEvent(a0)
        dialog = CloseDialog()
        if dialog.exec():
            self.only_export_mode = True
            self.create_export_page()
            return a0.ignore()
        elif dialog.cancelled:
            return a0.ignore()
        else:
            super().closeEvent(a0)


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName('uvdot-edit')

    browser = Application()
    browser.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
