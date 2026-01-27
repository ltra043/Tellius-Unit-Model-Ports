import sys
import os
import math
from pathlib import Path
import shutil
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTableWidgetItem, QPushButton,
                             QLabel, QMessageBox, QComboBox, QLineEdit, QFileDialog, QDialog,
                             QStackedWidget, QTextEdit)
from PyQt6.QtGui import QStandardItem, QStandardItemModel

anim_paths = []
other_paths = []
src_file_list = []
dest_file_list = []
standard_src_file_list = []

motions_all_9 = ['atk1', 'crit', 'damage', 'dead', 'escape', 'event', 'magic1',
                 'magic2', 'move2', 'ready', 'rod', 'tackle', 'trans', 'move', 'wait', 'atk2']
motions_10_to_9 = ['atk', 'arc', 'damage', 'dead', 'avoid', 'evt1', 'mag',
                   'mag', 'walk', 'poise', 'rod', 'tack', 'trans', 'move', 'wait']

motions_10_evt = ['evt2', 'evt3', 'evt4', 'evt5', 'evt6', 'evt7', 'evt8',
                  'evt9', 'evt10', 'evt11', 'evt12']

motions_all_10 = ['wait', 'move', 'twait', 'walk', 'atk', 'atk2', 'mag', 'mag2', 'crit',
                  'atku', 'atk2u', 'magu', 'mag2u', 'critu', 'atkd', 'atk2d', 'magd',
                  'mag2d', 'critd', 'arc', 'arc2', 'arc3', 'arc4', 'arc5', 'rod', 'tack',
                  'avoid', 'poise', 'guard', 'damage', 'trans', 'dead', 'up', 'down', 'flip',
                  'flip2', 'evt1', 'evt2', 'evt3', 'evt4', 'evt5', 'evt6', 'evt7', 'evt8',
                  'evt9', 'evt10', 'evt11', 'evt12']
wp_all_str_list = ['N', 'SW', 'SP', 'JA', 'AX', 'HA', 'BW', 'RD', 'BG']
anim_data_dict = {}
anim_data_dict_hex = {}
model_list = []

#resource_path()    return: os.path.join(base_path, relative_path)
def resource_path(relative_path):
    '''
    Redirects the paths of external files referenced by this script. Wrap all filenames with the
    function resource_path()
    from https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file

    :param relative_path: Path
    :return: os.path.join(base_path, relative_path): Path
    '''
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(resource_path('10-to-9-ymu.ui'), self)
        self.stackedWidget.setCurrentWidget(self.Start_0)

        load_anim_data_fe10()
        self.comboBox_1.addItems(model_list)

        self.directory = "."
        self.tableModel = QTableWidgetItem()
        self.selectModel = QStandardItemModel()
        self.selected = []
        self.comboBox_1.setEditable(True)

        # navigation buttons
        self.button_next_0.clicked.connect(lambda: Navigate.goto_1(self))
        self.button_back_1.clicked.connect(lambda: Navigate.goto_0(self))

        # Start_0 buttons
        self.button_input_0.clicked.connect(lambda: Start.select_input(self))
        self.button_output_0.clicked.connect(lambda: Start.select_output(self))

        # Port_1 buttons
        self.radio_comboBox_1.toggled.connect(lambda: Port.toggle(self))
        self.button_load_table_1.clicked.connect(self.table_1)
        self.button_run_1.clicked.connect(self.run_1)
        self.comboBox_1.currentIndexChanged.connect(lambda: Port.fill_anim_data_1(self))

    def table_1(self):
        # Port.load_table_1(self)
        print(f'running MainWindow.table_1() ...')
        status, rename_dict = Port.load_table_1(self)
        if status:
            path_dict = Port.fill_table_1(self, rename_dict)
            return True, path_dict
        else:
            path_dict = {}
            return False, path_dict

    def run_1(self):
        # Port.run_1(self, rename_dict, copy_list)
        print(f'Running "run_1" ...')
        status, path_dict = self.table_1()
        src_path_list, dest_path_list = list(path_dict.values())
        print(status)
        if status:
            directory_dict = Start.directory(self)
            _, _, input_pack, _ = list(directory_dict.values())

            '''Copy any non-animation file (excluding pack.cmp)'''
            Port.copy_other(self)
            wp_dict = Port.copy_anim(src_path_list, dest_path_list, input_pack)
        print('Completed porting all files!')


class Navigate:
    # Navigate.goto_0(self)     return: None
    def goto_0(self):
        print(f'Running function goto_0')
        self.stackedWidget.setCurrentWidget(self.Start_0)

    # Navigate.goto_1(self)     return: input_dir, output_dir
    def goto_1(self):
        ''' Confirm valid input & output selection
        - Check if input and output are existing directories and that neither field is empty.
        - Determine source folder name and edit label on Port_1.
        - Clear or refresh Port_1 textbox and table, in case data remains from previous use.

        :return: list(input_dir: path, output_dir: path)
        '''
        print(f'Running "goto_1" ...')
        input_dir = Path(self.lineEdit_input_0.text())
        output_dir = Path(self.lineEdit_output_0.text())
        input_pack = input_dir.joinpath('pack')
        input_len = len(self.lineEdit_input_0.text())
        output_len = len(self.lineEdit_output_0.text())
        len_0_check = input_len * output_len    # len_0_check == 0 if at least one field is empty


        if not input_pack.exists():
            QMessageBox.warning(self, "Warning", f'Please decompress pack.cmp using Lumina to '
                                                 f'continue')
            return

        if input_dir.exists() and len_0_check != 0:
            model = input_dir.name
            self.label_src_1.setText(f'Source Folder: {model}')     #set source folder name
            self.tableW_1.clearContents()                           #reset table
            self.tableW_1.setRowCount(12)
            self.radio_comboBox_1.setChecked(True)                  #reset AnimData
            self.comboBox_1.setCurrentIndex(len(model_list)-1)
            if model in model_list:                                 # match AnimData to src folder
                self.comboBox_1.setCurrentIndex(model_list.index(model))

            Start.directory(self)       # create output directories if they do not exist
            self.stackedWidget.setCurrentWidget(self.Port_1)
            return input_dir, output_dir
        else:
            QMessageBox.warning(self, "Warning", f'Please enter an existing path for input/output')
            return


class Start:
    # Start.select_input(self)      return: None
    def select_input(self):
        self.directory = QFileDialog.getExistingDirectory(None, "Select Input Directory")
        if self.directory:
            # If a folder was selected (not cancelled), update lineEdit to selected directory
            input_dir = Path(self.directory)
            self.lineEdit_input_0.setText(str(input_dir))
        else:
            # If a folder selection was cancelled, use the last input
            last_input = self.lineEdit_input_0.text()
            print(f'No selection was made. Reusing the last input:\n{last_input}')
            print('')
            self.lineEdit_input_0.setText(last_input)

    # Start.select_output(self)      return: None
    def select_output(self):
        self.directory = QFileDialog.getExistingDirectory(None, "Select Output Directory")
        if self.directory:
            # If a folder was selected (not cancelled), update lineEdit to selected directory
            output_dir = Path(self.directory)
            self.lineEdit_output_0.setText(str(output_dir))
        else:
            # If a folder selection was cancelled, use the last output
            last_output = self.lineEdit_output_0.text()
            print('No selection was made. Reusing the last input ' + last_output)
            print('')
            self.lineEdit_output_0.setText(last_output)

    # Start.directory(self)     return: directory_dict | None (if input_pack DNE)
    def directory(self):
        input_dir = Path(self.lineEdit_input_0.text())
        output_dir = Path(self.lineEdit_output_0.text())
        input_pack = input_dir.joinpath('pack')
        output_pack = output_dir.joinpath('pack')

        if not output_dir.exists():
            output_dir.mkdir()
        if not output_pack.exists():
            output_pack.mkdir()

        directory_dict = {}
        directory_dict['input_dir'] = input_dir
        directory_dict['output_dir'] = output_dir
        directory_dict['input_pack'] = input_pack
        directory_dict['output_pack'] = output_pack

        return directory_dict


class Port:
    # Port.toggle(self)      return: None
    def toggle(self):
        print(f'Running "fill_anim_data_1" ...')
        if self.radio_comboBox_1.isChecked():
            print(f'comboBox selected')
            self.textEdit_anim_data_1.setReadOnly(True)
            self.comboBox_1.setEnabled(True)
        elif self.radio_textBox_1.isChecked():
            print(f'textBox selected')
            self.textEdit_anim_data_1.setReadOnly(False)
            self.comboBox_1.setEnabled(False)


    # Port.fill_anim_data_1(self)      return: None
    def fill_anim_data_1(self):
        print(f'Running "fill_anim_data_1" ...')
        model = self.comboBox_1.currentText()
        print(f'anim_data_dict in fill: {anim_data_dict}')
        if model == 'Select Model':
            self.textEdit_anim_data_1.setText('Select your FE10 source model from the dropdown '
                                              'list.\n\nAlternatively, input AnimData in this '
                                              'textbox.')
        else:
            # print(anim_data_dict)
            anim_data = anim_data_dict[model]
            print(f'model: {model}')
            print(anim_data)
            self.textEdit_anim_data_1.setText(str(anim_data))


    # Port.load_table_1(self)      return True | False, rename_dict
    def load_table_1(self):
        ''' Load source and dest file names and fill table
        - Generate list of bytes from AnimData input
        - Read AnimData to determine the weapon type for each animation ile
        - Write dictionary matching each key (source file) to a value (renamed file)
        - Write list for source files that need to be duplicated
            - Source file is used for multiple weapons (usually None and another weapon)
            - Format is a list of 2-length lists.
                - The first item of the sub-list is the renamed file in the output directory
                - Last item of sub-list is the name the file should be duplicated and renamed to
        - Check that files expected according AnimData exist in the input directory
        - Fill the table with source and destination file names

        :return: tuple (bool, rename_dict)
            bool: true of false if data was loaded (data not loaded if AnimData is incorrect size)
            rename_dict = {src_file: dest_file, ...}
            dupe_src_anim_data = [[renamed file which will be duplicated, ...]
            dupe_dest_anim_data = [destination duplicated file], ...]
        '''
        print(f'Running "load_table_1" ...')

        '''Local Variables'''
        wp_num_list = []
        rename_dict = {}
        rename_status = False
        anim_data = self.textEdit_anim_data_1.toPlainText()

        '''Check for correct  AnimData size'''
        if len(anim_data) / 2 == 440:
            anim_data = anim_data[16:440 * 2]
            print(f'anim_data: {anim_data}, len = {len(anim_data) / 2}')
        elif len(anim_data) / 2 != 432:
            QMessageBox.warning(self, "Warning", f'Incorrect AnimData size')
            return False, rename_dict
        for count in range(432):
            byte = anim_data[count * 2:count * 2 + 2]
            byte_int = int(byte, 16)
            wp_num_list.append(byte_int)

        # print(f'anim_data_dict_int:\n{anim_data_dict_int}\n')
        print(f'wp_num_list: {wp_num_list}\nlen = {len(wp_num_list)}')

        '''Make list of source/dest file names '''
        for count, wp_num in enumerate(wp_num_list):
            if wp_num != 0:
                wp_str_index = math.floor(count / 48)
                wp_str = wp_all_str_list[wp_str_index]  # determine weapon type

                motion_index = count % 48
                src_motion = motions_all_10[motion_index]  # determine src anim motion
                # print(f'SRC: {src_motion}_{wp_num}')

                '''Determine fe9 destination motion'''
                if src_motion in motions_10_to_9:
                    rename_status = True
                    index = motions_10_to_9.index(src_motion)
                    dest_motion = motions_all_9[index]
                elif src_motion in motions_10_evt:
                    rename_status = True
                    dest_motion = src_motion
                if rename_status:  # Ignores files with no equivalent FE9 animation
                    src_file = f'{src_motion}_{wp_num}.ga'
                    dest_file = f'{dest_motion}_{wp_str}.ga'
                    if src_file not in list(rename_dict.keys()):
                        '''Check if source file is used for multiple weapon animations'''
                        rename_dict[src_file] = [dest_file]
                    else:
                        rename_dict[src_file].append(dest_file)

                    if src_motion == 'atk':
                        dest_file = f'atk2_{wp_str}.ga'
                        rename_dict[src_file].append(dest_file)
            rename_status = False

        # print(f'rename_dict: {rename_dict}\nlen = {len(rename_dict)}')
        # print(f'dupe_src_anim_data: {dupe_src_anim_data}\nlen = {len(dupe_src_anim_data)}')
        # print(f'dupe_dest_anim_data: {dupe_dest_anim_data}\nlen = {len(dupe_dest_anim_data)}')
        return True, rename_dict


    # Port.fill_table_1(self, rename_dict)      return: path_dict
        # path_dict.keys() = src_path_list, dest_path_list
    def fill_table_1(self, rename_dict: dict):
        '''
        - Evaluate the lists of source and destination files from load_table_1. 
        - Determine if source files exist in the input directory and match to a destination file. 
        - Distinguish between files for which the program should read and write an edited version 
        of the source file, and which can be duplicated later to avoid repeating the same work.   

        :param rename_dict: dictionary of FE10 to FE9 renamed anims generated in load_table_1
        :return: path_dict
                    - dictionary of source and destination paths
                    - keys = src_path_list, dest_path_list, dupe_src_path_list, dupe_dest_path_list
                    - src_path file's data will be edited and written to the dest_path
        '''
        print('Running "fill_table_1" ...')
        directory_dict = Start.directory(self)
        input_dir, output_dir, input_pack, output_pack = list(directory_dict.values())
        input_file_list = []
        input_path_list = []  # Different from input_paths[]; these paths have been verified

        src_file_list = []
        dest_file_list = []
        src_path_list = []
        dest_path_list = []
        standard_src_file_list = []

        # List of all animation file paths in input directory and pack
        input_paths = [
            [file for file in input_dir.iterdir() if file.suffix == '.ga'],
            [file for file in input_pack.iterdir() if file.suffix == '.ga']
        ]
        input_paths = [path for sublist in input_paths for path in sublist]

        ''' Check if file name is in the proper format 'motion_#.ga' or 'prefix_motion_#.ga'''
        for path in input_paths:
            src_format = True
            src_name = path.stem
            src_file = path.name
            # print(src_name.split('_'))
            # print(len(src_name.split('_')))
            if len(src_name.split('_')) == 2:
                src_motion, wp_num = src_name.split('_')
                standard_src_file = src_file
            elif len(src_name.split('_')) == 3:
                prefix, src_motion, wp_num = src_name.split('_')
                standard_src_file = f'{src_motion}_{wp_num}.ga'
            else:
                src_motion = "N/A"
                wp_num = "N/A"
                src_format = False
            if (src_motion.lower() in motions_all_10 and wp_num.isdecimal() and len(wp_num) == 1):
                input_file_list.append(src_file)
                standard_src_file_list.append(standard_src_file)
                input_path_list.append(path)
            else:
                src_format = False
            print(f'src_motion: {src_motion}, wp_num: {wp_num}, status: {src_format}')

        if not src_format:
            QMessageBox.warning(self, "Warning",
                                f'Some animation file names are in a non-standard format.'
                                f'These files will be skipped over. If you wish to include these '
                                f'files, change their names to match the format: motion_#.ga '
                                f'and refresh the table.\n\n'
                                f'The issue may be:\n'
                                f'- Motion name does not exist in vanilla FE10\n'
                                f'- Animation weapon # after "_" is not a single digit number\n'
                                f'- Animation name contains more than 2 "_" characters* (See '
                                f'Note)\n\n '
                                f'Note: Standard names include 1 underscore, but this program '
                                f'allows for a prefix and 1 additional underscore to be added to '
                                f'the start of the name for organization purposes\n'
                                )

        if len(standard_src_file_list) > 0:
            for standard_src_file in [f for f in standard_src_file_list
                                      if f in list(rename_dict.keys())]:
                src_index = standard_src_file_list.index(standard_src_file)
                src_occurrence = len(rename_dict[standard_src_file])
                src_file = input_file_list[src_index]
                src_path = input_path_list[src_index]
                src_file_list.extend([src_file]*src_occurrence)
                src_path_list.extend([src_path]*src_occurrence)

                for dest_file in rename_dict[standard_src_file]:
                    print(f'dest_file: {dest_file}')
                    if src_path.parent.name == 'pack':
                        dest_path = output_pack.joinpath(dest_file)
                        print(f'pack dest: {dest_path} ')
                    else:
                        dest_path = output_dir.joinpath(dest_file)
                    dest_file_list.append(dest_file)
                    dest_path_list.append(dest_path)

            '''Sort files by src_file A_Z, maintaining matching order'''
            src_file_list_sorted = list(enumerate(src_file_list))
            src_file_list_sorted.sort(key=lambda x: x[1])
            dest_file_list_sorted = []

            for index, src_file in src_file_list_sorted:
                dest_file = dest_file_list[index]
                dest_file_list_sorted.append(dest_file)
                print(f'index: {index}, SRC: {src_file}, DEST: {dest_file}')
            src_file_list_sorted = [x[1] for x in src_file_list_sorted]

        '''Fill Table with src and dest file names'''
        row_count = len(src_file_list_sorted)
        self.tableW_1.clearContents()
        self.tableW_1.setRowCount(row_count)
        for row, file in enumerate(src_file_list_sorted):
            # print(str(row) + ' ' + file)
            item = QTableWidgetItem(file)
            self.tableW_1.setItem(row, 0, item)
        for row, file in enumerate(dest_file_list_sorted):
            # print(str(row) + ' ' + file)
            item = QTableWidgetItem(file)
            self.tableW_1.setItem(row, 1, item)
        self.tableW_1.setColumnWidth(0, 143)
        self.tableW_1.setColumnWidth(1, 143)
        # print(f'row count: {row_count}')
        path_dict = {'src_path_list': src_path_list, 'dest_path_list': dest_path_list}
        return path_dict


    # Port.copy_anim(input_pack)        return: None
    @staticmethod
    def copy_anim(src_path_list, dest_path_list, input_pack):
        """ Copy and modify all .ga anim files from src_path_list
            1. Read model's skeleton.g file and look for up to 8 possible displayed weapons.
            2. Sort files according to the number and type of pointers at the end of the file.
            3. Hex edit all files contain footer section 2. See Port.hex_edit() for more info
            4. Add model's weapons to a list (from skeleton and from collective footer 2 data)
            5. Hex edit files without footer section 2. #!!! Test set col 2 to 00 instead of 08
        :param src_path_list: list of source paths of animation files from the source model
        :param dest_path_list: list of destination paths for edited animation files
        :param input_pack: path of the pack folder in the input directory
        :return: None
        """
        print(f'Running copy_anim ...')
        # print(f'src_path_list:\n{src_path_list}')

        '''Look for visible weapons in skeleton.g'''
        wp_dict = Port.count_skeleton_wp(input_pack)

        for count, src_path in enumerate(src_path_list):
            dest_path = dest_path_list[count]
            Port.hex_edit(src_path, dest_path, wp_dict)

        return wp_dict

    # Port.copy_other(self)         return: None
    def copy_other(self):
        print(f'Running "copy_other" ...')
        directory_dict = Start.directory(self)
        input_dir, output_dir, input_pack, output_pack = list(directory_dict.values())

        '''List of non-animation files in the source directory'''
        other_path_list = [path for path in input_dir.iterdir()
                           if path.suffix != '.ga' and path.stem != 'pack']
        other_path_list = other_path_list + [path for path in input_pack.iterdir()
                                             if path.suffix != '.ga']

        '''Copy non-animation files from input directory to output directory.'''
        for src_path in other_path_list:
            # print(src_path.parent.name)
            if src_path.parent.name == 'pack':
                dest_path = output_pack.joinpath(src_path.name)
            else:
                dest_path = output_dir.joinpath(src_path.name)
            shutil.copy(src_path, dest_path)
            print(f'{src_path.name}:\nSRC: {src_path}\nDEST: {dest_path}\n')


    # Port.count_ftr_ptr(src_path_list)          return sort_ftr_dict
    @staticmethod
    def count_ftr_ptr(src_path_list) -> dict:
        """ --- Sort by footer pointer count--- \n
        Some expected results are:
            - Units with 0 or 1 visible weapon:
                - ftr_0_none_list contains wait, poise animations
                - ftr_1_only_list contains all other animations
                - event animations could be in any of the lists
            - Units with 2+ weapons (this considers SP/JA and AX/HA as separate weapons):
                - ftr_2_only_list contains damage, wait, poise, possibly event animations
                - ftr_3_all_list contains all other animations
            - Note, these are not strictly followed rules/groupings

        :return: sort_ftr_dict = {'ftr_0_none_list': ftr_0_none_list, 'ftr_1_only_list': ftr_1_only_list,
                             'ftr_2_only_list': ftr_2_only_list, 'ftr_3_all_list':ftr_3_all_list}
        """
        print(f'Running count_ftr_ptr ...')
        ftr_0_none_list = []
        ftr_1_only_list = []
        ftr_2_only_list = []
        ftr_3_all_list = []

        total_edit_count = len(src_path_list)
        for count, src_path in enumerate(src_path_list):
            print(f'Sorting {src_path.name} ... ({count + 1}/{total_edit_count})')
            end = f'{src_path.name} sorted!\n'  # string to print at end of
            # iteration

            with open(src_path, "rb") as SOURCE:
                # value of the pointer at the start of file
                data = SOURCE.read()
                total_size = len(data)
                hdr_ptr = data[0:4]

                '''Sort by presence of footer data section(s)'''
                hdr_ptr_int = int.from_bytes(hdr_ptr, "big")

                if hdr_ptr_int == 0:
                    ftr_count = 0
                    ftr_0_none_list.append(src_path)
                    print(end)
                    continue
                    # return

                '''Read first pointer in footer index'''
                SOURCE.seek(hdr_ptr_int)
                ftr_ID_first = int.from_bytes(SOURCE.read(4), "big")
                if ftr_ID_first == 5:
                    ftr_ptr_1 = SOURCE.read(4)
                    ftr_data_1_start = int.from_bytes(ftr_ptr_1, "big")
                else:  # ftr_ID_first == 0
                    ftr_ptr_2 = SOURCE.read(4)
                    ftr_data_2_start = int.from_bytes(ftr_ptr_2, "big")

                '''Determine # of footer data sections'''
                SOURCE.seek(total_size - 4)
                last_4_bytes = SOURCE.read(4)
                last_4_bytes_int = int.from_bytes(last_4_bytes, "big")
                if last_4_bytes_int != 0:
                    ftr_count = 3  # all 3 data pointers exist
                    ftr_3_all_list.append(src_path)
                    ftr_ptr_3 = last_4_bytes
                    ftr_data_3_start = last_4_bytes_int
                    print(end)
                    continue
                    # return
                else:
                    ftr_count = 1

                if ftr_ID_first == 5:  # if only footer_data_1 exists
                    ftr_1_only_list.append(src_path)
                    print(end)
                    continue
                    # return
                else:  # if only footer_data_2 exists
                    ftr_2_only_list.append(src_path)
                    print(end)

            # print(f'ftr_0_none_list: {ftr_0_none_list}')
            # print(f'ftr_1_only_list: {ftr_1_only_list}')
            # print(f'ftr_2_only_list: {ftr_2_only_list}')
            # print(f'ftr_3_all_list: {ftr_3_all_list}')
        sort_ftr_dict = {'ftr_0_none_list': ftr_0_none_list, 'ftr_1_only_list': ftr_1_only_list,
                         'ftr_2_only_list': ftr_2_only_list, 'ftr_3_all_list': ftr_3_all_list}
        for key in list(sort_ftr_dict.keys()):
            print(f'{key}: {len(sort_ftr_dict[key])}')
            if key == 'ftr_3_all_list':
                print('')
        return sort_ftr_dict


    # Port.read_hex(src_path: Path)        return data_dict
    @staticmethod
    def read_hex(src_path: Path):
        ''' --- Read hex data and organize into parts ---    \n
        Read and store hex data for the following sections:
            - Initial header pointer & file organization info
            - Skeleton Bone Table, Metadata, Keyframe Data
            - All footer sections, identifying data,  and pointers

        Return is a dictionary tying together a section's name with its hex data (bytes or list
        of integers). It also contains other file info, such as ftr_ID. The value of ftr_ID is an
        integer telling which footer pointers are present (0-3)

        :param src_path: Path of the source animation file
        :return: data_dict {'data_section': hex data, 'ftr_ID': int (0-3)}
        '''
        print('Running read_hex ...')
        data_dict = {}

        with open(src_path, "rb") as SOURCE:
            # Value of the pointer at the start of file
            data = SOURCE.read()
            total_size = len(data)
            hdr_ptr = data[0:4]
            # print(f'hdr_ptr: {hdr_ptr}')
            hdr_ptr_int = int.from_bytes(hdr_ptr, "big")

            '''File organization info'''
            bytes_09_1b = data[9:28]
            table_count_src = data[28:32]
            SOURCE.seek(32)
            table_addr = SOURCE.read(4)
            meta_data_addr = SOURCE.read(4)
            bytes_28_2b = SOURCE.read(4)
            frame_data_addr = SOURCE.read(4)
            print(f'bytes_09_1B: {bytes_09_1b}')
            print(f'table_count_src: {table_count_src}')
            print(
                f'File address markers: {table_addr}, {meta_data_addr}, {bytes_28_2b}, {frame_data_addr}')

            '''Table info & data'''
            table_size = int.from_bytes(table_count_src, "big") * 16
            table_start = int.from_bytes(table_addr, "big")
            SOURCE.seek(table_start)
            table_data = SOURCE.read(table_size)

            '''Mapping Meta Data
            - This is the data immediately after the table.
            - Possibly starting position and/or visibility control
            '''
            meta_start = int.from_bytes(meta_data_addr, "big")
            frame_start = int.from_bytes(frame_data_addr, "big")
            meta_data_size = frame_start - meta_start
            SOURCE.seek(meta_start)
            meta_data = SOURCE.read(meta_data_size)

            '''Build current data dictionary'''
            data_dict['hdr_ptr'] = hdr_ptr
            data_dict['bytes_09_1b'] = bytes_09_1b
            data_dict['table_count_src'] = table_count_src
            data_dict['table_addr'] = table_addr
            data_dict['meta_data_addr'] = meta_data_addr
            data_dict['bytes_28_2b'] = bytes_28_2b
            data_dict['frame_data_addr'] = frame_data_addr
            data_dict['table_data'] = table_data
            data_dict['meta_data'] = meta_data

            '''Map Keyframe Data and Footer'''
            if hdr_ptr_int == 0:        # if no footer data exists, ftr_ID = 0
                ftr_ID = 0
                frame_data_size = total_size - frame_start
            else:
                SOURCE.seek(hdr_ptr_int)
                ftr_ID_data = SOURCE.read(4)
                ftr_ptr = SOURCE.read(4)
                ftr_start = int.from_bytes(ftr_ptr, "big")
                ftr_data_size = hdr_ptr_int - ftr_start
                frame_data_size = ftr_start - frame_start
                SOURCE.seek(ftr_start)
                ftr_data = SOURCE.read(ftr_data_size)

                '''Determine ftr_ID if footer data exists'''
                SOURCE.seek(total_size - 4)
                ftr_3_ptr = SOURCE.read(4)
                ftr_3_start = int.from_bytes(ftr_3_ptr, "big")
                if ftr_3_start != 0:
                    ftr_ID = 3
                elif int.from_bytes(ftr_ID_data, "big") == 0:
                    ftr_ID = 2
                else:
                    ftr_ID = 1

            if ftr_ID == 3:
                ftr_2_ID_data = ftr_ID_data
                ftr_2_ptr = ftr_ptr
                ftr_2_start = ftr_start

                SOURCE.seek(ftr_3_start)
                ftr_1_ID_data = SOURCE.read(4)
                ftr_1_ptr = SOURCE.read(4)
                ftr_1_start = int.from_bytes(ftr_1_ptr, "big")
                from_1_ptr_2_ID = SOURCE.read(4)

                ftr_1_data_size = ftr_2_start - ftr_1_start
                ftr_2_data_size = ftr_3_start - ftr_2_start
                frame_data_size = ftr_1_start - frame_start

                SOURCE.seek(ftr_1_start)
                ftr_1_data = SOURCE.read(ftr_1_data_size)

                SOURCE.seek(ftr_2_start)
                ftr_2_data = SOURCE.read(ftr_2_data_size)

            SOURCE.seek(frame_start)
            frame_data = SOURCE.read(frame_data_size)
            data_dict['frame_data'] = frame_data
            data_dict['ftr_1_data'] = []
            data_dict['ftr_2_data'] = []
            data_dict['ftr_ID'] = ftr_ID
            if ftr_ID == 1:
                data_dict['ftr_1_data'] = ftr_data
            elif ftr_ID == 2:
                data_dict['ftr_2_data'] = ftr_data
            elif ftr_ID == 3:
                data_dict['ftr_1_data'] = ftr_1_data
                data_dict['ftr_2_data'] = ftr_2_data
            return data_dict


    #Port.make_wp_id_list(data_dict: dict, full_wp_id_list)      return full_wp_id_list
    @staticmethod
    def make_wp_id_list(data_dict: dict, full_wp_id_list):
        print('Running wp_vis_edit ...')
        # full_wp_id_list = data_dict['full_wp_id_list']
        hidden_wp_id_list = data_dict['hidden_wp_id_list']

        ftr_2_data = list(data_dict['ftr_2_data'])
        hidden_wp_count = ftr_2_data[1]
        # total_wp_count = len(full_wp_id_list)
        for count in range(hidden_wp_count):
            addr_index = count * 2 + 9
            bone_index = ftr_2_data[addr_index] + 3
            bone_int = ftr_2_data[bone_index]
            hidden_wp_id_list.append(bone_int)
            if bone_int not in full_wp_id_list:
                full_wp_id_list.append(bone_int)
        #         print(f'hidden_wp_count: {hidden_wp_count}')
        #         print(f'bone_index: {bone_index}')
        #         print(f'bone_int: {bone_int}')
        # print(f'full_wp_id_list: {full_wp_id_list}')
        return full_wp_id_list


    # Port.wp_vis_edit(ftr_ID: int, dest_path: Path, data_dict: dict)     return: None
    @staticmethod
    def wp_vis_edit(ftr_ID: int, dest_path: Path, data_dict: dict):
        """Make adjustments to FE10 data to make sure not-in-use weapons are invisible in FE9
        - Determine all weapon bones in the skeleton and find bone ID for each one.
        - Determine which skeleton bones should be hidden weapons for each animation.
        - Add or update table, meta-, and frame data to hide un-equipped weapons

        :param ftr_ID: integer telling how many and which pointers are present at end of file
        :param dest_path: Path of output file
        :param data_dict: dictionary identifying source and modified data for each part of the
        animation file
        :return: None
        """
        print('Running wp_vis_edit ...')

        '''Load weapon lists for model'''
        wp_dict = data_dict['wp_dict']
        full_wp_count = len(wp_dict)
        _, current_wp = dest_path.stem.split('_')
        full_wp_id_list = list(wp_dict.values())
        hidden_wp_id_list = []
        for wp in wp_dict:
            if wp != f'_{current_wp.lower()}_':
                hidden_wp_id_list.append(wp_dict[wp])
        hidden_wp_count = len(hidden_wp_id_list)
        data_dict['hidden_wp_id_list'] = hidden_wp_id_list


        '''Update starting address and size of Bone Table, Metadata, and Keyframe Data'''
        table_count_src = data_dict['table_count_src']
        table_data = list(data_dict['table_data'])
        meta_data = data_dict['meta_data']

        table_count_dest_int = int.from_bytes(table_count_src, "big") + hidden_wp_count
        print(f'table_count_dest (hex): {hex(table_count_dest_int)}')

        # table_addr = data_dict['table_addr']
        table_size_int = table_count_dest_int * 16
        table_count_diff = table_count_dest_int - int.from_bytes(table_count_src, "big")
        table_size_diff = (table_count_diff) * 16

        meta_data_addr = 48 + table_size_int
        meta_data_addr = hex(meta_data_addr)
        print(f'meta_data_addr:{meta_data_addr}')
        meta_data_addr = bytes.fromhex(meta_data_addr[2:len(meta_data_addr)].zfill(8))
        meta_data_size_diff = table_count_diff * 3 * 12

        frame_data_addr = data_dict['frame_data_addr']
        frame_data_addr_int = int.from_bytes(
            frame_data_addr, "big") + table_size_diff + meta_data_size_diff
        frame_data_addr = hex(frame_data_addr_int)
        frame_data_addr = bytes.fromhex(frame_data_addr[2:len(frame_data_addr)].zfill(8))
        frame_data_size_src = len(data_dict['frame_data'])
        frame_data_size_diff = table_count_diff * 3 * 4

        '''Update header pointer and footer pointer 1 (if it exists)'''
        if ftr_ID in [1, 3]:
            ftr_data_addr_int = frame_data_addr_int + frame_data_size_src + frame_data_size_diff
            ftr_data_addr = hex(ftr_data_addr_int)
            ftr_data_addr = bytes.fromhex(ftr_data_addr[2:len(ftr_data_addr)].zfill(8))
            data_dict['hdr_ptr'] = list(ftr_data_addr)

            ftr_ptr = ftr_data_addr_int + 40
            ftr_ptr = hex(ftr_ptr)
            ftr_ptr = bytes.fromhex(ftr_ptr[2:len(ftr_ptr)].zfill(8))
            data_dict['ftr_1_ptr'] = list(ftr_ptr)
        else:
            data_dict['hdr_ptr'] = [0, 0, 0, 0]
            data_dict['ftr_ptr'] = []

        '''Generate new data'''
        table_data_add = []
        meta_entry_count = table_data[-5]
        last_meta_entry_size = table_data[-1]
        meta_entry_count = meta_entry_count + last_meta_entry_size

        meta_data_add = []
        frame_entry_count = meta_data[len(meta_data) - 2:len(meta_data)]
        frame_entry_count = int.from_bytes(frame_entry_count, "big")
        last_frame_entry_size = meta_data[len(meta_data) - 5]
        frame_entry_count = frame_entry_count + last_frame_entry_size
        meta_data_format = ['00', '00', '0F', '00', '00', '01', '00', '01', '00', '00', '04', '58',
                            '00', '01', '0F', '00', '00', '01', '00', '01', '00', '00', '04', '59',
                            '00', '02', '0F', '00', '00', '01', '00', '01', '00', '00', '04', '5A']
        meta_data_new = [int(b, 16) for b in meta_data_format]

        frame_data_add = []
        frame_first = data_dict['bytes_09_1b'][14]

        for count in range(hidden_wp_count):
            '''New Table rows'''
            table_data_add.extend([0, 0, 0, hidden_wp_id_list[count]])
            table_data_add.extend([0, 0, 0, 8])
            table_data_add.extend([0, 0, 0, meta_entry_count])
            table_data_add.extend([0, 0, 0, 3])
            meta_entry_count += 3

            '''New Metadata entries'''
            for meta_count in range(3):
                last_frame_index = 5 + meta_count*12
                meta_data_new[last_frame_index] = frame_first

                frame_entry_count_byte = frame_entry_count + meta_count + count * 3
                frame_entry_count_hex = hex(frame_entry_count_byte)
                frame_entry_count_hex = list(bytes.fromhex(frame_entry_count_hex[2:len(
                    frame_entry_count_hex)].zfill(8)))
                for byte_index, byte in enumerate(frame_entry_count_hex):
                    meta_index = 8 + meta_count * 12 + byte_index
                    meta_data_new[meta_index] = byte

            meta_data_add.extend(meta_data_new)

            '''New Keyframe data entries'''
            frame_data_add.extend([0, frame_first, 0, 0] * 3)

        '''Remove FE10 Table Rows that use hidden ID'''
        table_count_src_int = int.from_bytes(table_count_src, "big")
        table_rows = []
        for row in range(table_count_src_int):
            row_data = []
            start_index = row * 16
            for byte_count in range(16):
                # print(start_index+byte_count)
                row_data.append(table_data[start_index + byte_count])
            # print(f'row_data: {row_data}')
            table_rows.append(row_data)

        table_data = []
        minus_row_count = 0
        for row_data in table_rows:
            if row_data[3] not in full_wp_id_list:
                table_data.extend(row_data)
            else:
                minus_row_count += 1
        table_count_dest_int = table_count_dest_int - minus_row_count
        table_padding = [0] * 16 * minus_row_count

        '''Add to new data to data dictionary'''
        data_dict['table_count_dest_int'] = table_count_dest_int
        data_dict['meta_data_addr'] = meta_data_addr
        data_dict['frame_data_addr'] = frame_data_addr
        data_dict['table_data'] = table_data
        data_dict['table_data_add'] = table_data_add
        data_dict['table_padding'] = table_padding
        data_dict['meta_data_add'] = meta_data_add
        data_dict['frame_data_add'] = frame_data_add

        print(f'table_data_add: {table_data_add}')
        print(f'meta_data_add: {meta_data_add}')
        print(f'frame_data_add: {frame_data_add}')


    # Port.write_hex(ftr_ID: int, dest_path: Path, data_dict: dict)       return: None
    @staticmethod
    def write_hex(ftr_ID: int, dest_path: Path, data_dict: dict):
        ''' Write modified hex data to new file in output directory

        :param data_dict: dictionary of data read from the source file and modified,
        to be written to the dest file
        :param ftr_ID: Identify the type and amount of footer data pointers.
            - 0 for no pointers
            - 1 and 2 for only one pointer (only Pointer 1 or only Pointer 2 is present)
            - 3 for all 3 pointers
        :param dest_path: Path for the destination animation file
        :return: None
        '''
        print('Running write_hex ...')
        print(f'ftr_ID = {ftr_ID}')

        # 'address_markers', 'table_data', 'meta_data', 'frame_data', 'ftr_data'

        with open(Path(dest_path), "wb+") as DEST:
            print(f'Writing {dest_path.name}...')
            DEST.write(bytearray(data_dict['hdr_ptr']))
            DEST.write(bytearray([0, 0, 0, 0, 0]))
            DEST.write(data_dict['bytes_09_1b'])
            DEST.write(bytearray([0, 0, 0, data_dict['table_count_dest_int']]))
            DEST.write(data_dict['table_addr'])
            DEST.write(data_dict['meta_data_addr'])
            DEST.write(data_dict['bytes_28_2b'])
            DEST.write(data_dict['frame_data_addr'])
            DEST.write(bytearray(data_dict['table_data']))
            DEST.write(bytearray(data_dict['table_data_add']))  # ! final ver only
            DEST.write(bytearray(data_dict['table_padding']))
            DEST.write(data_dict['meta_data'])
            DEST.write(bytearray(data_dict['meta_data_add']))
            DEST.write(data_dict['frame_data'])
            DEST.write(bytearray(data_dict['frame_data_add']))
            if ftr_ID == 1 or ftr_ID == 3:
                DEST.write(bytearray(data_dict['ftr_1_ptr']))
                DEST.write(bytearray([0] * 36))
                DEST.write(bytearray(data_dict['ftr_1_data']))
            print(f'End of writing {dest_path.name}\n')


    # Port.count_skeleton_wp(input_pack)        return: wp_dict
    @staticmethod
    def count_skeleton_wp(input_pack):
        with (open(input_pack.joinpath('skeleton.g'), 'rb') as skeleton):
            data = skeleton.read()
            total_size = len(data)

            skeleton.seek(4)
            str_pool_ptr = skeleton.read(4)
            str_pool_ptr = int.from_bytes(str_pool_ptr, "big")
            skeleton.seek(str_pool_ptr)
            str_pool_bytes = skeleton.read(total_size - str_pool_ptr)
            str_pool_split = str_pool_bytes.split(b'\x00')
            str_pool_decode = [s.decode('utf-8') for s in str_pool_split if s]
            print(f'decoded_strings: {str_pool_decode}')

            wp_dict = {}
            for wp_str in ['_ar_', '_sw_', '_sp_', '_ja_', '_ax_', '_ha_', '_bw_', '_rd_', '_bg_']:
                if wp_str in str_pool_decode:
                    wp_dict[wp_str] = str_pool_decode.index(wp_str) - 1
            print(f'wp_dict: {wp_dict}')
        return wp_dict


    # Port.hex_edit(src_path: Path, dest_path: Path, wp_dict: dict)
    # return: None
    @staticmethod
    def hex_edit(src_path: Path, dest_path: Path, wp_dict: dict):
        print(f'Running hex_edit for {src_path.name} ...')
        print(f'\nSRC: {src_path.name}, DEST: {dest_path.name}')

        data_dict = Port.read_hex(src_path)
        data_dict['wp_dict'] = wp_dict
        ftr_ID = data_dict['ftr_ID']

        Port.wp_vis_edit(ftr_ID, dest_path, data_dict)
        Port.write_hex(ftr_ID, dest_path, data_dict)


# load_anim_data_fe10()     return: None
def load_anim_data_fe10():
    anim_data_file = resource_path('FE10-AnimData.txt')

    with open(anim_data_file, 'r') as f:
        data = f.readlines()
    for x in range(245):
        line = (x * 3)
        model = data[line][:-1]
        anim_data = data[line + 1][:-1]
        anim_data_dict[model] = anim_data

    anim_data_dict_sorted = dict(sorted(anim_data_dict.items()))
    model_list.extend(list(anim_data_dict_sorted.keys()))
    model_list.append('Select Model')
    print(model_list)

# main()    return: None
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(main_window)
    widget.setGeometry(300, 100, 560, 560)
    widget.show()
    sys.exit(app.exec())


""" MAIN  """
if __name__ == '__main__':
    main()