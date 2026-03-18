from sys import exit, argv
from datetime import datetime
from pathlib import Path
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QStackedWidget)
from PyQt6.QtGui import QStandardItemModel

from modules import start, navigate, port
from modules.config import *

assets_path = Path(resource_path('assets'))
asset_ui = assets_path.joinpath('10-to-9-ymu.ui')
asset_anim_data = assets_path.joinpath('FE10-AnimData.txt')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(asset_ui, self)
        self.stackedWidget.setCurrentWidget(self.Start_0)

        load_anim_data_fe10()
        self.comboBox_1.addItems(MODELS)

        self.directory = "."
        self.tableModel = QTableWidgetItem()
        self.selectModel = QStandardItemModel()
        self.selected = []
        self.comboBox_1.setEditable(True)

        # navigation buttons
        self.button_next_0.clicked.connect(lambda: navigate.goto_1(self))
        self.button_back_1.clicked.connect(lambda: navigate.goto_0(self))

        # Start_0 buttons
        self.button_input_0.clicked.connect(lambda: start.select_input(self))
        self.button_output_0.clicked.connect(lambda: start.select_output(self))

        # Port_1 buttons
        self.radio_comboBox_1.toggled.connect(lambda: port.toggle(self))
        self.button_load_table_1.clicked.connect(self.table_1)
        self.button_run_1.clicked.connect(self.run_1)
        self.comboBox_1.currentIndexChanged.connect(lambda: port.fill_anim_data_1(self))

    def table_1(self):
        print(f'\nRunning MainWindow.table_1() ...')
        self.tableW_1.clearContents()  # reset table
        self.tableW_1.setRowCount(12)
        status, rename_dict = port.load_table_1(self)
        if status:
            path_dict = port.fill_table_1(self, rename_dict)
            current_datetime = datetime.now().strftime("%H:%M:%S")
            self.label_status_1.setText(f'Table filled at time {current_datetime}')
            return True, path_dict
        else:
            path_dict = {}
            current_datetime = datetime.now().strftime("%H:%M:%S")
            self.label_status_1.setText(f'Failed to load files at {current_datetime}')
            return False, path_dict

    def run_1(self):
        print(f'\nRunning MainWindow.run_1() ...')
        self.label_status_1.setText(f'Processing files ...')
        status, path_dict = self.table_1()
        if status:
            src_paths, dest_paths = list(path_dict.values())
            directory_dict = start.directory(self)
            _, _, input_pack, _ = list(directory_dict.values())

            '''Copy any non-animation file (excluding pack.cmp)'''
            wp_dict = port.copy_anim(src_paths, dest_paths, input_pack)
            port.copy_other(self, wp_dict, True)
            if self.radio_knife_yes.isChecked():
                port.rename_no_wp(directory_dict)
            current_datetime = datetime.now().strftime("%H:%M:%S")
            self.label_status_1.setText(f'Finished porting files at time {current_datetime}')
        print('Completed porting all files!')


# load_anim_data_fe10()     return: None
def load_anim_data_fe10():
    """ Load AnimData info from file
            - Anim Data is used later to determine which weapon is assigned to each animation
    :return: None
    """
    print(f'\nRunning load_anim_data_fe10() ...')
    with open(asset_anim_data, 'r') as f:
        data = f.readlines()
    for x in range(245):
        line = (x * 3)
        model = data[line][:-1]
        anim_data = data[line + 1][:-1]
        ANIM_DATA_DICT[model] = anim_data

    anim_data_dict_sorted = dict(sorted(ANIM_DATA_DICT.items()))
    MODELS.append('Select Model')
    MODELS.extend(list(anim_data_dict_sorted.keys()))
    # print(MODELS)


def main():
    app = QApplication(argv)
    main_window = MainWindow()
    widget = QStackedWidget()
    widget.addWidget(main_window)
    widget.setGeometry(300, 100, 650, 530)
    widget.show()
    exit(app.exec())


if __name__ == '__main__':
    main()
