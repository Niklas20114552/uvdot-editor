import os
import sys

import pyperclip
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from uvlib import NetworkFiles

network_files = NetworkFiles()


class PlacesTab(QWidget):
    def __init__(self) -> None:
        def check_button():
            self.add_button.setDisabled(not (self.add_name.text() and self.add_loc.text()))

        super().__init__()
        self.dont_update = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Name', 'Location'])
        self.table.itemChanged.connect(self.process_update)

        self.layout.addWidget(self.table)

        self.update_table()

        self.add_box = QGroupBox('Add place')
        self.add_layout = QHBoxLayout()
        self.add_box.setLayout(self.add_layout)

        self.add_name = QLineEdit()
        self.add_loc = QLineEdit()
        self.add_button = QPushButton('Add place')
        self.add_button.setFixedWidth(100)

        self.add_name.setPlaceholderText('Name')
        self.add_loc.setPlaceholderText('Location')
        if network_files.st_mode:
            self.add_loc.setDisabled(True)
        self.add_name.textChanged.connect(check_button)
        self.add_loc.textChanged.connect(check_button)

        self.add_button.clicked.connect(self.add_place)

        self.add_layout.addWidget(self.add_name)
        self.add_layout.addWidget(self.add_loc)
        self.add_layout.addWidget(self.add_button)

        self.layout.addWidget(self.add_box)
        check_button()

    def add_place(self):
        network_files.add_place(self.add_name.text(), self.add_loc.text())
        self.update_table()

    def process_update(self, item: QTableWidgetItem):
        if self.dont_update:
            return
        index = self.table.item(item.row(), 0).text()
        if item.column() == 0:
            dict_index = item.row()
            old_name = network_files.get_place_by_index(dict_index)
            if item.text().strip() == '':
                network_files.remove_place(dict_index)
            else:
                network_files.rename_place(old_name, item.text(), dict_index)
        elif item.column() == 1:
            if item.text().strip() == '':
                item.setText(network_files.get_index_place(index))
            else:
                network_files.set_index_place(index, item.text())
        self.update_table()

    def update_table(self):
        try:
            self.dont_update = True

            self.table.setRowCount(network_files.get_place_len())
            for row, name in enumerate(network_files.get_places()):
                name_cell = QTableWidgetItem(name)
                if network_files.st_mode:
                    loc_cell = QTableWidgetItem('')
                else:
                    loc_cell = QTableWidgetItem(network_files.get_location_place(name))
                if network_files.st_mode:
                    loc_cell.setFlags(loc_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)

                self.table.setItem(row, 0, name_cell)
                self.table.setItem(row, 1, loc_cell)
                self.table.resizeColumnsToContents()
                self.table.resizeRowsToContents()
        except Exception as e:
            network_files.reset_network()
            print(f"[D> An error occurred during table update: {e}")
        finally:
            self.dont_update = False


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
        if network_files.st_mode:
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
        network_files.add_method(self.add_name.text(), self.add_bg.text(), self.add_fg.text(), self.add_op.text())
        self.update_table()

    def process_update(self, item: QTableWidgetItem):
        if self.dont_update:
            return
        index = self.table.item(item.row(), 0).text()
        if item.column() == 0:
            dict_index = item.row()
            old_name = network_files.get_method_by_index(dict_index)
            if network_files.st_mode:
                if item.text().startswith('USTe '):
                    network_files.set_method_bg_color(old_name, '#066b5f')
                    network_files.rename_method(old_name, item.text(), dict_index)
                elif item.text().startswith('UST '):
                    network_files.set_method_bg_color(old_name, '#6b006b')
                    network_files.rename_method(old_name, item.text(), dict_index)
                elif item.text().strip() == '':
                    network_files.remove_method(dict_index)
                else:
                    item.setText(old_name)
            else:
                if item.text().strip() == '':
                    network_files.remove_method(dict_index)
                else:
                    network_files.rename_method(old_name, item.text(), dict_index)
        elif item.column() == 1:
            if item.text().strip() == '':
                item.setText(network_files.get_method_bg_color(index))
            else:
                network_files.set_method_bg_color(index, item.text())
        elif item.column() == 2:
            if item.text().strip() == '':
                item.setText(network_files.get_method_fg_color(index))
            else:
                network_files.set_method_fg_color(index, item.text())
        elif item.column() == 3:
            if item.text().strip() == '':
                item.setText(network_files.get_method_op(index))
            else:
                network_files.set_method_op(index, item.text())
        self.update_table()

    def update_table(self):
        try:
            self.dont_update = True

            self.table.setRowCount(network_files.get_methods_len())
            for row, name in enumerate(network_files.get_methods()):
                name_cell = QTableWidgetItem(name)
                bg_cell = QTableWidgetItem(network_files.get_method_bg_color(name))
                fg_cell = QTableWidgetItem(network_files.get_method_fg_color(name))
                operator_cell = QTableWidgetItem(network_files.get_method_op(name))
                # transfer_checkbox = QCheckBox()
                # transfer_checkbox.setChecked(name in network_files['transfers'])
                # transfer_cell = QTableWidgetItem(transfer_checkbox)
                if network_files.st_mode:
                    bg_cell.setFlags(bg_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    fg_cell.setFlags(fg_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    operator_cell.setFlags(operator_cell.flags() & ~Qt.ItemFlag.ItemIsEnabled)

                self.table.setItem(row, 0, name_cell)
                self.table.setItem(row, 1, bg_cell)
                self.table.setItem(row, 2, fg_cell)
                self.table.setItem(row, 3, operator_cell)
                # self.table.setItem(row, 4, transfer_cell)
                self.table.resizeColumnsToContents()
                self.table.resizeRowsToContents()
        except Exception as e:
            network_files.reset_network()

            print(f"[D> An error occurred during table update: {e}")
        finally:
            self.dont_update = False


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


class Application(QMainWindow):

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
            network_files.process_file(text)
            if network_files.is_valid_network():
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
            except Exception:
                try:
                    with open("./network.js", 'r') as f:
                        input_js(f.read())
                except Exception:
                    subtitle.setText(
                        'Failed to import a local file! Please check if network.js or data.ts exists in the current directory and try again!')

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
        import_layout = QHBoxLayout()
        submit_button = QPushButton('&Import Textbox')
        open_file_button = QPushButton('&Open file')
        auto_file_button = QPushButton('&Auto-detect file')
        skip_import_button = QPushButton('&Skip Importing')
        import_layout.addWidget(submit_button)
        import_layout.addWidget(open_file_button)
        import_layout.addWidget(auto_file_button)
        import_layout.addWidget(skip_import_button)

        submit_button.clicked.connect(process_input)
        open_file_button.clicked.connect(open_file_picker)
        auto_file_button.clicked.connect(open_local_file)
        skip_import_button.clicked.connect(skip_import)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(editbox)
        layout.addLayout(import_layout)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_export_page(self):
        def prepare_export():
            if st_export.isChecked():
                export_area.setPlainText(network_files.create_st_export())
            else:
                export_area.setPlainText(network_files.create_export())

        def copy_export():
            if st_export.isChecked():
                pyperclip.copy(network_files.create_st_export())
            else:
                pyperclip.copy(network_files.create_export())
            if self.only_export_mode:
                self.close()

        def saveas():
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save script as...', os.path.expanduser('~'),
                                                       'JavaScript network file (*.js')
            with open(file_path, 'w') as f:
                if st_export.isChecked():
                    f.write(network_files.create_st_export())
                else:
                    f.write(network_files.create_export())
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

        uvdot_export.setDisabled(network_files.st_mode)
        uvdot_export.setChecked(not network_files.st_mode)
        st_export.setChecked(network_files.st_mode)

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
        layout.addWidget(save_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_main_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title = QLabel()
        title.setFont(QFont(title.font().family(), 14))
        if network_files.st_mode:
            title.setText('Seacrestica Transports Network')
        else:
            title.setText('UltraVanilla Department of Transportation Network')

        export_button = QPushButton('&Export')
        export_button.setFixedWidth(50)
        import_button = QPushButton('&Import')
        import_button.setFixedWidth(50)
        # Do different options with tabs
        tab_bar = QTabWidget()
        tab_bar.addTab(MethodsTab(), "&Methods")
        tab_bar.addTab(NodesTab(), "&Nodes")
        tab_bar.addTab(PlacesTab(), "&Places")

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

    editor = Application()
    editor.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
