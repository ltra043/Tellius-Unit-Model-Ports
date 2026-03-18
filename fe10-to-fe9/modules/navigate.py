from pathlib import Path
from PyQt6.QtWidgets import (QMessageBox)
import shutil

from modules import start
from modules import config
from modules.config import MODELS

# navigate.goto_0(self)     return: None
def goto_0(self):
    print(f'\nRunning navigate.goto_0() ...')
    self.stackedWidget.setCurrentWidget(self.Start_0)
    self.radio_delete_anim_0.setChecked(True)


# navigate.goto_1(self)     return: input_dir, output_dir
def goto_1(self):
    """Confirm valid input & output selection
    - Check if input and output are existing directories and that neither field is empty.
    - Determine source folder name and edit label on Port_1.
    - Clear or refresh Port_1 textbox and table, in case data remains from previous use.

    :return: list(input_dir: path, output_dir: path)
    """
    directory_dict = start.directory(self)  # create output dirs if they do not exist
    print(f'\nRunning navigate.goto_1() ...')
    if directory_dict is None:
        QMessageBox.warning(self, "Warning", f'Please enter a valid output path')
        return None
    input_dir, output_dir, input_pack, output_pack = list(directory_dict.values())
    input_len = len(self.lineEdit_input_0.text())
    output_len = len(self.lineEdit_output_0.text())
    len_0_check = input_len * output_len    # len_0_check == 0 if at least one field is empty

    if not input_dir.exists():
        QMessageBox.warning(self, "Warning", f'Please enter a valid input path')
        return None
    elif not input_pack.exists():
        QMessageBox.warning(self, "Warning", f'Please decompress pack.cmp using Lumina to '
                                             f'continue')
        return None

    if len_0_check != 0:
        reset(self)
        clear_output(self, output_dir)
        config.reset()

        '''Edit source folder text and load corresponding comoBox item'''
        model = input_dir.name
        if model == 'knight1_sp_ｆ':     # fix Fiona T1, which uses non-standard character ｆ
            model = 'knight1_sp_f'
        self.label_src_1.setText(f'Source Folder: {model}')
        if model in MODELS:
            self.comboBox_1.setCurrentIndex(MODELS.index(model))

        self.stackedWidget.setCurrentWidget(self.Port_1)
        return input_dir, output_dir
    else:
        QMessageBox.warning(self, "Warning", f'Please enter a valid output path')
        return None


def reset(self):
    """Clear or reset data from previous use"""
    print(f'\nRunning navigate.reset() ...')
    self.tableW_1.clearContents()
    self.tableW_1.setRowCount(12)
    self.radio_wait_1.setChecked(True)
    self.radio_comboBox_1.setChecked(True)
    self.radio_knife_no.setChecked(True)
    self.comboBox_1.setCurrentIndex(0)
    self.label_status_1.setText('Waiting for input. '
                                '\nClick "Load / Refresh Table" or "Port Files"')


# navigate.clear_output(self, output_dir: Path)      return: None
def clear_output(self, output_dir: Path):
    print(f'\nRunning navigate.clear_output() ...')
    if self.radio_delete_none_0.isChecked():
        return None
    paths = output_dir.iterdir()

    if self.radio_delete_all_0.isChecked():
        for path in paths:
            if path.is_file():                  # delete files in main output directory
                path.unlink()
            elif path.name == 'pack':
                for pack_path in path.iterdir():
                    if pack_path.is_file():          # delete files in main pack directory
                        pack_path.unlink()
                    elif pack_path.is_dir():         # delete folders in main pack directory
                        shutil.rmtree(pack_path, ignore_errors=True)
            elif path.is_dir():                 # delete folders in main output directory
                shutil.rmtree(path, ignore_errors=True)

    elif self.radio_delete_anim_0.isChecked():
        for path in paths:
            if path.suffix =='.ga':  # delete .ga files in main output directory
                path.unlink()
            elif path.name == 'pack':
                for pack_path in path.iterdir():
                    if pack_path.suffix == '.ga':  # delete .ga files in main pack directory
                        pack_path.unlink()

    return None

